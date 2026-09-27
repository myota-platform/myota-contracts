# MyOTA event contract

Services publish durable, versioned events to an outbox owned by the emitting service. The initial implementation records the event envelope in memory; production deployment connects the outbox to a broker such as NATS JetStream or RabbitMQ without changing the HTTP contracts.

```json
{
  "eventId": "uuid",
  "eventType": "geodata.entity.reviewed.v1",
  "occurredAt": "2026-01-01T00:00:00Z",
  "producer": "geodata-service",
  "aggregate": { "type": "entity", "id": "uuid" },
  "correlationId": "uuid",
  "payload": {}
}
```

Important events include `identity.account.created.v1`, `identity.callsign.verified.v1`, `programme.created.v1`, `geodata.import.accepted.v1`, `geodata.entity.candidate.created.v1`, `geodata.entity.reviewed.v1`, `activity.activation.created.v1`, `activity.qso.recorded.v1`, `awards.definition.saved.v1`, `awards.definition.published.v1`, `awards.request.created.v1`, `awards.issued.v1`, and `awards.rendered.v1`.

`CANDIDATE` is the single pre-review lifecycle state. A candidate records its
origin in `candidateSource.type`: `ADAPTER_IMPORT` identifies an adapter and
import run, while `COMMUNITY_PROPOSAL` identifies a proposal and proposer.
The former `geodata.entity.proposed.v1` event and `PROPOSED` status are retired;
consumers should handle `geodata.entity.candidate.created.v1` and the review
event instead.

Award definitions, requests, and issuance records are owned by the activity service. They are exposed under the same port and bounded API as activation/QSO execution (`8004` locally), while binary backgrounds, signatures, and generated certificates are addressed through the configured S3-compatible object store.
