from __future__ import annotations

import argparse
from pathlib import Path
from .mover import move_media
import logging
import sys


def main(argv=None):
    parser = argparse.ArgumentParser(prog="photo_mover", description="Move photos/videos from source to destination")
    parser.add_argument("--src", required=True, help="Source directory")
    parser.add_argument("--dst", required=True, help="Destination directory")
    parser.add_argument("--recursive", action="store_true", help="Scan source recursively")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually move files; show what would happen")
    parser.add_argument("--extensions", help="Comma-separated list of extensions to include (e.g. jpg,png,mp4)")
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(message)s")

    exts = None
    if args.extensions:
        exts = [e.strip() for e in args.extensions.split(",") if e.strip()]

    try:
        moved = move_media(Path(args.src), Path(args.dst), recursive=args.recursive, dry_run=args.dry_run or True, extensions=exts)
        if args.dry_run:
            print("Dry run: files that would be moved:")
        else:
            print("Moved files:")
        for p in moved:
            print(" - ", p)
    except Exception as e:
        print("Error:", e)
        sys.exit(2)


if __name__ == "__main__":
    main()
