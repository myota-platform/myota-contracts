from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class EventRegistryTests(unittest.TestCase):
    def test_registry_entries_have_unique_subjects_and_checked_in_schemas(self):
        registry = json.loads(
            (ROOT / "contracts/event-registry.json").read_text(encoding="utf-8")
        )
        subjects = [item["subject"] for item in registry["events"] + registry["work"]]
        self.assertEqual(len(subjects), len(set(subjects)))
        self.assertEqual(len(registry["events"]), 68)
        self.assertEqual(len(registry["work"]), 10)
        self.assertEqual(
            {
                event_type
                for work in registry["work"]
                for event_type in work.get("sourceEventTypes", [])
            },
            {
                "geodata.import.queued.v1",
                "geodata.import.recovered.v1",
                "geodata.import.processing.queued.v1",
                "geodata.import.processing.recovered.v1",
                "geodata.entity-deletion-job.queued.v1",
                "geodata.entity.location-enrichment-requested.v1",
            },
        )
        for event in registry["events"]:
            self.assertEqual(event["subject"], f"myota.events.{event['eventType']}")
            schema_path = ROOT / "contracts" / event["schema"]
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            self.assertEqual(schema["allOf"][1]["properties"]["eventType"]["const"], event["eventType"])
            self.assertEqual(event["payloadEvidence"], "pending-owner-schema-review")
        for work in registry["work"]:
            self.assertIn(work["subject"].split(".")[2], {"activity", "geodata"})
            self.assertRegex(work["workType"], r"^[a-z][a-z0-9-]*(\.[a-z][a-z0-9-]*)+\.v1$")
            self.assertTrue(re.fullmatch(r"[a-z0-9-]+-v1", work["durable"]))

    def test_outer_event_envelope_rejects_relay_mutable_fields(self):
        schema = json.loads(
            (ROOT / "contracts/schemas/event-envelope.schema.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(schema["properties"]["envelopeVersion"]["const"], 1)
        self.assertFalse(schema["additionalProperties"])
        self.assertNotIn("attempts", schema["properties"])
        self.assertIn("causationId", schema["properties"])


if __name__ == "__main__":
    unittest.main()
