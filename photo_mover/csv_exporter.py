from __future__ import annotations

import csv
import hashlib
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, TextIO

import sys

logger = logging.getLogger(__name__)


@dataclass
class MediaFileInfo:
    filename: str
    extension: str
    relative_path: str
    size_bytes: int
    sha256: str | None = None


def compute_sha256(path: Path, chunk_size: int = 8192) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()


def scan_media(
    src: Path,
    *,
    recursive: bool = False,
    extensions: Iterable[str] | None = None,
    include_hash: bool = False,
) -> Iterator[MediaFileInfo]:
    from .mover import DEFAULT_EXTENSIONS, is_media

    if extensions is None:
        exts = DEFAULT_EXTENSIONS
    else:
        exts = {e.lower().lstrip(".") for e in extensions}

    src = Path(src)
    if not src.exists():
        raise FileNotFoundError(f"Source not found: {src}")

    iterator = src.rglob("*") if recursive else src.iterdir()

    for p in sorted(iterator):
        if is_media(p, exts):
            rel = p.relative_to(src)
            sha = compute_sha256(p) if include_hash else None
            yield MediaFileInfo(
                filename=p.name,
                extension=p.suffix.lstrip(".").lower(),
                relative_path=str(rel),
                size_bytes=p.stat().st_size,
                sha256=sha,
            )


_CSV_COLUMNS_BASE = ["filename", "extension", "relative_path", "size_bytes"]
_CSV_COLUMNS_HASH = _CSV_COLUMNS_BASE + ["sha256"]


def write_csv(
    records: Iterable[MediaFileInfo],
    output: TextIO | None = None,
    *,
    include_hash: bool = False,
) -> None:
    if output is None:
        output = sys.stdout
    columns = _CSV_COLUMNS_HASH if include_hash else _CSV_COLUMNS_BASE
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(columns)
    for record in records:
        row = [
            record.filename,
            record.extension,
            record.relative_path,
            str(record.size_bytes),
        ]
        if include_hash:
            row.append(record.sha256 or "")
        writer.writerow(row)
