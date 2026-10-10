# Contract generation and compatibility

The repository's `openapi.yaml` is the versioned source of truth for HTTP contracts. The checked-
in `python/myota_client.py` is a dependency-light client for local integration;
production SDKs should be regenerated in CI with the pinned OpenAPI Generator
version selected by the consuming repository.

The repository-root `openapi.yaml` and `myota-platform/contracts/openapi.yaml`
files are generated mirrors. Do not edit them directly; run
`python3 scripts/sync_contract_mirrors.py --platform-root ../myota-platform`

The event registry and JSON Schemas in `event-registry.json` and `schemas/`
are authoritative here. The mirror sync copies them to `myota-platform` along
with `events.md`. Each fact records its producer source files relative to the
owning repository. The 19 Identity and 12 Programme fact payloads have
source-derived schemas from `myota-identity-service/identity.py` and
`myota-programme-service/programmes.py`; these schemas allow additive fields
and record data classification. They still require joint owner review before
they can gate a producer. Other payloads marked
`pending-source-payload-review` remain open. Run
`python3 scripts/audit_workspace_event_sources.py --workspace-root ..` from a
full workspace to verify source references and ensure Python event-like source
literals have a fact or legacy-work disposition.

Geodata payloads use the shared Master data category catalogue: `entityTypes` is
an ordered, non-empty list, `entityTypeCodes` is a compatibility alias, and
singular `entityType` is deprecated. The first category remains the compatibility
primary; all category assignments are authoritative in the geodata service
relation. Imports do not require a programme and first produce pre-processed
records; administrator promotion explicitly produces CANDIDATE or APPROVED
entities.

Compatibility rules:

- Additive request/response fields are compatible within `/v1`.
- Removing or changing a field requires `/v2` or an explicit deprecation window
  with `Deprecation` and `Sunset` response headers.
- Event names carry their schema version (`*.v1`); consumers reject unknown
  major versions and may accept additive fields.
- Every mutating request supports `Idempotency-Key`; every response carries
  request/correlation IDs.

CI should run an OpenAPI linter, server/client generation, and a breaking-change
diff against the last released contract before publishing a service image.

The proposed REST resource consolidation and compatibility migration is
documented in the
[myota-docs REST API consolidation plan](https://github.com/myota-platform/myota-docs/blob/main/docs/api-rest-consolidation-plan.md).
This file remains contract guidance only; no route changes have been made.
