# MyOTA contracts

MyOTA is a programme-agnostic platform for outdoor activation programmes. MPOTA is represented as a configured programme, not as the platform itself. No rules or charter text are copied from POTA or any other programme: every programme supplies its own configuration, policy, eligibility, awards and public charter.

This repository is the API-first contract boundary for MyOTA. It owns the
versioned OpenAPI document, event envelopes, compatibility rules, and
dependency-light generated client used by the local integration slice.

## What works now

- Contracts expose reusable capabilities without embedding the charter,
  eligibility, award thresholds, or rules of MPOTA, POTA, or another
  programme.

The OpenAPI document is the canonical cross-service contract. Geodata imports and manual proposals accept one or more shared `entityTypes`; the first ordered code is retained as the legacy primary `entityType`, while the relational assignment set is authoritative. Imports are programme-independent and first enter durable pre-processing; administrator promotion explicitly chooses CANDIDATE or APPROVED. Programme assignment and programme-specific eligibility remain separate concerns.

Phase 0 is frozen. The canonical file is `contracts/openapi.yaml`; the root
file and the platform copy are generated mirrors. Synchronize them with
`python3 scripts/sync_contract_mirrors.py --platform-root ../myota-platform`.
Run the route and contract checks with
`python3 scripts/check_contract_phase0.py --canonical contracts/openapi.yaml --mirror openapi.yaml --mirror ../myota-platform/contracts/openapi.yaml --service-root ../myota-deploy/services --semantic-baseline contracts/semantic-duplicates.json --inventory-out contracts/route-inventory.json`.

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

The OpenAPI document is the source of truth for HTTP compatibility. CI runs
the Phase 0 mirror, route-registration, duplicate-operation, and semantic-
duplicate checks in [contract-freeze.yml](.github/workflows/contract-freeze.yml).
The generated route baseline is stored in
[`contracts/route-inventory.json`](contracts/route-inventory.json).

The route cleanup is documented in the
[REST API consolidation plan](https://github.com/myota-platform/myota-docs/blob/main/docs/api-rest-consolidation-plan.md).
Phase 1 resource aliases are implemented and documented in
[api-phase1-resource-updates.md](https://github.com/myota-platform/myota-docs/blob/main/docs/api-phase1-resource-updates.md).
Phase 2 geodata resources are implemented and documented in
[api-phase2-geodata-resource-model.md](https://github.com/myota-platform/myota-docs/blob/main/docs/api-phase2-geodata-resource-model.md).
Phase 3 activity and award jobs are implemented and documented in
[api-phase3-activity-award-jobs.md](https://github.com/myota-platform/myota-docs/blob/main/docs/api-phase3-activity-award-jobs.md).
Legacy action routes remain available as deprecated aliases while clients
migrate. The root OpenAPI file and the myota-platform integration copy are
generated mirrors of `contracts/openapi.yaml`.

## Source project

The original `ea7klk/mpota` repository remains untouched. Its charter and planned flows are treated as the migration source; see [`docs/migration-from-mpota.md`](docs/migration-from-mpota.md).
