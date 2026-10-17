# 12a — Discovery Checklist Status (Doc 12 §5)

Status of the kickoff discovery checklist from [doc 12 §5](12-walking-skeleton-plan.md#5-discovery-checklist-kickoff-before-s1), as of 2026-10-17.
Doc 12 itself is not edited here; this file tracks what is verified, what is partial, and what is blocked on a named human.

Legend: ✅ verified from repo/GitHub · 🟡 partly verified, rest needs a decision · ⛔ blocked on human input or access this session does not have

## Checklist

| # | Item (doc 12 §5) | Status | Evidence / notes | Needed to close |
|---|---|---|---|---|
| 1 | Pilot mission selected (real or fixture) + named gate humans per role | 🟡 | **Decision:** the doc 12 §3 fallback fixture *"Idempotent order submission with partial fulfilment"* (FS-014 family, doc 10) is the pilot mission. Still open: named humans for G0–G7, and writing the fixture as full templates (needs the pilot Confluence space, item 3). | Named humans for G0–G7. Fixture templates once Confluence access exists. |
| 2 | Jira: project key, issue types (Mission/Unit), transitions for gates, webhook/API access, service account | ⛔ | The Jira connector is not available in Arena, so nothing can be verified from this session. | Jira admin to supply project key, issue types, transition names, webhook/API access, and a service account. |
| 3 | Confluence: space key, template page IDs (doc 04 loaded), API access, version/history availability | ⛔ | The Confluence connector is not available in Arena. Version/history capture is also S3's job (doc 12 §2), so it must be proven by spike, not assumed. | Confluence admin to supply space key, template page IDs, and API access. S3 confirms version/hash capture. |
| 4 | Git: host, pilot repo, branch protection + CODEOWNERS, ledger repo created | 🟡 | **Host: GitHub** (`Asiant/factory`; `gh` authenticated). **Pilot repo:** this repo (`Asiant/factory`) for the pilot is assumed, to be confirmed. **Branch protection on `main`:** cannot be read with the session token (HTTP 403); repo rulesets are empty. **CODEOWNERS:** no file exists in the repo. **Ledger repo:** requested as public `Asiant/factory-ledger`, but creation failed: the session token returns HTTP 403 on repo creation, and no such repo exists. | Create `Asiant/factory-ledger` through an account with repo-creation rights (or grant the token that scope). Confirm the pilot repo. Confirm branch protection on `main` through an admin. Decide CODEOWNERS owners. |
| 5 | IdP: SSO/OIDC app for UI + Jira identity mapping for approvers | ⛔ | No IdP tenant or OIDC client is available in this session. | Identity admin to supply the IdP and an OIDC app for the UI, plus the Jira user mapping for approvers. |
| 6 | Model access: API model for emulated CLM + skills; per-run budget limits | ⛔ | The model is not selected and no budget is set. Doc 05 emulated CLM and doc 12 S2 assume an API model. | Decision: which API model, and per-run budget envelope. Keys go through the org secret store, never into the repo or chat. |
| 7 | Authority QnA (doc 03 §4) run for the pilot team; matrix confirmed by a named admin | ⛔ | Not started. This needs a named org admin and cannot be done by an agent. | Named org admin runs the ~15-question org QnA plus the per-mission addendum. Output: `authority-matrix.yaml`. |
| 8 | Sandbox: where skills run code (CI runner/container), network/tool allowlist | 🟡 | **Current sandbox outbound allowlist:** `github.com`, `codeload.github.com`, `api.github.com`, `registry.npmjs.org`, `pypi.org`, `files.pythonhosted.org`. **Not on the list:** Jira, Confluence, the IdP, and any model API host. | Decide where skills run (CI runner vs container). Add allowlist entries for Jira, Confluence, IdP, and model API hosts. |

## Pre-S1 gaps this surfaced

- **Empty PR risk:** the blueprint content is already on `main` (signed commit `9f03866`, merged via PR #1 from `arena/fbd51a57-factory`). A PR from this branch to `main` has no content diff.
- **Ledger repo:** doc 12 §1 requires one ledger repo. Creation was requested (public, `Asiant/factory-ledger`) but failed with HTTP 403; it still needs to be created.
- **Branch protection:** unverified. Doc 08 relies on Git-only ledger gates, so protection on `main` (and on the ledger repo) matters.

## Next actions

1. Human decisions: named gate humans (item 1), CODEOWNERS owners (item 4), model and budget (item 6), and the sandbox runner choice (item 8).
2. Access or admin confirmation for items 2, 3, 5, and 7.
3. Once item 1 is decided, S1 (graph extraction) can start on the chosen fixture. S3 (gate hash-capture) needs item 2 and item 3 access.
