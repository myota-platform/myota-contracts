#!/usr/bin/env python3
"""Synchronize the checked-in OpenAPI mirrors from the canonical document."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--platform-root", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    canonical = root / "contracts" / "openapi.yaml"
    for mirror in (
        root / "openapi.yaml",
        args.platform_root / "contracts" / "openapi.yaml",
    ):
        mirror.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(canonical, mirror)
        print(f"synced {mirror}")
    source_contracts = root / "contracts"
    mirror_contracts = args.platform_root / "contracts"
    for relative in (
        Path("events.md"),
        Path("event-registry.json"),
        Path("schemas"),
    ):
        source = source_contracts / relative
        mirror = mirror_contracts / relative
        if source.is_dir():
            if mirror.exists():
                shutil.rmtree(mirror)
            shutil.copytree(source, mirror)
        else:
            mirror.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, mirror)
        print(f"synced {mirror}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
