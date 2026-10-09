#!/usr/bin/env python3
"""Generate per-event schema wrappers from the checked-in event registry.

The registry is authoritative in this repository. Per-event payloads remain
intentionally permissive until their owning services close the recorded
payload-evidence gates; this generator does not invent payload properties.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "contracts/event-registry.json"
SCHEMA_DIR = ROOT / "contracts/schemas/events"


def event_schema(event_type: str) -> dict:
    safe = event_type.replace(".", "-")
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"https://github.com/myota-platform/myota-contracts/contracts/schemas/events/{safe}.schema.json",
        "title": f"{event_type} envelope v1",
        "allOf": [
            {"$ref": "../event-envelope.schema.json"},
            {"type": "object", "properties": {"eventType": {"const": event_type}}},
        ],
    }


def main() -> None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    events = registry["events"]
    SCHEMA_DIR.mkdir(parents=True, exist_ok=True)
    expected = set()
    for event in events:
        path = ROOT / "contracts" / event["schema"]
        expected.add(path)
        path.write_text(json.dumps(event_schema(event["eventType"]), indent=2) + "\n", encoding="utf-8")
    for stale in SCHEMA_DIR.glob("*.schema.json"):
        if stale not in expected:
            stale.unlink()
    print(f"generated {len(events)} per-event schemas from {REGISTRY}")


if __name__ == "__main__":
    main()
