#!/usr/bin/env python3
"""Fail when source-owned runtime modules drift from Deploy or Platform mirrors."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    root = (
        Path(sys.argv[1]).resolve()
        if len(sys.argv) > 1
        else Path("..").resolve()
    )
    manifest = (
        Path(__file__).resolve().parents[1]
        / "contracts"
        / "runtime-mirror-map.json"
    )
    data = json.loads(manifest.read_text(encoding="utf-8"))
    errors: list[str] = []
    for entry in data["entries"]:
        source = root / entry["owner"] / entry["path"]
        if not source.is_file():
            errors.append(
                f"missing owner source: {entry['owner']}/{entry['path']}"
            )
            continue
        for mirror in entry["mirrors"]:
            target = root / mirror
            if not target.is_file():
                errors.append(
                    f"missing mirror: {mirror} (from {entry['owner']}/{entry['path']})"
                )
            elif target.read_bytes() != source.read_bytes():
                errors.append(
                    f"drift: {mirror} differs from {entry['owner']}/{entry['path']}"
                )
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(
        f"runtime mirror audit passed: {len(data['entries'])} owner paths, "
        f"{sum(len(e['mirrors']) for e in data['entries'])} mirrors"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
