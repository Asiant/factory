---
id: FS-NFS
mission: MISSION-003
version: 3
status: signed
template: {id: fs-nfs, version: 1, hash: sha256:fixture-fs-nfs-tpl}
links: {derives_from: [MISSION-003], covers: [], decided_by: []}
owner: {role: product-owner, person: Asiant}
summary_s0: "FS-014..FS-022 + NFS-007/011/013: idempotent submission, partial fulfilment, status, notifications."
---
# FS-NFS@v3 — Functional and non-functional requirements

## Purpose
The signed requirement set the HLD must cover 100%: eight functional items and
three quantified non-functional targets.

## Summary (S1)
Eight FS items: idempotent order submission on retry, partial fulfilment
allowed, buyer-visible status timeline, remainder cancellation, later
shipments, per-line tracking, and submission notifications that do not
duplicate. Three NFS: p95 checkout latency under 800 ms at 2k rps,
99.9% submission API availability, 90-day auditable order events.

## Scope & Non-scope
Covers the order/fulfilment/notify surface of MISSION-003. Non-goals as in the
mission scope; pricing and payment auth are out.

## §2 Ordering
### FS-014 — Orders idempotent on retry
statement: Retrying an order submission with the same Idempotency-Key creates at most one order.
acceptance_test: Given a submitted order, when the same payload and Idempotency-Key are resubmitted within 24h, then exactly one order exists and the response returns the original order id.
priority: must
source: checkout-team

### FS-015 — Partial fulfilment allowed
statement: An order may be fulfilled across multiple shipments at line granularity.
acceptance_test: Given an order with 3 lines, when only 2 lines ship, then the order state is partially-fulfilled with the remainder open.
priority: must
source: seller-ops

## §3 Order lifecycle
### FS-016 — Order status timeline visible to buyer
statement: The buyer sees a per-order status timeline including partial fulfilment states.
acceptance_test: Given a partially fulfilled order, when the buyer opens the order, then the timeline shows submitted, partially-fulfilled and per-line shipment states.
priority: must
source: checkout-team

### FS-020 — Retry returns original order id
statement: A retried submission returns the order id created by the first accepted submission.
acceptance_test: Given a first submission created order O, when the same Idempotency-Key is retried, then the response body carries O's id.
priority: must
source: checkout-team

### FS-021 — Confirmation on first accepted submission
statement: A confirmation notification is sent when a submission is first accepted.
acceptance_test: Given a first submission, when it is accepted, then exactly one confirmation notification is queued.
priority: should
source: marketing

### FS-022 — Retry does not duplicate notifications
statement: A retried submission does not queue another confirmation.
acceptance_test: Given a confirmed order, when the same submission is retried, then zero new notifications are queued.
priority: must
source: marketing

## §5 Fulfilment
### FS-017 — Buyer can cancel unfulfilled remainder
statement: The buyer can cancel the unfulfilled remainder of a partially fulfilled order.
acceptance_test: Given a partially fulfilled order, when the buyer cancels the remainder, then open lines are cancelled and shipped lines are untouched.
priority: must
source: seller-ops

### FS-018 — Seller can ship remaining lines later
statement: Remaining lines may ship in later shipments without re-ordering.
acceptance_test: Given a partially fulfilled order, when the seller ships the remainder, then the order reaches fulfilled with all lines accounted.
priority: must
source: seller-ops

### FS-019 — Per-line shipment tracking
statement: Each shipment carries tracking state at line granularity.
acceptance_test: Given a multi-shipment order, when any shipment updates, then per-line tracking reflects the change.
priority: should
source: seller-ops

## §4 Performance
### NFS-007 — Checkout latency
category: performance
quantified_target: p95 checkout < 800ms @ 2k rps
verification_method: load test at G5-approved command

## §6 Reliability
### NFS-011 — Submission availability
category: operability
quantified_target: submission API 99.9% monthly availability
verification_method: SLO error-budget report from release telemetry

## §7 Auditability
### NFS-013 — Order events auditable
category: compliance
quantified_target: order events retained and auditable for 90 days
verification_method: audit-log query evidence attached at G7

## Glossary refs
Idempotency-Key: client-supplied request header, unique per intended submission. Partial fulfilment: at least one line shipped while others remain open.

## Decisions & Rationale
KDD-002 decides the partial-fulfilment policy; ADR-014 decides the idempotency
mechanism. Statements here are the obligations those decisions must satisfy.

## Open Questions
(none open — Q-1 lives on the mission.)

## Risks & Assumptions
- Assumption: clients adopt Idempotency-Key before enforcement mode (two-release rollout).

## Verification
AI-checks at G1: every FS testable, every NFS quantified. Change of this
artifact re-opens G1 (hash change).

## Change Log
| version | date | author | reason |
|---|---|---|---|
| 3 | 2026-10-18 | human:Asiant | signed fixture set (v1 intake, v2 wording pass) |
