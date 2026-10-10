from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OWNER_REPOSITORIES = {
    "identity-service": "myota-identity-service",
    "programme-service": "myota-programme-service",
    "activity-service": "myota-activity-service",
    "geodata-service": "myota-geodata-service",
    "operations-service": "myota-operations-service",
}


class EventRegistryTests(unittest.TestCase):
    def test_registry_entries_have_unique_subjects_and_checked_in_schemas(
        self,
    ):
        registry = json.loads(
            (ROOT / "contracts/event-registry.json").read_text(
                encoding="utf-8"
            )
        )
        subjects = [
            item["subject"] for item in registry["events"] + registry["work"]
        ]
        self.assertEqual(len(subjects), len(set(subjects)))
        self.assertEqual(len(registry["events"]), 68)
        identity_events = [
            event
            for event in registry["events"]
            if event["owner"] == "identity-service"
        ]
        self.assertEqual(len(identity_events), 19)
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
            self.assertEqual(
                event["subject"], f"myota.events.{event['eventType']}"
            )
            sources = event["producerSources"]
            self.assertTrue(sources)
            self.assertEqual(sources, sorted(set(sources)))
            for source in sources:
                repository, relative_path = source.split("/", 1)
                self.assertEqual(
                    repository, OWNER_REPOSITORIES[event["owner"]]
                )
                self.assertTrue(relative_path.endswith(".py"))
            schema_path = ROOT / "contracts" / event["schema"]
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            self.assertEqual(
                schema["allOf"][1]["properties"]["eventType"]["const"],
                event["eventType"],
            )
            if event["owner"] == "identity-service":
                self.assertEqual(
                    event["payloadEvidence"],
                    "source-derived-identity-callsite",
                )
                self.assertEqual(
                    schema["x-payload-evidence"], event["payloadEvidence"]
                )
                self.assertEqual(
                    schema["x-data-classification"],
                    event["dataClassification"],
                )
                self.assertIn(
                    event["dataClassification"],
                    {
                        "personal",
                        "personal-and-security",
                        "internal-configuration",
                        "internal-authorization",
                        "security-sensitive",
                    },
                )
                payload = schema["allOf"][1]["properties"]["payload"]
                self.assertEqual(payload["type"], "object")
                self.assertTrue(payload["additionalProperties"])
                self.assertTrue(payload["required"])
                if event["eventType"] == "identity.service-token.issued.v1":
                    self.assertEqual(
                        set(payload["properties"]), {"service", "scopes"}
                    )
                    self.assertNotIn("accessToken", payload["properties"])
                if event["eventType"] == "identity.login.failed.v1":
                    self.assertEqual(
                        event["dataClassification"],
                        "personal-and-security",
                    )
                    self.assertEqual(
                        set(payload["properties"]), {"email", "remoteAddr"}
                    )
            else:
                self.assertEqual(
                    event["payloadEvidence"], "pending-source-payload-review"
                )
        for work in registry["work"]:
            self.assertIn(
                work["subject"].split(".")[2], {"activity", "geodata"}
            )
            self.assertRegex(
                work["workType"], r"^[a-z][a-z0-9-]*(\.[a-z][a-z0-9-]*)+\.v1$"
            )
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
