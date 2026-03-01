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
