from pathlib import Path
import tempfile
import shutil
from photo_mover.mover import move_media


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
