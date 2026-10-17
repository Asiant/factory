# 09 — Own UI & System Components (Decision D5)

Jira + Confluence + Git are the systems of record for tracking, documents and
code. Our own UI exists only where those tools cannot give humans a
**navigable understanding of a mission** or cannot enforce the gate/CLM
protocol. It is backed by our own system components; it never becomes a
second source of truth — every write goes through the adapters (doc 08 §09)
and the mission ledger (state/gates/audit/links) lives in Git only.

## 1. Own UI surfaces (v1 skeleton scope marked ◆)

| Surface | What it does | Backed by |
|---|---|---|
| ◆ **Mission Map** | One mission on one screen: narrative brief + the nested Semantic Artifact Graph (doc 10) — expandable mission→phase→artifact→section→item, tiered summaries, rollup health, stale/orphan highlighting | Mission Control state + artifact graph service (indexed from tools + Git ledger) |
| ◆ **Gate Inbox** | Approver's queue: each pending gate with its Review Pack (artifact, diff since last gate, AI-check evidence, open questions, risks, checklist, hashes being signed); Approve / Request Changes / Reject / Escalate | Gate service + authority matrix (doc 03 §4); writes gate record, drives Jira transition |
| ◆ **Change Lens** | "What changed at each level": pick a revision → semantic diff per level + impacted artifacts (graph propagation, doc 10 §5; prose by Review Explainer agent) | Artifact graph + diff service over Git ledger + tool history |
| ◆ **Persona Chat** | Converse with persona-agents (doc 02) bound to a mission/node context: ask from the graph, run skills, brainstorm toward artifact drafts. Sessions are archived to the Git ledger; outcomes land in artifacts (never only in chat). **Chat cannot approve gates** — approvals happen only in Gate Inbox/Jira (author decision 2026-10-17) |
| ◆ **Context Inspector** | Per agent run: context manifest, SEG-A..D snapshot viewer, CLM edit diffs — "exactly what did the model see, and what did it change?" | CLM runtime snapshots (doc 05) |
| **Reports** | Leverage / delivery / quality dashboards (doc 07), trend vs archived past reports (D9) | Reporting mart over event/cost ledgers |
| **Admin: Authority QnA** | Org onboarding + per-mission QnA that generates the gate authority matrix; confirm/version it (doc 03 §4) | Config service; matrix versioned in Git |
| **Admin: Agent Registry** | Agent versions, autonomy tiers, budgets, eval status; promote/rollback agent versions | Registry service; changes are reviewed config changes |

## 2. Own system components

```
Own UI (web)
  └─ BFF / API ──┬─ Mission Control (durable workflow, gate protocol, timers)
                 ├─ Agent Harness (registry, runner, sandbox, tool gateway)
                 ├─ CLM Runtime (context compile/edit-sync/snapshots — doc 05 §6)
                 ├─ Artifact Graph Service (indexes tools + Git ledger; traceability, impact)
                 ├─ Adapters: Jira · Confluence · Git/CI (doc 08 §09)
                 ├─ Ledgers: event/audit (append-only) · cost · eval results
                 └─ Reporting Mart (doc 07 metrics, report archive)
Data stores (ours, all rebuildable from Git ledger + tool APIs):
  workflow DB (Mission Control state) · graph index · report mart
Source of truth remains: Jira / Confluence / Git (ledger in Git only) (doc 08).
```

Rules:
- **Read from projections, write via protocol.** UI reads fast projections
  (graph index, workflow DB); every mutation flows through Mission Control /
  adapters so gates, hashes and audit are never bypassed by a UI shortcut.
- **Degraded mode:** if our components are down, humans keep working
  directly in Jira/Confluence/Git (takeover, doc 08); the harness rebuilds
  its indexes from the Git ledger + tool APIs on recovery.
- **Identity:** SSO/OIDC; UI session identity is what gate records sign with.
- **Not in v1 UI:** authoring artifacts in our UI (author in Confluence/Git;
  chat drafts are proposals routed to the homes), gate approvals inside
  chat, mobile app, multi-org tenancy screens.

## 3. Walking-skeleton cut (next cycle, if approved)

One mission type (new feature), one Jira project, one Confluence space, one
repo: G0→G2 + G5 gates live in Gate Inbox, Mission Map + Context Inspector
read-only, emulated CLM for FS/NFS + HLD agents, Persona Chat (no gate approvals), Git ledger + AI-off drill,
descriptive report v1 (no baseline — D9). Everything else stays blueprint.
