# MyOTA contracts

MyOTA is a programme-agnostic platform for outdoor activation programmes. MPOTA is represented as a configured programme, not as the platform itself. No rules or charter text are copied from POTA or any other programme: every programme supplies its own configuration, policy, eligibility, awards and public charter.

This repository is the API-first contract boundary for MyOTA. It owns the
versioned OpenAPI document, event envelopes, compatibility rules, and
dependency-light generated client used by the local integration slice.

## What works now

- The global contract time policy is UTC. Offset-bearing inputs normalize to
  the same UTC instant; legacy unqualified date-times mean UTC rather than
  browser/server local time. See the [UTC policy](https://github.com/myota-platform/myota-docs/blob/main/docs/utc-time-policy.md).
- Authenticated binary award artwork replacement/read resources and bounded
  transient PDF previews. Draft schemas retain manager/signature/effective-date
  fields and custom text. Both clients expose these preferred methods. See the
  [designer resource guide](https://github.com/myota-platform/myota-docs/blob/main/docs/programme-and-award-design.md).
- SeaweedFS status and paged sampled-history resources at
  `/v1/operations/object-storage` and `/v1/operations/object-storage/snapshots`,
  plus the live-identity-checked `/v1/operations/observability-session` resource
  for per-user Grafana Editor/Viewer role resolution. Clients cover all three.
- Permission-checked JetStream status and paged snapshot-history resources at
  `/v1/operations/jetstream` and `/v1/operations/jetstream/snapshots`, with
  nullable unknown measurements rather than invented zero values.
- Entity responses expose `version`; preferred entity update methods in both
  clients accept an optional version and send `If-Match`. Stale updates return
  HTTP 409, allowing users to reload before overwriting concurrent work.
- Contracts expose reusable capabilities without embedding the charter,
  eligibility, award thresholds, or rules of MPOTA, POTA, or another
  programme.

The OpenAPI document is the canonical cross-service contract. Geodata imports and manual proposals accept one or more shared `entityTypes`; the first ordered code is retained as the legacy primary `entityType`, while the relational assignment set is authoritative. Imports are programme-independent and first enter durable pre-processing; administrator promotion explicitly chooses CANDIDATE or APPROVED. Programme assignment and programme-specific eligibility remain separate concerns.

Browser file intake uses the contract's user-owned resumable upload-session
resource, bounded binary part upload, progress lookup, explicit completion, and
abort operations under `/v1/geodata/import-uploads`. See the
[uploaded-source and worker lifecycle](https://github.com/myota-platform/myota-docs/blob/main/docs/geodata-horizontal-scaling-roadmap.md)
for retry, object-storage, and JetStream execution semantics.

Phase 0 is frozen. The canonical file is `contracts/openapi.yaml`; the root
file and the platform copy are generated mirrors. Synchronize them with:

```sh
python3 scripts/sync_contract_mirrors.py \
  --platform-root ../myota-platform \
  --deploy-root ../myota-deploy
```

This also generates the compact event-routing catalog consumed by the
deployment relay and its synchronized platform copy.
Run the route and contract checks with
`python3 scripts/check_contract_phase0.py --canonical contracts/openapi.yaml --mirror openapi.yaml --mirror ../myota-platform/contracts/openapi.yaml --service-root ../myota-deploy/services --service-root ../myota-geodata-service --semantic-baseline contracts/semantic-duplicates.json --inventory-out contracts/route-inventory.json`.

The contract repository does not own runtime services or database migrations.
Deployment and service ownership are documented in the
[repository map](https://github.com/myota-platform/myota-docs/blob/main/docs/repository-map.md).

## NATS event/work contracts

Phase 1 defines the versioned event/work envelopes and registry for 68 current
facts and ten selected work commands. The generated payload schemas record
source-observed shapes and data classifications; the project team's joint
review accepts them as inventory contracts only. Producer enforcement remains
gated on per-event projections, payload-size and compatibility fixtures, and
the compatible successor for the current Geodata preprocessed payload. The
target JetStream topology is not deployed; see the [migration plan](https://github.com/myota-platform/myota-docs/blob/main/docs/operations/messaging/nats-event-migration-plan.md)
and [Phase 1 completion evidence](https://github.com/myota-platform/myota-docs/blob/main/docs/operations/messaging/evidence/phase1-completion-2026-10-10.md).

## Validate contracts and clients

```bash
python3 scripts/check_generated_clients.py
```

Run the mirror/route check above with sibling repositories checked out; CI
uses the same geodata and deployment registries. This repository has no
runtime dev server. Use `myota-deploy` with Colima for end-to-end API tests.
The [latest scaling delivery](https://github.com/myota-platform/myota-docs/blob/main/docs/geodata-horizontal-scaling-roadmap.md#latest-delivery-and-evidence--7-october-2026)
links conditional edits, upload resources and authenticated operations APIs.

See the [project charter](https://github.com/myota-platform/myota-docs/blob/main/docs/project-charter.md)
and [charter gap analysis](https://github.com/myota-platform/myota-docs/blob/main/docs/charter-gap-analysis.md)
for the policy and product boundaries that contracts must preserve.

## Architecture

The OpenAPI document is the source of truth for HTTP compatibility. The
checked-in stdlib Python client and TypeScript client façade cover the
preferred resource operations introduced in Phases 1–3. Browser clients may
supply their own authenticated request implementation, but lifecycle writes
must use these resource methods rather than deprecated action routes. CI runs
the Phase 0 mirror, route-registration, duplicate-operation, and semantic-
duplicate checks in [contract-freeze.yml](.github/workflows/contract-freeze.yml).
It also verifies preferred-operation coverage with
[`scripts/check_generated_clients.py`](scripts/check_generated_clients.py).
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

The original `ea7klk/mpota` repository remains untouched. Its planned flows are
treated as migration context; see the [migration strategy](https://github.com/myota-platform/myota-docs/blob/main/docs/migration-from-mpota.md).
