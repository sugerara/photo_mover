from __future__ import annotations

import argparse
from pathlib import Path
from .mover import move_media
import logging
import sys


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="photo_mover", description="Move photos/videos from source to destination"
    )
    parser.add_argument("--src", required=True, help="Source directory")
    parser.add_argument("--dst", help="Destination directory")
    parser.add_argument(
        "--recursive", action="store_true", help="Scan source recursively"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't actually move files; show what would happen",
    )
    parser.add_argument(
        "--extensions",
        help="Comma-separated list of extensions to include (e.g. jpg,png,mp4)",
    )
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument(
        "--csv",
        action="store_true",
        help="Output file listing as CSV to stdout (does not move files)",
    )
    parser.add_argument(
        "--csv-include-hash",
        action="store_true",
        help="Include SHA256 hash column in CSV output (requires --csv)",
    )

    args = parser.parse_args(argv)

    if args.csv_include_hash and not args.csv:
        parser.error("--csv-include-hash requires --csv")
    if not args.csv and not args.dst:
        parser.error("--dst is required when not using --csv mode")

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO, format="%(message)s"
    )

    exts = None
    if args.extensions:
        exts = [e.strip() for e in args.extensions.split(",") if e.strip()]

    try:
        if args.csv:
            from .csv_exporter import scan_media, write_csv

            records = scan_media(
                Path(args.src),
                recursive=args.recursive,
                extensions=exts,
                include_hash=args.csv_include_hash,
            )
            write_csv(records, include_hash=args.csv_include_hash)
        else:
            moved = move_media(
                Path(args.src),
                Path(args.dst),
                recursive=args.recursive,
                dry_run=args.dry_run or True,
                extensions=exts,
            )
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
