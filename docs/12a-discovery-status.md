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

## Checklist

| # | Item (doc 12 §5) | Status | Evidence / notes | Still open |
|---|---|---|---|---|
| 1 | Pilot mission selected (real or fixture) + named gate humans per role | 🟡 | Fixture chosen (see above). Gate humans set for the test setup only. | Named humans for G0–G7 in the real project. Fixture written as full templates needs the pilot Confluence space (item 3). |
| 2 | Jira: project key, issue types (Mission/Unit), transitions for gates, webhook/API access, service account | ⛔ | The Jira connector is not available in Arena, so nothing can be verified from this session. | Jira admin to supply project key, issue types, transition names, webhook/API access, and a service account. |
| 3 | Confluence: space key, template page IDs (doc 04 loaded), API access, version/history availability | ⛔ | The Confluence connector is not available in Arena. Version/history capture is S3's job (doc 12 §2) and must be proven by spike. | Confluence admin to supply space key, template page IDs, and API access. |
| 4 | Git: host, pilot repo, branch protection + CODEOWNERS, ledger repo created | 🟡 | **Host: GitHub.** **CODEOWNERS:** added on this branch, `* @Asiant` (test setup). It is not enforced until branch protection requires code-owner review. **Branch protection on `main`:** cannot be read with the session token (HTTP 403); repo rulesets are empty. **Pilot repo:** this repo (`Asiant/factory`) assumed, to be confirmed. **Ledger repo:** `Asiant/factory-ledger` to be created by `@Asiant`; the agent's token can't create repos. | Turn on branch protection and code-owner review for `main` (needs admin). Create `Asiant/factory-ledger`. Replace CODEOWNERS owner with the real person for the real project. |
| 5 | IdP: SSO/OIDC app for UI + Jira identity mapping for approvers | ⛔ | No IdP tenant or OIDC client is available in this session. | Identity admin to supply the IdP and an OIDC app for the UI, plus the Jira user mapping for approvers. |
| 6 | Model access: API model for emulated CLM + skills; per-run budget limits | 🟡 | **Model chosen:** Copilot-provided models. **Blocker:** from this sandbox, `api.githubcopilot.com` and `models.github.ai` are unreachable (outbound allowlist). **Budget:** not set. | Allow the Copilot model endpoint(s) from the skill sandbox (or run the trial from a host that can reach them). Set a per-run budget envelope. Keys go through the org secret store, never into the repo or chat. |
| 7 | Authority QnA (doc 03 §4) run for the pilot team; matrix confirmed by a named admin | ⛔ | Not started. The test setup has one human (`@Asiant`) in every gate role, so the QnA can be simplified for the test. | Named org admin runs the org QnA and the per-mission addendum for the real project. Output: `authority-matrix.yaml`. |
| 8 | Sandbox: where skills run code (CI runner/container), network/tool allowlist | 🟡 | **Decided:** containers. **Current sandbox outbound allowlist:** `github.com`, `codeload.github.com`, `api.github.com`, `registry.npmjs.org`, `pypi.org`, `files.pythonhosted.org`. | Add allowlist entries for the Copilot model endpoint(s) first, then Jira, Confluence, and the IdP once those exist. Define the container image and the network policy. |

## Next actions

1. Allow the Copilot model endpoint(s) in the skill container's network policy, then run the model trial (item 6).
2. `@Asiant` creates `Asiant/factory-ledger`.
3. `@Asiant` (or an admin) turns on branch protection and code-owner review for `main`.
4. Set the per-run budget (item 6).
5. Jira, Confluence, IdP, and the authority QnA wait on access or a named admin (items 2, 3, 5, 7).
6. S1 (graph extraction) can start on the fixture once the container setup exists. S3 (gate hash-capture) needs items 2 and 3.
