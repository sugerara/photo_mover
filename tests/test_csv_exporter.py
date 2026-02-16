import csv
import hashlib
import io
from pathlib import Path

import pytest

from photo_mover.csv_exporter import (
    MediaFileInfo,
    compute_sha256,
    scan_media,
    write_csv,
)


def create_file(path: Path, content: bytes = b"x") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


# --- Phase 1: scan_media tests ---


def test_scan_media_basic(tmp_path):
    """基本的な非再帰スキャン: 全ファイルを返す"""
    src = tmp_path / "photos"
    src.mkdir()
    create_file(src / "a.jpg", b"hello")
    create_file(src / "b.png", b"world!")
    create_file(src / "readme.txt", b"not media")

    results = list(scan_media(src))

    assert len(results) == 3
    filenames = {r.filename for r in results}
    assert filenames == {"a.jpg", "b.png", "readme.txt"}


def test_scan_media_fields(tmp_path):
    """各フィールドの値が正しいこと"""
    src = tmp_path / "photos"
    src.mkdir()
    content = b"test content 12345"
    create_file(src / "photo.jpg", content)

    results = list(scan_media(src))

    assert len(results) == 1
    info = results[0]
    assert info.filename == "photo.jpg"
    assert info.extension == "jpg"
    assert info.relative_path == "photo.jpg"
    assert info.size_bytes == len(content)
    assert info.sha256 is None


def test_scan_media_recursive(tmp_path):
    """再帰スキャンでサブディレクトリ内のファイルも返す"""
    src = tmp_path / "photos"
    create_file(src / "a.jpg")
    create_file(src / "sub" / "b.png")
    create_file(src / "sub" / "deep" / "c.mp4")

    results = list(scan_media(src, recursive=True))

    assert len(results) == 3
    relative_paths = {r.relative_path for r in results}
    assert "a.jpg" in relative_paths
    assert str(Path("sub") / "b.png") in relative_paths
    assert str(Path("sub") / "deep" / "c.mp4") in relative_paths


def test_scan_media_non_recursive_ignores_subdirs(tmp_path):
    """非再帰ではサブディレクトリ内のファイルを返さない"""
    src = tmp_path / "photos"
    create_file(src / "a.jpg")
    create_file(src / "sub" / "b.png")

    results = list(scan_media(src, recursive=False))

    assert len(results) == 1
    assert results[0].filename == "a.jpg"


def test_scan_media_all_files_when_no_extensions(tmp_path):
    """--extensions 未指定時は画像以外も含む全ファイルを返す"""
    src = tmp_path / "files"
    src.mkdir()
    create_file(src / "a.jpg", b"photo")
    create_file(src / "readme.txt", b"text")
    create_file(src / "data.csv", b"csv")
    create_file(src / "script.py", b"code")

    results = list(scan_media(src))

    assert len(results) == 4
    filenames = {r.filename for r in results}
    assert filenames == {"a.jpg", "readme.txt", "data.csv", "script.py"}


def test_scan_media_custom_extensions(tmp_path):
    """カスタム拡張子でフィルタリングできる"""
    src = tmp_path / "photos"
    create_file(src / "a.jpg")
    create_file(src / "b.png")
    create_file(src / "c.gif")

    results = list(scan_media(src, extensions=["jpg", "gif"]))

    assert len(results) == 2
    filenames = {r.filename for r in results}
    assert filenames == {"a.jpg", "c.gif"}


def test_scan_media_empty_directory(tmp_path):
    """空ディレクトリでは空リストを返す"""
    src = tmp_path / "empty"
    src.mkdir()

    results = list(scan_media(src))

    assert results == []


def test_scan_media_nonexistent_source(tmp_path):
    """存在しないソースディレクトリでFileNotFoundErrorを送出"""
    with pytest.raises(FileNotFoundError):
        list(scan_media(tmp_path / "no_such_dir"))


def test_scan_media_relative_path_from_src(tmp_path):
    """ネストしたディレクトリの相対パスがsrcからの相対になっている"""
    src = tmp_path / "base"
    create_file(src / "2024" / "jan" / "photo.heic")

    results = list(scan_media(src, recursive=True))

    assert len(results) == 1
    expected = str(Path("2024") / "jan" / "photo.heic")
    assert results[0].relative_path == expected


def test_scan_media_utf8_filename(tmp_path):
    """日本語ファイル名を正しく扱える"""
    src = tmp_path / "photos"
    create_file(src / "写真.jpg")
    create_file(src / "動画.mp4")

    results = list(scan_media(src))

    assert len(results) == 2
    filenames = {r.filename for r in results}
    assert "写真.jpg" in filenames
    assert "動画.mp4" in filenames


# --- Phase 2: SHA256 tests ---


def test_compute_sha256(tmp_path):
    """基本的なSHA256ハッシュ計算"""
    f = tmp_path / "test.bin"
    content = b"Hello, World!"
    f.write_bytes(content)

    expected = hashlib.sha256(content).hexdigest()
    assert compute_sha256(f) == expected


def test_compute_sha256_large_file(tmp_path):
    """チャンク読みで大きなファイルも正しくハッシュ計算"""
    f = tmp_path / "big.bin"
    content = b"A" * 100_000
    f.write_bytes(content)

    expected = hashlib.sha256(content).hexdigest()
    assert compute_sha256(f) == expected


