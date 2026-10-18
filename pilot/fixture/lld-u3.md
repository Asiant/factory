---
id: LLD-U3
mission: MISSION-003
version: 1
status: signed
template: {id: lld, version: 1, hash: sha256:fixture-lld-tpl}
links: {derives_from: [U3], covers: [], decided_by: [ADR-014]}
owner: {role: engineering-lead, person: Asiant}
summary_s0: "LLD-U3@v1: POST /orders (Idempotency-Key), dedup store schema, sequences."
---
# LLD-U3@v1 — Low-level design for U3

## Purpose
Contracts, schemas and sequences for idempotent submission, detailed enough
to derive contract tests (G6).

## Summary (S1)
One API operation (API-OP-09 POST /orders with Idempotency-Key), dedup store
table with 24h TTL, submit/retry sequence with 409 on key-payload mismatch,
and the test plan whose cases verify U3's acceptance criteria.

## Scope & Non-scope
U3 only. Non-goals: notification internals.

## APIs/contracts
### API-OP-09 — POST /orders (Idempotency-Key)
statement: Submit an order; Idempotency-Key header required; retry-safe.
implements: [C-3]
decided_by: [ADR-014]
contract: 201 created | 200 replay-with-original-order-id | 409 key/payload mismatch

## Schemas
idempotency_keys(key PK, order_id, payload_hash, created_at, expires_at)

## Sequences
submit → dedup lookup → miss: create order + key row · hit + hash match: return
original order id · hit + hash mismatch: 409.

## Error handling
Dedup store unavailable → 503 fail-fast (never duplicate-create); TTL expiry
sweeper is a background job.

## Low-level ADR refs
(decided_by ADR-014 as declared above; no new low-level ADRs.)

## Test plan
(derived cases live in TESTS-001 — TEST-220/TEST-221.)

## Decisions & Rationale
(decided_by ADR-014.)

## Open Questions
(none.)

## Risks & Assumptions
(none.)

## Verification
AI-check at G6: lld_hld_conformance, contract_tests_derivable.

## Change Log
| version | date | author | reason |
|---|---|---|---|
| 1 | 2026-10-18 | human:Asiant | fixture authored |
