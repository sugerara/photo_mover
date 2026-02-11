from __future__ import annotations

import shutil
from pathlib import Path
from typing import Iterable, List
import logging

logger = logging.getLogger(__name__)


DEFAULT_EXTENSIONS = {"jpg", "jpeg", "png", "heic", "mp4", "mov", "avi", "gif"}


def is_media(path: Path, extensions: Iterable[str]) -> bool:
    return path.is_file() and path.suffix.lstrip(".").lower() in extensions


def move_media(
    src: Path,
    dst: Path,
    *,
    recursive: bool = False,
    dry_run: bool = True,
    extensions: Iterable[str] | None = None,
) -> List[Path]:
    """Move media files from src into dst.

    Returns list of files that would be/was moved (destination paths).
    """
    if extensions is None:
        extensions = DEFAULT_EXTENSIONS
    else:
        extensions = {e.lower().lstrip(".") for e in extensions}

    src = Path(src)
    dst = Path(dst)
    moved: List[Path] = []

    if not src.exists():
        raise FileNotFoundError(f"Source not found: {src}")
    dst.mkdir(parents=True, exist_ok=True)

    if recursive:
        it = src.rglob("*")
    else:
        it = src.iterdir()

    for p in it:
        try:
            if is_media(p, extensions):
                rel = p.relative_to(src)
                target = dst.joinpath(rel.name)
                if dry_run:
                    logger.info("DRY RUN: move %s -> %s", p, target)
                    moved.append(target)
                else:
                    logger.info("Moving %s -> %s", p, target)
                    target_parent = target.parent
                    target_parent.mkdir(parents=True, exist_ok=True)
                    # Use shutil.move which handles cross-device moves
                    shutil.move(str(p), str(target))
                    moved.append(target)
        except Exception:
            logger.exception("Error processing %s", p)

    return moved
