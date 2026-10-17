# 12 — Walking Skeleton Plan

Status: **PLAN ONLY** (this document). No code until this plan is signed off
through the same explain → question → sign-off walkthrough as the blueprint.
Goal: the thinnest end-to-end slice that proves the signed blueprint works on
one real mission — elaboration half fully, construction half at one unit.

## 1. Scope

### In scope (exactly)
- **One mission type:** new feature, standard template (`new-feature-standard`, doc 02).
- **One pilot mission** (see §3 fixture): Intake → FS/NFS → HLD → decomposition → **one unit** through LLD → implementation → verification. Gates G0, G1, G2, G5, G6, G7 live; G3/G4 exercised in lightweight form (KDD/ADR recorded for the pilot's real decisions); G8 as a *simulated* release plan only (no production deploy in skeleton).
- **One Jira project, one Confluence space, one Git repo, one ledger repo.**
- **Personas/skills live:** product-agent (mission-intake, fs-elaboration, value-slicing), architect-agent (hld-design, nfs-design, kdd-recording, adr-drafting), engineering-agent (lld-design, implementation), quality-agent (verification). Delivery/knowledge personas: reporting + change-explaining skills only, as batch/manual triggers.
- **UI:** Mission Map, Gate Inbox, Change Lens, Context Inspector (all ◆ doc 09) + Persona Chat (no gate approvals).
- **CLM:** emulated context-as-file (doc 05 §6) for fs-elaboration and hld-design only; other skills run with compiled graph context (no SEG-C editing) — proving CLM where it matters without betting every skill on it.
- **Graph:** nested extraction from Confluence/Git/Jira for the pilot mission; structured tools (doc 10 §3) as the only agent read path in scope.
- **Reporting:** descriptive v1 report (doc 07, no baseline) generated once at skeleton end + archived.

### Explicitly out of scope
Production deployment/real G8 execution · G9/G10 admin UIs (config files edited by hand) · auto-approval (guardrails designed, but **skeleton runs L1 everywhere except verification** — auto-pass enabled only after skeleton review) · multi-mission/multi-team concurrency beyond 3 concurrent missions · native CLM model · compliance features (D8) · mobile.

## 2. Phase 0 — De-risking spikes (before any skeleton build)

Each spike: timeboxed, throwaway code allowed, pass/fail criterion decided in advance. **A failed spike stops the plan for redesign, not for heroics.**

| # | Spike | Timebox | Build | Pass criterion | If it fails |
|---|---|---|---|---|---|
| S1 | Graph extraction & impact | 3–4 days | Parser for Confluence-export/Git markdown pilot artifacts → nodes/edges; `impact_preview` for an FS change | Changing pilot FS-014 flags exactly {HLD comp, ADR, unit, test evidence}; zero signed-node false positives on the fixture set | Simplify node model (fewer edge types / coarser granularity) and re-spike |
| S2 | Emulated CLM loop | 3–4 days | fs-elaboration skill with `edit_ctx`, SEG partition, snapshots on one API model | CLM eval quick suite: 100% signed-constraint retention; edit-validity ≥90%; cost/run within budget envelope vs append-only baseline measured | Fall back to compiled-context-only for all skills; CLM revisited post-skeleton |
| S3 | Gate hash-capture | 2–3 days | Confluence page version+hash capture, Jira transition webhook → gate record in Git ledger; edit page post-sign → stale detection | Stale-gate fires on post-sign edit; gate record reconstructs "who signed what hash when" from ledger alone | Artifact type moves primary home to Git (doc 08 fallback) before build |

**Spike order:** S1 and S3 in parallel (independent), then S2 (needs graph context tools from S1 in minimal form). Spike outputs: a one-page verdict each, filed in `docs/spikes/`, go/no-go recorded in the decision log.

## 3. Pilot mission fixture

A real (preferred) or realistic mission, chosen at kickoff with:
- 8–15 FS items, 3–5 NFS with quantifiable targets, at least one genuine design decision worthy of a KDD and one ADR, decomposable into 3–5 units (skeleton builds **one**).
- A named human for each human gate role (G0–G7) from the pilot team.
- Success definition for the skeleton itself: mission reaches G7 on one unit with all gate records in the ledger, Change Lens explains one mid-flight FS change, one AI-off stage completed by hand.

If no real mission is available, use the fallback fixture: *"Idempotent order submission with partial fulfilment"* (FS-014 family already used in docs 10) written as full templates in the pilot Confluence space.

## 4. Build order (after spikes pass)

| Step | Deliverable | Depends on | Acceptance test |
|---|---|---|---|
| B1 | Ledger + Mission Control core: state.yaml/gates.yaml/audit.jsonl in Git; stage machine for the standard template; durable pause/resume at gates | S3 | Kill the service mid-gate-wait; restart; mission resumes at same gate with ledger intact |
| B2 | Adapters: Jira (issues/transitions/webhooks), Confluence (page CRUD/version/hash), Git (branch/PR/checks) | B1 | Create mission in UI → Jira epic + Confluence tree + ledger entries exist and cross-link |
| B3 | Graph service: extraction pipeline, node/edge store (relational), structured tools API (doc 10 §3), summaries S0/S1 | S1, B2 | `trace(FS-014 → test)` returns full path; orphan check flags a deliberately uncovered FS |
| B4 | CLM runtime: context compile (graph neighbourhood), `edit_ctx`, snapshots, Context Inspector feed | S2, B3 | Run fs-elaboration; inspector shows manifest + every SEG-C diff; replay from snapshot reproduces context |
| B5 | Skills runtime: persona registry enforcement (ceilings, budgets), fs-elaboration + hld-design + kdd/adr + value-slicing live | B4 | A skill attempting a forbidden tool (e.g. engineering persona calling merge) is blocked and logged |
| B6 | Gate Inbox + Review Packs + Jira one-click capture; hash staleness | B1–B3 | Sign G1 in Jira; edit Confluence page; gate shows STALE and stage blocks |
| B7 | Mission Map + Change Lens | B3 | Mid-flight FS change → Change Lens lists impacted nodes by class (invalidates/requires-review/rollup) matching S1 expectations |
| B8 | Construction slice: lld-design, implementation (branch+PR, never merges), verification skill with approved verification command | B5 | One unit: LLD → PR → verification report with measured evidence; human merges |
| B9 | Persona Chat (bound to mission context; no gate actions), reporting v1, AI-off drill (one stage by hand), skeleton retrospective | B5–B8 | Chat draft lands as artifact proposal; AI-off stage validates identically; report generated + archived |

Estimated total: spikes ~2 weeks elapsed; B1–B9 ~4–6 weeks elapsed for a small team (2–3 engineers + author time for gates). Estimates are planning aids, not commitments; re-estimate after spike verdicts.

## 5. Discovery checklist (kickoff, before S1)

- [ ] Pilot mission selected (real or fixture) + named gate humans per role
- [ ] Jira: project key, issue types for Mission/Unit, workflow transitions usable for gates, webhook/API access, service account
- [ ] Confluence: space key, template page IDs (doc 04 templates loaded), API access, version/history availability confirmed
- [ ] Git: host (GitHub/GitLab/Bitbucket), pilot repo, branch protection + CODEOWNERS, ledger repo created
- [ ] IdP: SSO/OIDC app for UI + Jira identity mapping for approvers
- [ ] Model access: API model for emulated CLM + skills; per-run budget limits set
- [ ] Authority QnA (doc 03 §4) run for the pilot team; matrix confirmed by a named admin
- [ ] Sandbox: where skills run code (CI runner/container), network/tool allowlist

## 6. Risks & mitigations (top 5)

| Risk | Mitigation |
|---|---|
| Confluence/Jira APIs too weak for hash/version capture | S3 spikes this first; Git-home fallback pre-designed (doc 08) |
| Graph extraction brittle on free-form pages | Templates enforced from day 1 (doc 04); parser targets template structure; inferred edges quarantined (doc 10) |
| Emulated CLM costs explode (full context re-send per call) | S2 measures real economy; budgets + circuit breakers in skill contracts; compiled-context fallback ready |
| Gate fatigue kills pilot-team goodwill | Skeleton gates limited to G0–G2/G5–G7; Review Packs designed to cut review time; touch-minutes measured from report v1 |
| Scope creep toward full platform | §1 out-of-scope list is normative; new requests become post-skeleton backlog entries, not skeleton changes |

## 7. Exit criteria for the skeleton (all must hold)

1. Pilot mission completes Intake → one unit merged via G7, every gate decision reconstructable from the Git ledger alone.
2. One mid-flight FS change demonstrated end-to-end in Change Lens with correct impact classification.
3. CLM eval quick suite green for the two CLM skills (or documented fallback decision taken).
4. One full stage completed AI-off by a human using playbooks, artifacts validating identically.
5. Report v1 produced and archived; skeleton retrospective held; go/no-go recommendation for (a) enabling low-risk auto-approval, (b) second mission type / bugfix template, (c) real G8.

## 8. What happens after

Skeleton review → decide: harden toward pilot-team production use
(more missions, auto-approval on, admin UIs), or adjust the blueprint
first. Rollout beyond the pilot team is a separate plan, not an extension
of this one.
