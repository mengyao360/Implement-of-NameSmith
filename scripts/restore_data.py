#!/usr/bin/env python3
"""Restore the original JSONL splits from verified gzip archive parts."""

import argparse
import gzip
import hashlib
import json
import shutil
import tempfile
from pathlib import Path


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def restore_split(archive_dir, output_dir, name, entry, force):
    output = output_dir / entry["output"]
    for part in entry["parts"]:
        path = archive_dir / part["file"]
        if path.stat().st_size != part["bytes"] or sha256_file(path) != part["sha256"]:
            raise ValueError(f"Archive part failed verification: {path}")

    if output.exists():
        if output.stat().st_size == entry["bytes"] and sha256_file(output) == entry["sha256"]:
            print(f"{name}: already restored; all archive parts and JSONL checksum verified.")
            return
        if not force:
            raise FileExistsError(f"{output} differs from the dataset; use --force to replace it.")

    # Keep the final destination untouched until decompression and checks pass.
    with tempfile.TemporaryDirectory(prefix="namesmith-", dir=output_dir) as temporary:
        temporary = Path(temporary)
        compressed = temporary / "split.jsonl.gz"
        with compressed.open("wb") as destination:
            for part in entry["parts"]:
                with (archive_dir / part["file"]).open("rb") as source:
                    shutil.copyfileobj(source, destination)

        restored = temporary / "split.jsonl"
        digest = hashlib.sha256()
        size = records = 0
        with gzip.open(compressed, "rb") as source, restored.open("wb") as destination:
            for block in iter(lambda: source.read(4 * 1024 * 1024), b""):
                destination.write(block)
                digest.update(block)
                size += len(block)
                records += block.count(b"\n")
        if (size, records, digest.hexdigest()) != (entry["bytes"], entry["records"], entry["sha256"]):
            raise ValueError(f"Restored {name} split failed verification.")
        restored.replace(output)
    print(f"{name}: restored {records:,} records to {output}")


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--splits", nargs="+", choices=["train", "val", "test"], default=["train", "val", "test"])
    parser.add_argument("--output-dir", type=Path, default=root / "data")
    parser.add_argument("--force", action="store_true", help="Replace an existing JSONL file with a different checksum.")
    args = parser.parse_args()
    archive_dir = root / "data" / "archives"
    manifest = json.loads((archive_dir / "manifest.json").read_text())
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name in args.splits:
        restore_split(archive_dir, args.output_dir, name, manifest["splits"][name], args.force)


if __name__ == "__main__":
    main()
