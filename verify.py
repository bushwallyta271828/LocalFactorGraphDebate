#!/usr/bin/env python3
"""Verify the publication manifest without importing plotting dependencies."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    manifest = json.loads((ROOT/'MANIFEST.json').read_text())
    for relative, expected in manifest['files'].items():
        path = ROOT/relative
        if path.is_symlink() or not path.is_file():
            raise SystemExit(f'Missing or linked release file: {relative}')
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise SystemExit(f'Changed release file: {relative}')
    print(f"Verified {len(manifest['files'])} release files")


if __name__ == '__main__':
    main()
