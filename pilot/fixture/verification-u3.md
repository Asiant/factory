---
id: VER-U3
mission: MISSION-003
version: 1
status: signed
template: {id: verification, version: 1, hash: sha256:fixture-verification-tpl}
links: {derives_from: [U3], covers: [], decided_by: []}
owner: {role: quality-lead, person: Asiant}
summary_s0: "VER-U3: G5-approved command green; TEST-220/221 evidence attached."
---
# VER-U3 — Verification report (skeleton slice)

## Purpose
Record of the approved verification command and measured evidence for U3.

## Summary (S1)
Command `make verify-u3` green on the U3 branch; TEST-221 and TEST-220 pass;
evidence attached and hashed. This report is the G7 input evidence set.

## Scope & Non-scope
U3 build slice. NFS evidence (NFS-007 load test) is a separate report.

## Command run
(G5-approved) `make verify-u3`

## Results
TEST-221 pass · TEST-220 pass · build green · lint green.

## NFS evidence links
(NFS-007/011/013 evidence produced at release rehearsal — out of slice.)

## Flaky quarantines
(none.)

## Decisions & Rationale
(none.)

## Open Questions
(none.)

## Risks & Assumptions
(none.)

## Verification
relates_to: [U3, TEST-221]

## Change Log
| version | date | author | reason |
|---|---|---|---|
| 1 | 2026-10-18 | human:Asiant | fixture authored |
