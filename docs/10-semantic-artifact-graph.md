# 10 — Semantic Artifact Graph ("Serena for documentation")

## 0. Answer: yes, this nesting is required

Flat document links (`covers: [FS-011]`) break at real scale: documents are
too coarse (one paragraph changes, a whole HLD goes "stale"), agents fall
back to file-read/grep and miss impact, and humans cannot navigate hundreds
of pages. The fix is what Serena does for code: instead of text search over
files, it exposes **symbol-level semantic tools** (overview, find symbol,
find references) built on a parsed structure. We build the same layer over
documentation, decisions and delivery artifacts.

> **The graph is the primary interface — for agents and humans.**
> Raw file read / full-text search is a fallback for discovery only, and
> its results enter the workflow only once resolved to graph node IDs.

## 1. Nested node model — documents are containers, not atoms

```
MISSION-003                         (mission)
└─ ELAB-01  Mission Elaboration     (phase)
│   ├─ FS-NFS@v3                    (artifact)
│   │   ├─ §2 Ordering              (section)
│   │   │   ├─ FS-014  "Orders idempotent on retry"      (atomic item)
│   │   │   └─ FS-015  "Partial fulfilment allowed"
│   │   └─ §4 Performance
│   │       └─ NFS-007 "p95 checkout < 800ms @ 2k rps"
│   ├─ HLD@v2 ── §3.2 Component C-3 "Order Service"
│   ├─ KDD-002, ADR-014 …
└─ CONST-01 Mission Construction
    ├─ U3 (unit) ── LLD@v1 ── API-OP-09 "POST /orders (idempotency-key)"
    └─ PR-482 ── code symbol `OrderService.submit()` ── TEST-221
```

**Granularity rule:** the smallest node is the smallest thing that can be
*owned, changed, signed or verified independently* — an FS item, an NFS
target, a component, a decision clause, an acceptance criterion, an API
operation, a test. Anything smaller stays prose inside its node; anything
larger must decompose.

| Node type | Examples | Key fields |
|---|---|---|
| Container | mission, phase, artifact, section | rollup status, child summary |
| Item | FS-014, NFS-007, acceptance criterion | statement, measure, status |
| Design | component C-3, data entity, API operation | contract, constraints |
| Decision | KDD-002, ADR-014 (+ clauses) | options, decision, consequences |
| Delivery | unit U3, LLD, PR, test, release | value statement, evidence |
| External | code symbol, Jira issue, Confluence page | foreign key into source system |

Every node: `id` (stable, never reused), canonical address
(`mission://MISSION-003/fs-nfs#FS-014`, resolves regardless of whether the
source lives in Confluence, Git or Jira), `version + content_hash`,
`status` (draft/in-review/signed/stale/under-review/superseded),
`owner`, `summary_refs` (§4), provenance (`authored_by`, run/gate ids).

## 2. Typed edges — containment is only one relation

| Edge | Meaning | Change-propagation behaviour (§5) |
|---|---|---|
| `contains` | nesting (parent→child) | child change rolls up: parent summary + status stale |
| `derives_from` | this node exists because of that one | source change ⇒ dependent requires review |
| `covers / satisfies` | design/unit satisfies FS/NFS | source change ⇒ coverage invalidated until re-checked |
| `decided_by` | constrained by KDD/ADR clause | decision superseded ⇒ dependents flagged immediately |
| `depends_on` | needs the other node as-is | target change ⇒ dependent review |
| `implements` | LLD/code implements design node | design change ⇒ implementation suspect |
| `verifies` | test/evidence verifies item | item change ⇒ evidence expired |
| `contradicts` | known conflict (must resolve) | blocks gate while open |
| `supersedes` | replaces (immutable history) | successors inherit dependents for re-review |
| `relates_to` | weak/informational | notification only, never staleness |

Every edge carries: `type, from, to, source` (`declared` in artifact /
`parsed` structural / `inferred` by agent), `confidence` (inferred only),
`created_by`, `at_hash`. **Rules:** gate invalidation may only be driven by
declared/parsed edges — inferred edges create *suggestions* a human or agent
must confirm. Cross-boundary edges link doc nodes to **code symbols** (via
the code graph / LSP-style index), so `FS-014 → C-3 → POST /orders →
OrderService.submit() → TEST-221` is one walkable path.

## 3. Structured agent tools (no random searching)

Agents access knowledge through these tools (tool-gateway enforced, doc 01
§3); `read_file`/`search` are restricted and logged when used as fallback.

| Tool (Serena analogue) | Purpose |
|---|---|
| `get_overview(node_id, level)` | summary-first orientation (get_symbols_overview) |
| `get_node(node_id, include_children?)` | exact node content by address (find_symbol) |
| `find_nodes(type, filters…)` | structured query: type/status/owner/gate/uncovered… |
| `get_neighbours(node_id, edges, direction, depth)` | parents, children, dependents, dependencies |
| `find_references(node_id)` | "what depends on / covers / verifies this?" (find_referencing_symbols) |
| `trace(from_id, to_type)` | path proof, e.g. FS→Unit→Test→Release; gaps returned explicitly |
| `impact_preview(node_id, new_version)` | propagation dry-run before a change is accepted (§5) |
| `coverage_report(scope, requirement_type)` | uncovered FS/NFS, unverified items, orphans |
| `get_context_for_task(agent_id, seed_nodes, budget)` | graph-neighbourhood context compilation for CLM (doc 05): walks typed edges by relevance (edge type > distance > recency), returns summary-then-detail nodes + manifest of node IDs |
| `propose_edge / propose_node_change` | agents *propose*; application goes through AI-checks + gates |

