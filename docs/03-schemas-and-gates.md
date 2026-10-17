# 03 — Artifact Schemas, IDs & Gate Policy

## 1. Identity & linking (the artifact graph)

Every artifact carries front-matter / tool fields:

```yaml
id: FS-014            # typed, immutable: MISSION- FS- NFS- HLD- KDD- ADR- U- LLD- VER- REL-
mission: MISSION-003
version: 3
status: draft | in-review | signed | superseded
links:
  derives_from: [MISSION-003]
  covers: [FS-011, FS-012]        # typed edges — impact analysis walks these
  decided_by: [KDD-002]
hash: sha256:…                     # gate signs a hash, not a vibe
owner: {role: lead-architect, person: idp-subject}
created: {by: agent:hld-designer@1.0.0 | human:<idp>, run_id: …, context_manifest: sha256:…}
```

Rules: IDs never reused · signed artifacts immutable (change = new version +
supersede link) · orphan links fail the phase-boundary verification gate in CI ·
the traceability matrix (Mission→FS→HLD→KDD/ADR→Unit→LLD→PR→Test→Release) is
generated from these edges, never hand-maintained.

> **This section is only the declaration format.** The full nested node/edge
> model, hierarchical summaries, structured agent tools and change-propagation
> rules live in **doc 10 (Semantic Artifact Graph)** — artifacts are containers
> of addressable item/section/decision nodes, not atomic documents.

## 2. Artifact minimum content

Templates are governed by **doc 04**: a common base template inherited by
all artifacts, a specific template per artifact type, resolved
platform → org → team → mission, locked per mission at G0; template drift
never voids a gate (only content-hash change does). The table below is the
required-content summary of those templates.

| Artifact | Must contain (AI-check enforces presence; human judges quality) |
|---|---|
| Mission | problem, who hurts, value hypothesis, scope, **non-goals**, success metric + baseline, risk tier |
| FS | per item: id, statement, acceptance test (measurable), priority, source stakeholder |
| NFS | per item: category (perf/security/compliance/operability/cost…), **quantified target**, verification method |
| HLD | context diagram, components & boundaries, data model sketch, integrations, failure modes, capacity assumptions, FS/NFS coverage matrix |
| KDD | context, ≥2 options (or justified sole option), trade-off scoring, decision, consequences, deciders |
| ADR | as KDD but engineering scope; status lifecycle proposed→accepted→superseded; conflict links |
| Unit | value statement ("user can …"), acceptance criteria, covered FS ids, dependencies, size estimate, demoable outcome |
| LLD | APIs/contracts, schemas, sequences, error handling, low-level ADRs, test plan |
| Verification | command run (the G5-approved one), results, NFS evidence links, flaky quarantines |
| Release | units included, rollout steps, rollback rehearsal evidence, flags, comms, owner |

## 3. Gate catalogue & policy

| Gate | After | Sign-off (accountable humans) | Dual control | Re-opens when |
|---|---|---|---|---|
| G0 | Mission intake | Product Owner | — | mission hash changes |
| G1 | FS/NFS | PO + Lead Architect | high tier | FS/NFS hash changes |
| G2 | HLD | Architect + team leads | — | HLD or signed FS/NFS changes |
| G3 | KDDs | Stakeholders | **high tier** | KDD set changes |
| G4 | ADRs | Architect + engineers | **high tier** | ADR set / HLD changes |
| G5 | Decomposition (+ verification command) | PO + Architect | — | unit graph changes |
| G6 | LLD (per unit) | Unit engineers (+ architect if ADR) — **auto-eligible: low-risk tier + no low-level ADR + all AI-checks green (doc 01 §5 guardrails)** | — | LLD/ADR changes |
| G7 | Code (per unit PR) | CODEOWNERS review | per repo policy | new commits pushed |
| G8 | Release | Release owner / on-call | **high tier** | plan or contents change |
| G9 | Context changes | Context owner | — | n/a (per proposal) |
| G10 | Monthly reporting review | Eng. leadership | — | n/a |

Gate protocol (harness-enforced):
- Gate record = `{gate, mission, artifact_hashes[], decision: approve|request_changes|reject|escalate, approvers[idp], rationale, dissent[], ts}` — immutable, append-only.
- **Approver ≠ proposer** for G3/G4/G8; an agent can never be an approver; a
  decision on stale hashes is void (harness re-requests the gate).
- `request_changes` comments are injected into the producing agent's SEG-C
  context verbatim on re-run — feedback is context, not chat loss.
- Gate wait incurs no compute (durable pause); SLA timers escalate to the
  delegate named in the authority matrix, never auto-approve.

## 4. Gate authority matrix — seeded by QnA (Decision D7)

Authority is **not hand-written config**. It is generated from a structured
Q&A and then confirmed:

1. **Org onboarding QnA** (once, ~15 questions): for each gate G0–G10 × risk
   tier — accountable role, named approver(s), is dual-control required,
   delegate when unavailable, response SLA, escalation target, can this gate
   ever run at L2/L3 autonomy.
2. **Mission QnA addendum** (per mission, at intake): risk tier confirmation,
   mission-specific stakeholders for G3, release owner/on-call for G8,
   any gate that must be *stricter* than org default (never looser without
   admin override + rationale recorded).
3. **Generation + confirmation:** answers compile to `authority-matrix.yaml`
   (roles → IdP subjects/groups); a named org admin reviews and confirms in
   the UI before the first gate can fire. Unanswered gate = gate defaults to
   *blocked*, never to auto-approve.
4. **Change control:** matrix changes are versioned, diffed, themselves
   approved by the org admin, and apply only to gates opened after the change
   (in-flight gates keep the matrix they opened under — recorded on the gate
   record).

Example output row:

```yaml
- gate: G4            # ADRs
  risk_tier: high
  approvers: [{role: lead-architect, subject: group:architects},
              {role: senior-engineer, subject: group:eng-leads}]
  dual_control: true
  proposer_excluded: true
  delegate: {subject: group:architects-deputies, after_sla_breach: true}
  sla_hours: 48
  escalate_to: group:eng-directors
  max_autonomy: L1
```
