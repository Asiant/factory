# 04 — Artifact Templates: Common Base + Per-Artifact + Overrides

Decision (walkthrough, 2026-10-17): **every artifact type has its own
template; all templates inherit a common base template; the base and
per-artifact templates can be overwritten/amended under control.**

## 1. Template inheritance model

```
templates/
  _common.md            ← base: inherited by ALL artifacts, never used alone
  mission.md            ← _common + mission sections
  fs-nfs.md  hld.md  kdd.md  adr.md  unit.md  lld.md
  verification.md  release.md  review-pack.md  report.md
```

Resolution order (like CSS cascade — closest wins):
**platform default → org override → team override → mission amendment**
Each level may only *extend or amend as permitted by §3*; the resolved
template for a mission is frozen into `mission.template-lock.yaml`
(template ids + versions + hashes) at G0, so an in-flight mission never
changes shape mid-way.

## 2. Common base template (all artifacts inherit)

```markdown
---
id: <TYPE-NNN>            # graph node id (doc 10)
mission: MISSION-NNN
version: N
status: draft|in-review|signed|superseded
template: {id: fs-nfs, version: 2.1, hash: sha256:…}
links: {derives_from: [], covers: [], decided_by: []}
owner: {role: …, person: <idp>}
summary_s0: ""            # one-line (doc 10 summaries)
---
# <Title>
## Purpose            — why this artifact exists, in 3–5 lines
## Summary (S1)       — ~80-word brief for navigators/reviewers
## Scope & Non-scope  — what this covers / explicitly does not
## <…artifact-specific sections (§4)…>
## Decisions & Rationale    — links to KDD/ADR nodes (never re-argued inline)
## Open Questions     — each: id, question, owner, due, blocking?
## Risks & Assumptions
## Verification       — how correctness of THIS artifact is checked
## Change Log         — version, date, author (agent skill+persona / human), reason
```

Invariants (AI-check enforced): graph-node header present, S0/S1 summaries
present, every Open Question has an owner, Change Log entry per version.

## 3. Override & amend rules

| Change kind | Examples | Who may | Effect on signed artifacts |
|---|---|---|---|
| **Extend** (add optional section/field) | team adds "Regulatory refs" to HLD | team template PR + context owner (G9) | none — applies to new drafts |
| **Amend** (reword guidance, reorder, change optional→required within artifact template) | org requires "Capacity assumptions" in every HLD | org admin approval, template version bump | none retroactively; in-flight *drafts* migrate or finish on locked version (author chooses) |
| **Base amend** (change `_common`) | add "Data classification" field for all artifacts | org admin + impact preview (which templates/missions affected) | signed artifacts stay on their pinned template hash — **template drift never voids a gate**; only content hash does (doc 03) |
| **Remove / weaken a required section** | drop "Non-goals" from Mission | **forbidden by override** — requires platform template change + leadership sign-off; treated as a governance change, not a template tweak | n/a |
| **Mission amendment** | this mission's FS template needs an extra "Partner API" section | mission owner proposes, approver of next gate accepts; recorded in template-lock | only that mission |

Rules: templates are versioned artifacts in Git reviewed like code ·
every override is a diff against its parent (no copy-paste forks) ·
the template a signed artifact used is recorded in its header — auditors
always see the exact rules it was written under · skills (doc 02) declare
which template version ranges they can produce; eval suites run against
current org-resolved templates.

## 4. Per-artifact specific sections (on top of _common)

| Template | Specific sections (required unless noted) |
|---|---|
| mission | Problem & who hurts · Value hypothesis · Success metric + baseline · Scope/Non-goals (in base) · Risk tier · Stakeholder map |
| fs-nfs | FS items (id, statement, acceptance test, priority, source) · NFS items (category, **quantified target**, verification method) · Glossary refs · MoSCoW summary (optional) |
| hld | Context diagram · Components & boundaries (each a graph node) · Data model sketch · Integrations · Failure modes · Capacity assumptions · **FS/NFS coverage matrix** (generated, doc 10) |
| kdd | Context · Options considered (≥2 or justified) · Trade-off scoring · Decision · Consequences · Deciders |
| adr | As KDD, engineering scope · Status lifecycle · Conflict/supersede links · Compliance-with (KDD refs) |
| unit | Value statement ("user can…") · Acceptance criteria · Covered FS ids · Dependencies (DAG refs) · Size estimate · Demo outcome |
| lld | APIs/contracts · Schemas · Sequences · Error handling · Low-level ADR refs · Test plan |
| verification | Command run (G5-approved) · Results · NFS evidence links · Flaky quarantines |
| release | Units included · Rollout steps · Rollback rehearsal evidence · Flags · Comms · Owner/on-call |
| review-pack | (generated, doc 09/10) Artifact + diff · AI-check evidence · Impact list · Reviewer checklist |
| report | Metric definition versions · Period · Leverage/Delivery/Quality sections (doc 07) · Lineage |