Discovery search (full-text / vector) exists but returns **candidate node
IDs with scores**; the agent must then verify via `get_node` /
`find_references` before citing. Every claim in an agent output must cite
node IDs — uncited claims fail AI-checks.

## 4. Hierarchical summaries — navigation for humans, selection for CLM

Each node carries tiered summaries, generated **bottom-up**
(item → section → artifact → phase → mission):

| Tier | Form | Used for |
|---|---|---|
| S0 | one line (≤140 chars) | graph labels, lists, breadcrumbs |
| S1 | ~80-word brief: purpose, status, key obligations | Mission Map cards, Gate Inbox, context selection |
| S2 | structured digest: decisions, constraints, open questions, risks, child rollup (signed/stale counts) | review packs, impact previews |

Summary governance:
- A summary is a **derived projection**: it stores `source_hash`; when any
  descendant changes, the summary is marked stale and queued for
  regeneration — summary staleness is itself a visible status, never silent.
- Humans can **pin/edit** a summary (e.g. the Mission Brief narrative); a
  pinned summary is no longer auto-overwritten — changes produce a proposed
  diff instead. Signed-level summaries (gate packs) are generated at gate
  time and frozen into the gate record.
- Summaries **never become truth**: every summary renders with links to its
  source nodes, and agents cite node IDs, not summaries, for claims.
- Human navigation = progressive disclosure: Mission Map shows S0/S1 and
  rollup health; expanding walks `contains`; any node opens with its
  summary, children, references and "what changed" in one view.

## 5. Change propagation — structured, gated, never silent

```
node version bump
  → 1. diff classification (editorial | semantic | structural, by AI-check + rules)
  → 2. reverse walk over typed edges → impact set, each entry classified:
        INVALIDATES   signed dependent (hash changed) → gate re-opens
        REQUIRES_REVIEW  derived/covered/implemented dependent → status=stale,
                         work item to owner + producing agent re-run proposal
        ROLLUP        ancestors → summary/status regeneration queued
        NOTIFY        relates_to only
  → 3. Propagation stops at sign-off boundaries: propagation creates
       *proposals and staleness*, never edits signed nodes and never
       carries an approval across a change.
       AUTO-UPDATE POLICY (author decision 2026-10-17): derived projections
       (summaries, indexes, coverage/trace matrices) always auto-update;
       UNSIGNED draft dependents (e.g. draft LLD section, draft test cases)
       auto-regenerate as proposals visibly marked "auto-updated — review
       me" (status stays draft, prior version retained); signed nodes only
       ever go stale — nothing auto-edits them.
  → 4. owners accept/reject each impact in Change Lens; graph shows
       unresolved impact count per mission (a gate cannot open with
       INVALIDATES unresolved in its scope)
  → 5. all of it is event-logged (who/what propagated, who cleared it)
```

Worked example: `FS-014` statement changes → `HLD §3.2/C-3` (covers)
REQUIRES_REVIEW → `ADR-014` (decided_by C-3 context) flagged → `U3`
(covers FS-014) stale → its acceptance criterion + `TEST-221` (verifies)
evidence expired → Mission S2 summary shows "1 invalidated coverage,
2 pending reviews"; G5 cannot re-open-sign until cleared. Code node
`OrderService.submit()` (implements) is *suspect*, not auto-edited.

Controls: depth/breadth limits per edge type, batching for bulk changes,
dry-run `impact_preview` in the UI *before* an author saves a semantic
change to a signed node (they see the blast radius first).

## 6. Build & storage

- **Sources remain authoritative** (Confluence/Git/Jira, doc 08); parsers
  extract nodes/edges from templates, headings, ID conventions, link fields
  and code annotations into the graph index. The index is a **rebuildable
  projection** — delete it and rebuild from sources + Git ledger.
- Graph store: property-graph DB or relational adjacency tables (skeleton:
  relational + recursive queries is enough); graph snapshots are taken at
  every gate (the signed state of the world), enabling "graph as of G2".
- Ontology (node/edge types) is versioned config; changing it is a reviewed
  change like a schema migration, with backfill/re-index plan.
- Determinism first: declared/parsed edges are exact; inferred edges are
  additive hints with confidence, expire if unconfirmed, and never drive
  gates. This is the doc-side equivalent of LSP precision vs grep fuzz.

## 7. What this changes in the other docs

- **Doc 03 §1** now points here: front-matter declares node/edge seeds;
  this doc defines the full model.
- **Doc 05 (CLM):** `get_context_for_task` replaces dump-and-embed context
  assembly; the context manifest lists node IDs + summary tiers used.
- **Doc 09 (UI):** Mission Map = nested graph explorer (not a flat
  diagram); Change Lens = impact propagation view (§5); every list in the
  UI is a structured graph query, not a document list.
- **Doc 02 (Agents):** registry tool lists change — `read_repo/read_artifacts`
  become graph tools (§3) with raw search restricted.
- **Metrics (doc 07):** adds graph health — orphan rate, unresolved-impact
  age, summary staleness, % agent claims with node citations.
