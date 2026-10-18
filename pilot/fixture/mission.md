---
id: MISSION-003
mission: MISSION-003
version: 1
status: signed
template: {id: mission, version: 1, hash: sha256:fixture-mission-tpl}
links: {derives_from: [], covers: [], decided_by: []}
owner: {role: product-owner, person: Asiant}
summary_s0: "Idempotent order submission with partial fulfilment for marketplace orders."
---
# MISSION-003 — Idempotent order submission with partial fulfilment

## Purpose
Marketplace buyers retry order submission on flaky mobile networks; today a
retry can create duplicate orders or lose a partially fulfilled basket. This
mission makes order submission idempotent and partial fulfilment a first-class
outcome, so retries are safe and part-shipped orders stay truthful.

## Summary (S1)
Buyers resubmitting an order with the same Idempotency-Key get exactly one
order and the original order id back. Partial fulfilment is allowed end to
end: lines may ship separately, the buyer can track and cancel the remainder.
Performance and availability targets apply to the submission path. Skeleton
pilot mission for the walking skeleton (doc 12 §3).

## Scope & Non-scope
Covers order submission, idempotency, partial fulfilment, buyer-visible order
status, remainder cancellation and submission notifications. Non-goals:
payment-provider migrations, seller-side fulfilment UI redesign, cross-order
basket semantics, loyalty pricing.

## Problem & who hurts
Mobile buyers on flaky connections double-tap submit; support absorbs the
ticket load and sellers re-ship duplicates. Buyers with part-shipped baskets
see ambiguous state and cancel whole orders they still want.

## Value hypothesis
If retries are idempotent and partial fulfilment is visible and manageable,
duplicate-order tickets drop and part-shipped orders convert instead of
cancelling.

## Success metric + baseline
Duplicate-order incidents per 10k submissions (baseline 14) → target ≤ 2;
cancellation rate on part-shipped orders (baseline 31%) → target ≤ 15%.

## Risk tier
Standard (money-adjacent but well-understood domain; rollback = flag off).

## Stakeholder map
PO (accountable G0/G1/G5), lead architect (G1/G2/G5), checkout team lead (G2),
marketplace seller ops (G3), on-call release owner (G8, simulated in skeleton).

## Decisions & Rationale
KDD-002 (partial-fulfilment policy) and ADR-014 (idempotency design) carry the
reasoning; never re-argued inline here.

## Open Questions
- Q-1: Do seller payouts need per-line settlement hooks in this mission? Owner: seller ops. Due: before G5. Blocking: no.

## Risks & Assumptions
- Risk: dedup store becomes a submission-path SPOF → NFS-011 targets it.
- Assumption: clients send Idempotency-Key on all submissions (contract change shipped with this mission).

## Verification
Success metrics above measured on the post-release cohort; mission-level
verification plan hangs off G5's verification command.

## Change Log
| version | date | author | reason |
|---|---|---|---|
| 1 | 2026-10-18 | human:Asiant | fixture authored for walking-skeleton pilot (FS-014 family) |
