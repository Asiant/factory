# 12a — Discovery Checklist Status (Doc 12 §5)

Status of the kickoff discovery checklist from [doc 12 §5](12-walking-skeleton-plan.md#5-discovery-checklist-kickoff-before-s1), updated 2026-10-18.
Doc 12 itself is not edited here; this file tracks what is verified, what is decided, and what is still open.

Legend: ✅ done · 🟡 partly done, rest open · ⛔ blocked on access or a missing input

## Decisions recorded

| Decision | Choice | Scope |
|---|---|---|
| Pilot mission | Fallback fixture *"Idempotent order submission with partial fulfilment"* (FS-014 family, doc 10) | Pilot |
| Gate humans G0–G7 | Test setup: the repo owner (GitHub `@Asiant`). Real project: named person per role, TBD | Test now; real TBD |
| CODEOWNERS owner | Test setup: `@Asiant` (`.github/CODEOWNERS`, `* @Asiant`). Real project: named person, TBD | Test now; real TBD |
| Model for emulated CLM + skills | GitHub Copilot-provided models (to try first) | Test |
| Skill execution | Containers | Pilot |
| Ledger repo `Asiant/factory-ledger` | Created by `@Asiant` (not by the agent) | Pilot |
| Model endpoint in skill network policy | **Primary `api.githubcopilot.com`** (matches the "Copilot-provided models" choice), **fallback `models.github.ai`** — both allowlisted in `pilot/sandbox/network-policy.yaml` (2026-10-18) | Test |
| Per-run budget envelope | `pilot/sandbox/budget-policy.yaml`: default run 120k tokens / 4 USD notional / 30 min / 24 model calls (doc 01 §4.1 shape), heavy/clm/trial envelopes, circuit-breaker parks over-budget runs (doc 05). Per-skill ceilings in doc 02 bind in addition | Test |
| S1 graph-extraction spike | **PASS — go** ([verdict](spikes/s1-graph-extraction.md)); fixture written as full doc-04 templates in `pilot/fixture/` | Pilot |

## Checklist

| # | Item (doc 12 §5) | Status | Evidence / notes | Still open |
|---|---|---|---|---|
| 1 | Pilot mission selected (real or fixture) + named gate humans per role | 🟡 | Fixture chosen and **now written as full doc-04 templates in Git** (`pilot/fixture/`, doc 08 fallback home): mission, FS-NFS@v3 (8 FS + 3 NFS), HLD@v2, KDD-002, ADR-014, U1–U3, LLD-U3, tests, verification, annotated code symbol. Gate humans set for the test setup only. | Named humans for G0–G7 in the real project. Confluence copy of the fixture when item 3 lands. |
| 2 | Jira: project key, issue types (Mission/Unit), transitions for gates, webhook/API access, service account | ⛔ | The Jira connector is not available in Arena, so nothing can be verified from this session. | Jira admin to supply project key, issue types, transition names, webhook/API access, and a service account. |
| 3 | Confluence: space key, template page IDs (doc 04 loaded), API access, version/history availability | ⛔ | The Confluence connector is not available in Arena. Version/history capture is S3's job (doc 12 §2) and must be proven by spike. | Confluence admin to supply space key, template page IDs, and API access. |
| 4 | Git: host, pilot repo, branch protection + CODEOWNERS, ledger repo created | 🟡 | **Host: GitHub.** **CODEOWNERS:** `* @Asiant` (test setup). **Ledger repo:** `Asiant/factory-ledger` created by `@Asiant` (user-attested; the session token gets 403 outside `Asiant/factory`, so the agent cannot read it). **Branch protection on `main`:** user-attested enabled. Agent-visible evidence: repo ruleset `main` (id 25333140, created 2026-10-18T06:01Z, deletion + non-fast-forward + pull-request rules) but `enforcement: disabled` and `require_code_owner_review: false`; classic branch-protection API is 403 for the session token. | Confirm the active mechanism and that **code-owner review is required** (otherwise CODEOWNERS is cosmetic). Note the test-setup deadlock: CODEOWNERS owner = PR author = `@Asiant`, and GitHub blocks author self-approval — decide the G7 test merge flow (second reviewer account, or a service account as PR author). |
| 5 | IdP: SSO/OIDC app for UI + Jira identity mapping for approvers | ⛔ | No IdP tenant or OIDC client is available in this session. | Identity admin to supply the IdP and an OIDC app for the UI, plus the Jira user mapping for approvers. |
| 6 | Model access: API model for emulated CLM + skills; per-run budget limits | 🟡 | **Model endpoint allowlisted** in the skill container network policy (see decision above). **First model trials run** (records in `pilot/model-trial/trials/`, no credentials recorded): trial-000 mock self-test green · trial-001 from the Arena sandbox → `network_blocked` (platform egress allowlist, TLS EOF) · trial-002 from a GitHub-hosted runner → exposed a harness env-name bug + `models.github.ai` stub `200 OK` bodies · trial-003 → **`api.githubcopilot.com` is reachable from the CI host** and rejects the run-scoped Actions installation token: *"the Copilot-Integration-Id header does not match the GitHub App that issued this installation access token"* · trial-004 (harness v2) → **`verdict: auth_rejected`** conclusive: same rejection for both `Copilot-Integration-Id` variants tried; `models.github.ai` serves only stub `200 OK` bodies (`invalid-response`, not counted as a trial). **Budget: set** (see decision above). | A completion trial needs a **Copilot-capable key in the org secret store** (injected as `FACTORY_MODEL_API_TOKEN`) and its matching `Copilot-Integration-Id`; then re-run `model_trial.py --require-ok`. Also sync the Arena sandbox egress allowlist with `pilot/sandbox/network-policy.yaml` so in-sandbox trials can reach the endpoint. |
| 7 | Authority QnA (doc 03 §4) run for the pilot team; matrix confirmed by a named admin | ⛔ | Not started. The test setup has one human (`@Asiant`) in every gate role, so the QnA can be simplified for the test. | Named org admin runs the org QnA and the per-mission addendum for the real project. Output: `authority-matrix.yaml`. |
| 8 | Sandbox: where skills run code (CI runner/container), network/tool allowlist | 🟡 | **Decided:** containers. **Network policy + tool allowlist defined:** `pilot/sandbox/network-policy.yaml` (deny-by-default egress; code-host/package-registry/model-endpoint classes; graph-tools/git/http/package-install/model-call allowed). CI runner path proven for model trials (trial-003/004). | Pin the container image (TBD in the policy file, needed before B5). Add Jira/Confluence/IdP hosts when items 2/3/5 land. Arena sandbox egress must be synced to the policy (trial-001 evidence). |

## Next actions

1. Org secret store: add a Copilot-capable key (`FACTORY_MODEL_API_TOKEN`) + its `Copilot-Integration-Id`; re-run the model trial to a `verdict: ok` completion (item 6). Sync the Arena sandbox egress allowlist with the network policy.
2. `@Asiant`: confirm branch protection on `main` enforces **code-owner review** (ruleset `main` currently reads `enforcement: disabled`, `require_code_owner_review: false`) and decide the G7 test merge flow given the author-self-approval deadlock (item 4).
3. S3 (gate hash-capture) is next in the spike order; it needs items 2 and 3 (Jira + Confluence). S2 (emulated CLM) can be prepared but its spike wants the model completion from action 1.
4. B3 (graph service) may start after S1 + S3 per doc 12 §2 spike order — S1 verdict is go.
5. Jira, Confluence, IdP, and the authority QnA wait on access or a named admin (items 2, 3, 5, 7).
6. Pin the skill container image (item 8) before B5 (skills runtime).
