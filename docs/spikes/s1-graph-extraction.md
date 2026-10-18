# Spike S1 — Graph extraction & impact: verdict

**Date:** 2026-10-18 · **Timebox:** doc 12 §2 allows 3–4 days; executed in one
working session against the fallback fixture · **Verdict: PASS — go** (B3 may
proceed after S3; spike order in doc 12 §2 unchanged).

## Pass criterion (doc 12 §2) → result

| Criterion | Result |
|---|---|
| Changing pilot FS-014 flags **exactly** {HLD comp, ADR, unit, test evidence} | ✅ flags = exactly `C-3` (HLD comp), `ADR-014` (ADR), `U3` (unit), `AC-U3-1` + `TEST-221` (test evidence) — see case A |
| Zero signed-node false positives on the fixture set | ✅ case A set-equality (no other node flagged at all), case C control run flags only the FS-015 family, full-node sweep: every flag carries a declared/parsed justification ≤2 hops (case D) |

Run: `.venv/bin/python spikes/s1-graph-extraction/run_s1.py` — 16/16 checks,
exit 0. One bug found and fixed by the assertions (the `derives_from` reverse
rule was unreachable in the dispatch table) — the expected-set assertion
caught it before any verdict was written.

## What was built (throwaway per doc 12 §2; production version is B3)

- **Fixture** `pilot/fixture/` — the doc 12 §3 fallback mission *"Idempotent
  order submission with partial fulfilment"* (FS-014 family, doc 10) written
  as **full doc-04 templates** in Git markdown (doc 08 fallback home until
  the pilot Confluence space exists, item 3): mission, FS-NFS@v3 (8 FS + 3
  NFS), HLD@v2 (C-1..C-4 + coverage matrix), KDD-002, ADR-014, U1–U3 (+ ACs),
  LLD-U3 (API-OP-09), TESTS-001 (TEST-220/221), VER-U3, annotated code
  symbol `OrderService.submit()`. This also advances discovery item 1.
- **Extractor** `spikes/s1-graph-extraction/extract.py` — front-matter +
  heading nesting + item link fields + HLD coverage matrix + `# graph:`
  code annotations → 178 nodes / 223 edges (containment from structure,
  typed edges declared; no inferred edges used).
- **Impact** `spikes/s1-graph-extraction/impact.py` — `impact_preview` per
  doc 10 §5: diff classification (editorial ⇒ no propagation), bounded
  reverse walk with per-edge behaviour, justification recorded on every
  entry, flags never driven by inferred edges.
- **Runner** `spikes/s1-graph-extraction/run_s1.py` — cases A–D + trace
  exhibits; JSON outputs under `out/` (gitignored).

## Impact rules as implemented (spike decisions)

| Edge (reverse hit) | Behaviour | Class |
|---|---|---|
| `covers` / `satisfies` / `depends_on` / `contradicts` | dependent requires review, status stale | **REQUIRES_REVIEW** (flag) |
| `verifies` | "item change ⇒ evidence expired" | **EVIDENCE_EXPIRED** (flag) |
| `derives_from` from acceptance criteria / tests | verification-evidence flavour of "dependent requires review" | **EVIDENCE_EXPIRED** (flag) |
| `derives_from` (other) | "source change ⇒ dependent requires review" | **REQUIRES_REVIEW** (flag) |
| `decided_by` (rev = decision changing) | dependents of a decision flagged | **REQUIRES_REVIEW** (flag) |
| decision-context rule (the doc's "(decided_by C-3 context)") | a flagged node's `decided_by` targets get flagged — the decision's context may no longer fit | **REQUIRES_REVIEW** (flag) |
| `implements` closure into code/LLD lane (≤2 hops) | "implementation suspect, not auto-edited" | **SUSPECT** (annotation) |
| `contains` ancestors | summary/status regeneration queued (auto, doc 10 §5 auto-update policy) | **ROLLUP** (annotation) |
| `relates_to` / `supersedes` | "notification only, never staleness" | **NOTIFY** (annotation) |

**Interpretation recorded here (the normative call for B3):** the pass
criterion's four classes are the *flag* classes — owner-actionable, gate
blocking. ROLLUP (auto projection refresh on ancestors) and SUSPECT (code
lane) and NOTIFY are *annotations*, never gates. This matches doc 10 §5
("relates_to: notification only"; "code node is suspect, not auto-edited";
derived projections always auto-update) and keeps "flags exactly
{…}" decidable.

## Cases

| Case | Change | Flags | Annotations |
|---|---|---|---|
| A | FS-014 statement (semantic) | `C-3` RR, `ADR-014` RR (decision-context via C-3), `U3` RR, `AC-U3-1` EE, `TEST-221` EE — buckets exactly {hld-comp, adr, unit, test-evidence} | ROLLUP `FS-NFS#s2-ordering`, `FS-NFS`, `MISSION-003`; SUSPECT `API-OP-09`, `OrderService.submit()` |
| B | FS-014 prose typo (editorial) | none | none |
| C | FS-015 statement (control) | `C-2` RR, `U2` RR, `KDD-002` RR (decision-context via U2), `AC-U2-1` EE, `TEST-220` EE — zero FS-014-family leakage | ROLLUP ancestors |
| D | every node changed (sweep) | 0 unjustified flags: all flags declared/parsed-driven, justification path ≤2 hops | — |

Trace exhibits (doc 10 §3, B3 acceptance preview): `trace(FS-014 → test)`
resolves via the declared graph (`FS-014 —verifies— TEST-221`), and the
design/implementation chain `FS-014 —covers— C-3 —implements— API-OP-09
—implements— OrderService.submit() —verifies— TEST-221` is walkable end to
end.

## Limits & follow-ups

- Confluence-export variant of the parser not exercised (needs item 3); the
  Git-markdown path is the doc 08 fallback and covers the same templates.
- Inferred edges are plumbed (`source` + "ignored inferred" note) but not
  produced — expected: they must never drive gates anyway (doc 10 §2).
- Diff classification is rules-only; S2's AI-check classification is a
  superset, not a change to the propagation rules.
- Node/edge store is in-memory dicts; B3's relational adjacency store,
  `get_context_for_task`, summaries S0/S1 and coverage_report are explicitly
  out of S1 scope.
- Relational/ontology config (doc 10 §6) still versioned-as-config work for B3.

## Go/no-go

**GO** on the S1 outcome: the nested node model + typed edges +
impact_preview reproduce the doc 10 §5 worked example exactly, with zero
signed-node false positives on the fixture set. No redesign of the node model
needed (the "if it fails" branch — fewer edge types / coarser granularity —
is not triggered). Proceed per doc 12 §2 spike order (S3 verdict next; S2
afterwards), B3 after both.