def test_scan_media_with_hash(tmp_path):
    """include_hash=Trueでsha256が計算される"""
    src = tmp_path / "photos"
    content = b"photo data here"
    create_file(src / "a.jpg", content)

    results = list(scan_media(src, include_hash=True))

    assert len(results) == 1
    expected_hash = hashlib.sha256(content).hexdigest()
    assert results[0].sha256 == expected_hash


def test_scan_media_without_hash(tmp_path):
    """デフォルト(include_hash=False)ではsha256はNone"""
    src = tmp_path / "photos"
    create_file(src / "a.jpg", b"data")

    results = list(scan_media(src, include_hash=False))

    assert len(results) == 1
    assert results[0].sha256 is None


# --- Phase 3: write_csv tests ---


def test_write_csv_header_and_rows():
    """ヘッダ行とデータ行が正しく出力される"""
    records = [
        MediaFileInfo("a.jpg", "jpg", "a.jpg", 100),
        MediaFileInfo("b.png", "png", "sub/b.png", 200),
    ]
    output = io.StringIO()

    write_csv(records, output)

    output.seek(0)
    reader = csv.reader(output)
    rows = list(reader)

    assert rows[0] == ["filename", "extension", "relative_path", "size_bytes"]
    assert rows[1] == ["a.jpg", "jpg", "a.jpg", "100"]
    assert rows[2] == ["b.png", "png", "sub/b.png", "200"]
    assert len(rows) == 3


def test_write_csv_with_hash():
    """include_hash=Trueでsha256カラムが含まれる"""
    records = [
        MediaFileInfo("a.jpg", "jpg", "a.jpg", 100, sha256="abc123def456"),
    ]
    output = io.StringIO()

    write_csv(records, output, include_hash=True)

    output.seek(0)
    reader = csv.reader(output)
    rows = list(reader)

    assert rows[0] == ["filename", "extension", "relative_path", "size_bytes", "sha256"]
    assert rows[1] == ["a.jpg", "jpg", "a.jpg", "100", "abc123def456"]


def test_write_csv_without_hash():
    """include_hash=Falseではsha256カラムなし"""
    records = [
        MediaFileInfo("a.jpg", "jpg", "a.jpg", 100, sha256=None),
    ]
    output = io.StringIO()

    write_csv(records, output, include_hash=False)

    output.seek(0)
    reader = csv.reader(output)
    rows = list(reader)

    assert rows[0] == ["filename", "extension", "relative_path", "size_bytes"]
    assert len(rows[1]) == 4


def test_write_csv_empty_records():
    """空レコードでもヘッダのみ出力される"""
    output = io.StringIO()

    write_csv([], output)

    output.seek(0)
    reader = csv.reader(output)
    rows = list(reader)

    assert len(rows) == 1
    assert rows[0] == ["filename", "extension", "relative_path", "size_bytes"]


def test_write_csv_utf8():
    """日本語ファイル名がCSVに正しく出力される"""
    records = [
        MediaFileInfo("写真.jpg", "jpg", "写真.jpg", 50),
    ]
    output = io.StringIO()

    write_csv(records, output)

    output.seek(0)
    content = output.read()
    assert "写真.jpg" in content


def test_write_csv_lf_line_endings():
    """改行コードがLFであること(CRLFでない)"""
    records = [
        MediaFileInfo("a.jpg", "jpg", "a.jpg", 100),
    ]
    output = io.StringIO()

    write_csv(records, output)

    raw = output.getvalue()
    assert "\r\n" not in raw
    assert "\n" in raw


# --- Phase 4: End-to-End tests ---


def test_csv_end_to_end(tmp_path):
    """scan_media → write_csv の結合テスト"""
    src = tmp_path / "photos"
    create_file(src / "a.jpg", b"photo1")
    create_file(src / "sub" / "b.mp4", b"video")
    create_file(src / "readme.txt", b"not media")

    records = list(scan_media(src, recursive=True))
    output = io.StringIO()
    write_csv(records, output)

    output.seek(0)
    reader = csv.DictReader(output)
    rows = list(reader)

    assert len(rows) == 3
    filenames = {r["filename"] for r in rows}
    assert filenames == {"a.jpg", "b.mp4", "readme.txt"}
    for row in rows:
        if row["filename"] == "a.jpg":
            assert row["size_bytes"] == "6"  # len(b"photo1")
        elif row["filename"] == "b.mp4":
            assert row["size_bytes"] == "5"  # len(b"video")
        elif row["filename"] == "readme.txt":
            assert row["size_bytes"] == "9"  # len(b"not media")


def test_csv_end_to_end_with_hash(tmp_path):
    """ハッシュ付きの結合テスト"""
    src = tmp_path / "photos"
    content = b"known content"
    create_file(src / "a.jpg", content)

    records = list(scan_media(src, include_hash=True))
    output = io.StringIO()
    write_csv(records, output, include_hash=True)

    output.seek(0)
    reader = csv.DictReader(output)
    rows = list(reader)

    assert len(rows) == 1
    assert rows[0]["sha256"] == hashlib.sha256(content).hexdigest()
