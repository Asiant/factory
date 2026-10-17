# factory

Production-ready agent harness for an original mission-driven engineering lifecycle — **not a vendor AI-lifecycle framework, and more than a code factory** (differences: doc 01 §2.1):
mission/problem statement → FS/NFS → HLD → KDD → ADR → incremental-value units →
LLD → code → verification → release, with typed agent contracts, human/AI check
gates, a Context Language Model (CLM) context system, human takeover (AI-off),
and AI-leverage / delivery / quality reporting.

**Current cycle: blueprint + contracts only (no running code).**

| Doc | Contents |
|---|---|
| [docs/01-research-and-blueprint.md](docs/01-research-and-blueprint.md) | Research, reference architecture, gate/autonomy model, reporting design, roadmap, 50-question bank (§11) |
| [docs/00-decisions.md](docs/00-decisions.md) | Round-1 decisions (D1–D4), tension register, open blocking questions |
| [docs/02-agent-registry.yaml](docs/02-agent-registry.yaml) | 6 persona-agents (mirroring human roles) × contracted skills applied case-by-case: I/O, AI-checks, gates, budgets, evals, playbooks |
| [docs/04-artifact-templates.md](docs/04-artifact-templates.md) | Common base template + per-artifact templates, override/amend cascade, mission template-lock |
| [docs/03-schemas-and-gates.md](docs/03-schemas-and-gates.md) | Artifact IDs/linking, minimum content, gate catalogue G0–G10 & sign-off policy |
| [docs/05-clm-design.md](docs/05-clm-design.md) | Meta-style CLM: partitioned context file, lifecycle, safety controls, CLM eval suite |
| [docs/07-metrics-definitions.yaml](docs/07-metrics-definitions.yaml) | Versioned leverage / delivery (DORA) / quality metric definitions |
| [docs/08-human-takeover-and-integrations.md](docs/08-human-takeover-and-integrations.md) | AI-off guarantees, Git-only mission ledger, Jira/Confluence/Git adapter design |
| [docs/10-semantic-artifact-graph.md](docs/10-semantic-artifact-graph.md) | Semantic Artifact Graph: nested nodes, typed edges, hierarchical summaries, structured agent tools, change propagation |
| [docs/09-own-ui-and-system-components.md](docs/09-own-ui-and-system-components.md) | Own UI surfaces (Mission Map, Gate Inbox, Change Lens, Context Inspector) + own system components; walking-skeleton cut |
| [docs/11-signoff-register.md](docs/11-signoff-register.md) | Blueprint sign-off register |
| [docs/12-walking-skeleton-plan.md](docs/12-walking-skeleton-plan.md) | Walking skeleton plan: spikes S1–S3, build order B1–B9, pilot fixture, exit criteria |
