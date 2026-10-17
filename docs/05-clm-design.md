# 05 — CLM Design (Meta-style Context Language Model)

Decision D1: the context system is a **Context Language Model** in the Meta/UW
sense — the model natively manages its own context, implemented by treating
context as a file the model edits (append, rewrite, delete, reorganise), with
each edit synchronised into the live context for the next turn; multiple
agents = multiple coexisting context files
([repo](https://github.com/facebookresearch/context-language-models),
[paper](https://arxiv.org/abs/2609.37725)).

## 1. Context file anatomy (per agent run / per mission thread)

```
context-file (synced to model each turn)
├── SEG-A  SYSTEM / CONSTITUTION      [harness-owned, READ-ONLY to model]
│          identity, contract, tool policy, gate rules, output schema
├── SEG-B  SIGNED TRUTH               [harness-injected, READ-ONLY to model]
│          signed mission brief, FS/NFS@hash, accepted KDD/ADR excerpts,
│          gate records — content-addressed, refreshed only by harness
│          after a gate event
├── SEG-C  WORKING CONTEXT            [CLM-EDITABLE — the CLM segment]
│          findings, hypotheses, plan, open questions, distilled tool
│          outputs, scratch reasoning pointers
└── SEG-D  WINDOW                     [harness-owned sliding window]
             recent turns/tool results not yet distilled into SEG-C
```

- The model edits **SEG-C only**, via file tools. Edits are diffs; every diff
  is logged (`context_edit` event: run_id, before/after hash, model rationale).
- SEG-B mutation is impossible at model layer (separate file/permission,
  harness concatenates segments at call time). This is our governance
  deviation from unrestricted CLM — flagged as eval question E-CLM-1.
- SEG-D overflow policy: harness nudges model to distil into SEG-C before
  truncation; truncations are events, never silent.

## 2. Lifecycle

1. **Compile** — harness assembles SEG-A/B/D + mission SEG-C seed from the
   artifact store; emits `context_manifest.yaml` (segment hashes, sources,
   token budgets). Manifest hash is recorded on every run.
2. **Run** — model works; SEG-C edits sync per turn (CLM mechanism).
   Snapshots taken at: run start, each gate submission, run end, and every
   N edits (configurable) → `snapshots/{run_id}/{seq}.md` + diffs.
3. **Promote** — facts in SEG-C are *claims*, not truth. At stage end, the
   producing agent's output artifact distils SEG-C; anything that must
   survive (decision, constraint, resolved question) must appear in the
   artifact or a proposed context-curation PR (Librarian agent A13).
   Unpromoted SEG-C content expires with the run.
4. **Share** — cross-agent context passes **only via artifacts and curated
   shared context**, never by one agent editing another's SEG-C. A parent
   agent may spawn a subagent with a seeded child context file (CLM
   multi-agent pattern), receiving back the child's artifact + SEG-C digest.

## 3. Safety & integrity controls

| Risk | Control |
|---|---|
| Model edits away an inconvenient instruction | SEG-A/B read-only; canary instructions in SEG-B checked per snapshot (eval + runtime probe) |
| Context poisoning via tool/web content | SEG-D quarantine tags; promotion requires artifact distillation + AI-check; external content never lands in SEG-B directly |
| Silent context drift over long missions | Snapshot diffs reviewable; Librarian audits SEG-C vs signed artifacts for contradictions (finding → gate pack) |
| Secret leakage into context file | Compile-time + edit-time secret scanning; context files inherit repo ACLs; redaction event if triggered |
| Cost blow-up from context churn | Per-segment token budgets in contract; edit-rate and context-size telemetry; budget circuit-breaker parks run |
| Non-reproducibility | manifest + snapshot hashes on every output; replay = same snapshot + agent/model version |

## 6. Emulated context-as-file runtime (Decision D6)

No CLM-native model in v1. The **harness emulates** the CLM mechanism on any
chat/tools API model:

```
loop per run:
  1. harness assembles context file (SEG-A..D, §1) -> workspace file ctx.md (+ ctx.manifest.yaml)
  2. model is instructed: ctx.md IS your working context; edit it with file
     tools (edit_ctx) whenever you learn, resolve, or discard something
  3. after each model turn, harness:
       - validates the ctx diff (SEG-A/B untouched? size budget? no secrets?)
       - snapshots the diff (context_edit event, §2)
       - builds the NEXT model call as: SEG-A + SEG-B (fresh, harness-owned)
         + edited SEG-C + SEG-D window  — i.e. the edited file becomes context
  4. on gate/tool events, harness refreshes SEG-B from signed artifacts only
```

Implementation notes for the skeleton:
- `edit_ctx` is a restricted tool: path-scoped to the run's SEG-C file only;
  SEG-A/B exist only in harness memory, never as model-writable files.
- Invalid edits (budget breach, secret detected, malformed) are rejected with
  a tool error the model can repair — counted in eval metric *edit validity*.
- Because emulation re-sends context per call, token cost is explicit in the
  cost ledger per run; the paper's FLOP savings do **not** automatically
  transfer — doc 05 §5.3 measures our real edit economy vs append-only.
- Model swap = config change (`model:` in agent registry override); the CLM
  eval suite must pass before a new model serves L2+ autonomy.

## 4. Model/runtime requirements (procurement checklist — superseded by D6: any tools-capable API model meeting these)

- [ ] Native or harness-emulated context-as-file sync per turn
- [ ] Deterministic snapshot/restore of context file
- [ ] Per-call segment-level logging (what exactly was sent)
- [ ] Data residency / no-training-on-data terms; local/self-host option
- [ ] Eval results on context-edit quality (E-CLM suite: retention of
      signed constraints, distillation fidelity, edit efficiency/FLOPs)

## 5. CLM eval suite (must exist before CLM is trusted at L2+)

1. **Constraint retention:** seed SEG-B with K signed constraints; long task;
   % still present & obeyed at end (target 100% for hard constraints).
2. **Distillation fidelity:** facts in tool outputs → SEG-C → artifact;
   human/LLM-rubric scored recall & hallucination rate.
3. **Edit economy:** edits/run, tokens saved vs append-only baseline
   (replicates the paper's FLOPs claim on *our* workloads).
4. **Poison resistance:** injected instruction in SEG-D; must not reach
   SEG-B/artifacts.
5. **Partition cost (E-CLM-1):** A/B partitioned vs unrestricted context on
   golden missions — quantifies what our governance deviation costs.
