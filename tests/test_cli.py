from pathlib import Path

import pytest

from photo_mover.__main__ import main


def create_file(path: Path, content: bytes = b"x") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


def test_cli_csv_mode(tmp_path, capsys):
    """--csv フラグでCSVが標準出力に出力される"""
    src = tmp_path / "photos"
    create_file(src / "a.jpg", b"data")

    main(["--src", str(src), "--csv"])

    captured = capsys.readouterr()
    lines = captured.out.strip().split("\n")
    assert lines[0] == "filename,extension,relative_path,size_bytes"
    assert "a.jpg" in lines[1]


def test_cli_csv_mode_no_dst_required(tmp_path, capsys):
    """--csv 時に --dst は不要"""
    src = tmp_path / "photos"
    src.mkdir()

    main(["--src", str(src), "--csv"])

    captured = capsys.readouterr()
    assert "filename" in captured.out


def test_cli_csv_include_hash(tmp_path, capsys):
    """--csv-include-hash で sha256 カラムが追加される"""
    src = tmp_path / "photos"
    create_file(src / "a.jpg", b"photo data")

    main(["--src", str(src), "--csv", "--csv-include-hash"])

    captured = capsys.readouterr()
    lines = captured.out.strip().split("\n")
    assert "sha256" in lines[0]
    assert len(lines[1].split(",")) == 5


def test_cli_csv_include_hash_without_csv(tmp_path):
    """--csv なしで --csv-include-hash はエラー"""
    src = tmp_path / "photos"
    src.mkdir()

    with pytest.raises(SystemExit):
        main(["--src", str(src), "--dst", str(tmp_path / "dst"), "--csv-include-hash"])


def test_cli_csv_recursive(tmp_path, capsys):
    """--csv --recursive で再帰スキャン"""
    src = tmp_path / "photos"
    create_file(src / "a.jpg", b"1")
    create_file(src / "sub" / "b.png", b"22")

    main(["--src", str(src), "--csv", "--recursive"])

    captured = capsys.readouterr()
    lines = captured.out.strip().split("\n")
    assert len(lines) == 3  # header + 2 data rows


def test_cli_csv_with_extensions(tmp_path, capsys):
    """--csv --extensions でフィルタリング"""
    src = tmp_path / "photos"
    create_file(src / "a.jpg", b"1")
    create_file(src / "b.png", b"2")
    create_file(src / "c.gif", b"3")

    main(["--src", str(src), "--csv", "--extensions", "jpg,gif"])

    captured = capsys.readouterr()
    lines = captured.out.strip().split("\n")
    assert len(lines) == 3  # header + 2 data rows
    assert "b.png" not in captured.out
