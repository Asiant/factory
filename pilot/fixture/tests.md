---
id: TESTS-001
mission: MISSION-003
version: 1
status: signed
template: {id: unit, version: 1, hash: sha256:fixture-test-tpl}
links: {derives_from: [FS-NFS], covers: [], decided_by: []}
owner: {role: quality-lead, person: Asiant}
summary_s0: "TESTS-001: TEST-220 (partial fulfilment) and TEST-221 (idempotent retry)."
---
# TESTS-001 — Test plan and cases (skeleton slice)

## Purpose
Derived test cases proving U2/U3 acceptance criteria; each case declares what
it verifies so the graph can expire evidence when requirements change.

## Summary (S1)
Two cases in the skeleton slice: TEST-220 for partial fulfilment (verifies
FS-015 + AC-U2-1) and TEST-221 for idempotent retry (verifies FS-014 +
AC-U3-1). Cases run under the G5-approved verification command.

## Scope & Non-scope
U2/U3 slice only; U1 cases come with the U1 build.

## U2 tests
### TEST-220 — Part-ship leaves order partially fulfilled
statement: Given a 3-line order, when 2 lines ship, then the order state is partially-fulfilled.
verifies: [FS-015, AC-U2-1]

## U3 tests
### TEST-221 — Retried submit creates one order
statement: Given a submitted order, when the same payload and Idempotency-Key are resubmitted, then exactly one order exists and the original order id is returned.
verifies: [FS-014, AC-U3-1, OrderService.submit()]

## Decisions & Rationale
(none.)

## Open Questions
(none.)

## Risks & Assumptions
(none.)

## Verification
Cases run via the G5-approved command; evidence in VER-U3.

## Change Log
| version | date | author | reason |
|---|---|---|---|
| 1 | 2026-10-18 | human:Asiant | fixture authored |
