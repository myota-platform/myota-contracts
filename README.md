# MyOTA contracts

MyOTA is a programme-agnostic platform for outdoor activation programmes. MPOTA is represented as a configured programme, not as the platform itself. No rules or charter text are copied from POTA or any other programme: every programme supplies its own configuration, policy, eligibility, awards and public charter.

This repository is the API-first contract boundary for MyOTA. It owns the
versioned OpenAPI document, event envelopes, compatibility rules, and
dependency-light generated client used by the local integration slice.

## What works now

- Contracts expose reusable capabilities without embedding the charter,
  eligibility, award thresholds, or rules of MPOTA, POTA, or another
  programme.

The OpenAPI document is the canonical cross-service contract. Geodata imports and manual proposals accept one or more shared `entityTypes`; the first ordered code is retained as the legacy primary `entityType`, while the relational assignment set is authoritative. Imports are programme-independent and always create candidate entities. Programme assignment and programme-specific eligibility remain separate concerns.

The contract repository does not own runtime services or database migrations.
Deployment and service ownership are documented in the
[repository map](https://github.com/myota-platform/myota-docs/blob/main/docs/repository-map.md).

## Run the vertical slice

```bash
python3 -m unittest discover -s tests -v
python3 services/dev_server.py
```

Contract-focused tests run without the full service stack. Use myota-deploy
with Colima for an end-to-end API test.

See the [project charter](https://github.com/myota-platform/myota-docs/blob/main/docs/project-charter.md)
and [charter gap analysis](https://github.com/myota-platform/myota-docs/blob/main/docs/charter-gap-analysis.md)
for the policy and product boundaries that contracts must preserve.

## Architecture

The OpenAPI document is the source of truth for HTTP compatibility. CI should
run an OpenAPI linter, client generation, and a breaking-change comparison
against the last released contract.

The proposed route cleanup is documented in the
[REST API consolidation plan](https://github.com/myota-platform/myota-docs/blob/main/docs/api-rest-consolidation-plan.md).
No endpoint changes have been implemented yet. The plan also identifies the
duplicate root OpenAPI file and the myota-platform integration copy that need
to become generated or CI-checked mirrors.

## Source project

The original `ea7klk/mpota` repository remains untouched. Its charter and planned flows are treated as the migration source; see [`docs/migration-from-mpota.md`](docs/migration-from-mpota.md).
