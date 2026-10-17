# 08 — Human Takeover (AI-off) · Integrations (Jira · Confluence · Git)

## Storage model (author-confirmed 2026-10-17) — no separate mirror

Everything already lives in the tools; we do not duplicate content.

| Content | Single home | Notes |
|---|---|---|
| Long-form artifacts (Mission, FS/NFS, HLD, KDD) | **Confluence** | one page tree per mission, from templates (doc 04) |
| Code, ADRs, templates, playbooks | **Git** | PR-reviewed |
| Tracking, gate clicks | **Jira** | issue types project the lifecycle |
| **Mission Ledger: state, gate records, audit, artifact links+hashes** | **Git only** | plain files (below). Our system reads/writes them via Git. Any DB/cache in our components is disposable and rebuildable from Git + tool APIs — Git is the sole authority for the ledger |
| Artifact graph index, UI caches | our components | rebuildable projections; deleting them loses nothing |

```
ledger-repo (Git)
  missions/MISSION-003/
    state.yaml        # stage, gate status, next action, owner
    gates.yaml        # append-only gate records (hashes signed, approver, ts)
    audit.jsonl       # append-only event log
    links.yaml        # artifact -> {home: confluence|jira|git, id/url, version, hash}
```

## 08 Human takeover

1. **AI-off = humans work in the same tools.** Jira/Confluence/Git remain
   fully usable without any agent; playbooks per skill (doc 02) describe the
   manual procedure using the same templates (doc 04) and checks — hand-made
   artifacts validate identically.
2. **State is readable without our UI:** `state.yaml` + `gates.yaml` in Git
   answer "where is this mission, what was signed, what happens next".
3. **Harness outage:** humans keep working; on recovery the harness rebuilds
   its indexes from Git ledger + tool APIs. Human edits made during outage
   win; skills rebase onto them.
4. **AI-off drill:** run as regular practice (not a rollout blocker) —
   drive a mission two stages with agents disabled; findings feed playbook
   fixes.
5. **Tool (Jira/Confluence) outage / vendor exit:** governed by those
   tools' own backup/export; explicitly out of scope for v1 (optional
   periodic export may be added later).

## 09 Integrations

| Capability | System | Contract |
|---|---|---|
| Mission / unit tracking | **Jira** | Mission = Epic (or dedicated type), Unit = Story/Sub-task; status projects stage state |
| Gate sign-off | **Jira transition OR own Gate Inbox — one click, human's choice** | Behind the click, the system auto-captures the gate record into the Git ledger: artifact versions + hashes at that moment (Confluence page version, Git SHA), approver identity vs authority matrix (doc 03 §4). No second approval step. A raw Jira transition the system cannot attribute/capture does not advance the stage |
| Long-form artifacts | **Confluence** | harness reads page version + content hash at gate time; post-sign-off edit ⇒ hash mismatch ⇒ gate stale (doc 03) |
| ADRs & code | **Git** | ADR files PR-reviewed; Confluence pages link, never copy |
| Code review (G7) | **Git host PR** | checks + CODEOWNERS captured as gate evidence; agents never merge |
| CI/CD (G8) | existing pipelines | verification command in CI; deploy events feed delivery metrics |
| Identity | IdP (SSO/OIDC) / Jira account | asserted identity checked against authority matrix; free-text names are not sign-off |

Rules: exactly **one primary home per artifact type** (above) — no double
bookkeeping · hash-pinning at gates uses each home's native versioning
(Confluence version, Git SHA, Jira updated-timestamp as weak fallback —
artifact types needing strong proof must live where versioning is strong) ·
harness failure never blocks humans from working in the tools directly.
