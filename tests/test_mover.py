from pathlib import Path
import tempfile
import shutil
from photo_mover.mover import move_media
from photo_mover.__main__ import main


def touch(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"x")


def test_move_non_recursive(tmp_path):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    (src).mkdir()
    a = src / "a.jpg"
    b = src / "b.mp4"
    touch(a)
    touch(b)

    moved = move_media(src, dst, recursive=False, dry_run=False)
    assert len(moved) == 2
    assert (dst / "a.jpg").exists()


def test_dry_run(tmp_path):
    src = tmp_path / "src2"
    dst = tmp_path / "dst2"
    src.mkdir()
    f = src / "f.png"
    touch(f)

    moved = move_media(src, dst, recursive=False, dry_run=True)
    assert len(moved) == 1
    assert not (dst / "f.png").exists()


def test_cli_move_without_dry_run(tmp_path):
    """--dry-run を指定しない場合、ファイルが実際に移動されること"""
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    touch(src / "photo.jpg")

    main(["--src", str(src), "--dst", str(dst)])

    assert (dst / "photo.jpg").exists()
    assert not (src / "photo.jpg").exists()


def test_cli_dry_run(tmp_path):
    """--dry-run 指定時、ファイルが移動されないこと"""
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    touch(src / "photo.jpg")

    main(["--src", str(src), "--dst", str(dst), "--dry-run"])

    assert not (dst / "photo.jpg").exists()
    assert (src / "photo.jpg").exists()


def test_duplicate_rename_basic(tmp_path):
    """dst に同名ファイルが既存 → photo_1.jpg にリネームされる"""
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    dst.mkdir()
    touch(src / "photo.jpg")
    touch(dst / "photo.jpg")

    moved = move_media(src, dst, recursive=False, dry_run=False)

    assert len(moved) == 1
    assert moved[0] == dst / "photo_1.jpg"
    assert (dst / "photo_1.jpg").exists()
    assert (dst / "photo.jpg").exists()


def test_duplicate_rename_multiple(tmp_path):
    """dst に photo.jpg と photo_1.jpg が既存 → photo_2.jpg になる"""
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    dst.mkdir()
    touch(src / "photo.jpg")
    touch(dst / "photo.jpg")
    touch(dst / "photo_1.jpg")

    moved = move_media(src, dst, recursive=False, dry_run=False)

    assert len(moved) == 1
    assert moved[0] == dst / "photo_2.jpg"
    assert (dst / "photo_2.jpg").exists()


def test_duplicate_rename_dry_run(tmp_path):
    """dry-run でもリネーム後のパスを返す"""
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    dst.mkdir()
    touch(src / "photo.jpg")
    touch(dst / "photo.jpg")

    moved = move_media(src, dst, recursive=False, dry_run=True)

    assert len(moved) == 1
    assert moved[0] == dst / "photo_1.jpg"


def test_duplicate_no_overwrite(tmp_path):
    """既存ファイルの内容が上書きされない"""
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    dst.mkdir()
    (src / "photo.jpg").write_bytes(b"new_file")
    (dst / "photo.jpg").write_bytes(b"original")

    move_media(src, dst, recursive=False, dry_run=False)

    assert (dst / "photo.jpg").read_bytes() == b"original"
    assert (dst / "photo_1.jpg").read_bytes() == b"new_file"


def test_duplicate_rename_returns_renamed_path(tmp_path):
    """戻り値が正しいリネーム後パスで、そのファイルが存在する"""
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    dst.mkdir()
    touch(src / "photo.jpg")
    touch(dst / "photo.jpg")
    touch(dst / "photo_1.jpg")

    moved = move_media(src, dst, recursive=False, dry_run=False)

    assert len(moved) == 1
    assert moved[0] == dst / "photo_2.jpg"
    assert (dst / "photo_2.jpg").exists()
