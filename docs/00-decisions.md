# Decision Log — Round 1 (2026-10-17)

These decisions, specified via the originating requirements and structured
Q&A, bind the blueprint in this folder.

| # | Decision (author-specified) | Choice | Implication |
|---|---|---|---|
| D1 | CLM meaning | **Meta-style Context Language Model** — model natively manages/edits its own context-as-a-file | We design for a CLM model/runtime (context file mirrored & synced per turn), not just a retrieval/compiler layer. Vendor/model selection, eval of context-edit behaviour, and safety partitioning (§05) become critical-path. Research: context-as-file sync, multi-agent context files coexisting [facebookresearch/context-language-models](https://github.com/facebookresearch/context-language-models), [arXiv:2609.37725](https://arxiv.org/abs/2609.37725). |
| D2 | Harness | **Vendor-neutral, own harness** | We build our own durable state machine, agent registry, tool gateway and gate protocol. Existing coding agents/models are pluggable executors behind contracts — never the platform itself. No external vendor lifecycle framework is adopted, even as a method: phases, gates and rituals are defined by this blueprint (doc 01 §2.1). |
| D3 | Source of truth | **Existing tools** (e.g. Jira/Confluence-class systems — **exact tools TBD, see Q-OPEN-1**) | Missions, gates and sign-offs live where teams already work. The harness must integrate via adapters, and must still guarantee human takeover: human takeover is via the same tools, with the mission ledger (state/gates/audit/links) in Git only — no duplicated artifact content (revised in doc 08 walkthrough). |
| D4 | v1 scope | **Blueprint + contracts only** (no running code) | This cycle delivers hardened design: schemas, templates, agent contracts, gate policies, CLM design, metric definitions, takeover playbooks, and an implementation plan. Walking skeleton is the proposed *next* cycle, gated on open questions §10 of doc 01. |

## Tension register (explicit, not hidden)

1. **D1 vs governance:** Meta CLM grants the model *unrestricted* context edits. Signed FS/HLD/ADR artifacts cannot be silently rewritten. Resolution: partitioned context (§05) — signed segments are harness-injected read-only; CLM freedom applies only to its working segment. This deviates from "unrestricted" CLM; the deviation is deliberate and must be validated by eval (does partitioning lose the CLM benefit?).
2. **D3 vs takeover/audit:** AI-off means humans take over *in Jira/Confluence/Git* using playbooks; our own records (ledger) are Git-only files so state is always readable without our UI. Vendor-off/disaster recovery of the SaaS tools themselves is out of scope v1 (author-confirmed, doc 08).
3. **D2 vs speed:** Own harness is slower to first value than adopting a ready-made vendor workflow. Mitigation: walking-skeleton scope discipline in the implementation plan (doc 01 §10).

## Round 2 decisions (2026-10-17, same sole author — answers to structured questions)

| # | Question | Decision | Implication |
|---|---|---|---|
| D5 | Existing tools | **Jira + Confluence + Git**, plus a **separate own UI** backed by our own system components where needed | Adapters: Jira (mission/unit tracking + gate transitions), Confluence (long-form artifacts FS/HLD/KDD), Git (code, ADRs-as-code where teams prefer, mission ledger). Own UI is additive (Mission Map, Gate Inbox, Review Packs, Reports) and reads/writes through the same adapters/mirror — never a second source of truth. Detail: doc 08 §09 + doc 09. |
| D6 | CLM model/runtime | **Emulate context-as-file** on a (frontier/API) model — no self-hosted CLM model, no fine-tune in v1 | Harness implements the CLM mechanism itself: context file mirrored per run, model edits via file tools, harness re-syncs the edited file into the next call. Model is swappable; the CLM eval suite (doc 05 §5) runs against whichever model is configured. Removes model-procurement blocker; adds harness sync/partition work. Detail: doc 05 §6. |
| D7 | Gate authority matrix | **Provided by QnA initially** — authority is captured through a structured Q&A (org/mission setup questionnaire), not hand-authored config | We design a Gate Authority QnA: at org onboarding and per mission risk tier, answers (roles, named people/delegates, dual-control thresholds, SLA/escalation) generate the authority matrix, which a named admin confirms before first gate fires. Changes after that are versioned config changes (PR/approval), not chat edits. Detail: doc 03 §4. |
| D8 | Data/compliance | **Not in first cut** | No residency/model-allowlist/retention constraints designed in v1 beyond baseline hygiene already in the blueprint (secret scanning, no secrets in context, least-privilege tools). Explicitly recorded as accepted risk; revisit before any regulated workload or production data is connected. |
| D9 | Manual baseline | **No baseline initially** — build reporting now, compare gradually against past reports as they accumulate | Leverage reporting starts as *descriptive* (first-pass rate, rework, cost, cycle time per stage) with no AI-vs-manual claim. From cycle 1, every report is archived versioned; trend-vs-past-reports becomes the comparison once ≥2–3 reporting periods exist. AI-off drill missions (doc 08) are still run for takeover readiness, and may later serve as a quasi-control — not claimed as one yet. Definitions updated: doc 07. |

### Resolved / remaining open
- ✅ Q-OPEN-1 → D5 (Jira/Confluence/Git + own UI) · ✅ Q-OPEN-2 → D6 (emulated CLM) · ✅ Q-OPEN-3 → D7 (QnA-seeded) · ✅ Q-OPEN-4 → D8 (deferred, accepted risk) · ✅ Q-OPEN-5 → D9 (no baseline; trends vs past reports)
- Still open (non-blocking for skeleton): exact Jira project/issue-type mapping & Confluence space/template mapping (discovery task in implementation plan, doc 09 §4); Git host specifics (GitHub/GitLab/Bitbucket — adapter is host-agnostic, webhook dialects differ); IdP for sign-off identity (assumed SSO/OIDC in org UI — confirm at skeleton kickoff).

## Round 3 decisions — walking-skeleton discovery & spikes (2026-10-18)

| # | Question | Decision | Implication |
|---|---|---|---|
| D10 | Skill container egress / model endpoint (discovery items 4, 8) | Allowlist **both** GitHub model endpoints in the skill container network policy: primary `api.githubcopilot.com` (matches the "Copilot-provided models" choice), fallback `models.github.ai`; deny-by-default otherwise. File: `pilot/sandbox/network-policy.yaml` | Egress is versioned policy edited by review (G9-class), never by skills. Platform allowlists (Arena sandbox, CI) must be synced to it — trial-001 evidence records the current gap. |
| D11 | Per-run budget (discovery item 6) | Per-run envelope in `pilot/sandbox/budget-policy.yaml`: default 120k tokens / 4 USD notional / 30 min / 24 model calls (doc 01 §4.1 shape), plus heavy / CLM-emulation / model-trial envelopes. Hard stop **parks the run** (doc 05 circuit-breaker); notional USD pricing recorded even for subscription-metered Copilot models | One envelope aggregates all model calls, CLM re-sends and retries per run; per-skill ceilings (doc 02) bind in addition; cost ledger keeps doc 07 metrics provider-comparable. |
| D12 | S1 graph-extraction & impact spike go/no-go (doc 12 §2) | **PASS — go** ([verdict](spikes/s1-graph-extraction.md)): FS-014 change flags exactly {HLD comp, ADR, unit, test evidence}, zero signed-node false positives on the fixture set | Nested node model + typed edges + impact_preview stand as designed (doc 10); no simplification re-spike. B3 may proceed after S3 per spike order. |

Full question bank (50, grouped A–E): doc 01 §11.
