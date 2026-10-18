#!/usr/bin/env python3
"""S1 spike runner — graph extraction & impact against the pass criterion
(doc 12 §2 spike S1):

  PASS if (1) changing pilot FS-014 flags exactly {HLD comp, ADR, unit, test
  evidence}, and (2) zero signed-node false positives on the fixture set.

Run:  .venv/bin/python spikes/s1-graph-extraction/run_s1.py
Exit: 0 = spike PASS (go), 1 = spike FAIL (stop for redesign, doc 12 §2).
"""

from __future__ import annotations

import json
import sys
from collections import deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from extract import classify_change, extract_fixture  # noqa: E402
from impact import impact_preview  # noqa: E402

REPO = HERE.parents[1]
FIXTURE = REPO / "pilot/fixture"
OUT = HERE / "out"

# ---- the S1 oracle (doc 10 §5 worked example) ------------------------------

KIND_TO_BUCKET = {
    "component": "hld-comp",
    "kdd": "adr",
    "adr": "adr",
    "unit": "unit",
    "acceptance-criterion": "test-evidence",
    "test": "test-evidence",
}

EXPECTED_A_FLAGS = {  # FS-014 semantic change
    "C-3": "REQUIRES_REVIEW",
    "ADR-014": "REQUIRES_REVIEW",
    "U3": "REQUIRES_REVIEW",
    "AC-U3-1": "EVIDENCE_EXPIRED",
    "TEST-221": "EVIDENCE_EXPIRED",
}
EXPECTED_A_BUCKETS = {"hld-comp", "adr", "unit", "test-evidence"}
EXPECTED_A_ROLLUP = ["FS-NFS", "FS-NFS#s2-ordering", "MISSION-003"]
EXPECTED_A_SUSPECT = ["API-OP-09", "OrderService.submit()"]

EXPECTED_C_FLAGS = {  # FS-015 semantic change (false-positive control run)
    "C-2": "REQUIRES_REVIEW",
    "U2": "REQUIRES_REVIEW",
    "KDD-002": "REQUIRES_REVIEW",  # decision-context rule via U2.decided_by
    "AC-U2-1": "EVIDENCE_EXPIRED",
    "TEST-220": "EVIDENCE_EXPIRED",
}
FS014_FAMILY = {
    "C-3", "ADR-014", "U3", "AC-U3-1", "AC-U3-2", "TEST-221",
    "API-OP-09", "OrderService.submit()",
}

SIGNED_EXPECTED = set(EXPECTED_A_FLAGS) | set(EXPECTED_C_FLAGS)

CHECKS: list[tuple[str, bool, str]] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    CHECKS.append((name, bool(cond), detail))


def find_path(graph, src: str, dst: str) -> list[str] | None:
    queue = deque([src])
    prev: dict[str, str | None] = {src: None}
    while queue:
        current = queue.popleft()
        if current == dst:
            path = []
            while current is not None:
                path.append(current)
                current = prev[current]
            return list(reversed(path))
        neighbours = set()
        for edge in graph.edges:
            if edge.frm == current:
                neighbours.add(edge.to)
            if edge.to == current:
                neighbours.add(edge.frm)
        for nxt in neighbours:
            if nxt not in prev:
                prev[nxt] = current
                queue.append(nxt)
    return None


def main() -> int:
    OUT.mkdir(exist_ok=True)
    graph = extract_fixture(FIXTURE)

    # ---- fixture sanity ----------------------------------------------------
    expected_nodes = (
        {"MISSION-003", "FS-NFS", "FS-NFS#s2-ordering", "HLD", "KDD-002", "ADR-014",
         "U1", "U2", "U3", "LLD-U3", "TESTS-001", "VER-U3"}
        | SIGNED_EXPECTED | FS014_FAMILY
        | {"FS-015", "FS-016", "NFS-007", "C-1", "C-4", "TEST-220"}
    )
    missing = sorted(expected_nodes - set(graph.nodes))
    check("fixture: all oracle nodes extracted", not missing, f"missing={missing}")
    unsigned = sorted(n for n in SIGNED_EXPECTED if graph.nodes[n].status != "signed") if not missing else []
    check("fixture: oracle nodes are signed", not unsigned, f"unsigned={unsigned}")
    check("fixture: extraction is non-trivial", len(graph.nodes) >= 25 and len(graph.edges) >= 40,
          f"nodes={len(graph.nodes)} edges={len(graph.edges)}")

    # ---- Case A: FS-014 semantic change ------------------------------------
    impact_a = impact_preview(graph, "FS-014", "semantic")
    got_a = impact_a.flag_map()
    check("A: flags == expected {C-3, ADR-014, U3, AC-U3-1, TEST-221}",
          got_a == EXPECTED_A_FLAGS, f"got={got_a}")
    buckets = {KIND_TO_BUCKET.get(graph.nodes[n].kind, graph.nodes[n].kind) for n in got_a}
    check("A: flag buckets == exactly {hld-comp, adr, unit, test-evidence}",
          buckets == EXPECTED_A_BUCKETS, f"buckets={sorted(buckets)}")
    annot = impact_a.annotation_map()
    check("A: ROLLUP == FS-014 ancestors", annot.get("ROLLUP") == EXPECTED_A_ROLLUP,
          f"got={annot.get('ROLLUP')}")
    check("A: SUSPECT == implementation lane {API-OP-09, OrderService.submit()}",
          annot.get("SUSPECT") == EXPECTED_A_SUSPECT, f"got={annot.get('SUSPECT')}")
    check("A: no NOTIFY (relates_to) noise on FS-014", "NOTIFY" not in annot, f"got={annot.get('NOTIFY')}")

    # ---- Case B: editorial change does not propagate -----------------------
    editorial = dict(graph.nodes["FS-014"].__dict__)
    editorial["content_hash"] = "sha256:typo-fix"
    probe = type(graph.nodes["FS-014"])(**editorial)
    kind_b = classify_change(graph.nodes["FS-014"], probe)
    impact_b = impact_preview(graph, "FS-014", kind_b)
    check("B: prose-only diff classifies as editorial", kind_b == "editorial", f"got={kind_b}")
    check("B: editorial change flags nothing", not impact_b.flags and not impact_b.annotations,
          f"got={impact_b.to_dict()}")

    # ---- Case C: FS-015 semantic change (control) --------------------------
    impact_c = impact_preview(graph, "FS-015", "semantic")
    got_c = impact_c.flag_map()
    check("C: flags == expected FS-015 family incl. KDD-002 via decision-context",
          got_c == EXPECTED_C_FLAGS, f"got={got_c}")
    check("C: zero cross-contamination into the FS-014 family",
          not (set(got_c) & FS014_FAMILY), f"leak={sorted(set(got_c) & FS014_FAMILY)}")

    # ---- Case D: sweep — zero unjustified flags on the fixture set ---------
    false_positives = []
    sweep_flags = 0
    for node_id in sorted(graph.nodes):
        sweep = impact_preview(graph, node_id, "semantic")
        for entry in sweep.flags:
            sweep_flags += 1
            for via in entry.via:
                if via["source"] not in ("declared", "parsed"):
                    false_positives.append((node_id, entry.node, "inferred-driven", via))
            path = find_path(graph, node_id, entry.node)
            if path is None or len(path) > 3:  # node + ≤2 propagation hops
                false_positives.append((node_id, entry.node, "no-justification-path", None))
    check("D: every flag on the fixture set has a declared/parsed justification ≤2 hops",
          not false_positives, f"false_positives={false_positives[:5]}")
    check("D: signed-node flags in the sweep are only ever justified (count>0 means exercised)",
          sweep_flags > 0, f"sweep_flags={sweep_flags}")

    # ---- bonus exhibit: walkable trace paths (doc 10 §3 / B3 acceptance) ---
    path_test = find_path(graph, "FS-014", "TEST-221")
    path_code = find_path(graph, "FS-014", "OrderService.submit()")
    check("trace(FS-014 -> test) finds a path", path_test is not None, f"path={path_test}")
    check("trace(FS-014 -> code symbol) finds a path", path_code is not None, f"path={path_code}")

    # ---- report ------------------------------------------------------------
    (OUT / "graph.json").write_text(json.dumps(graph.to_dict(), indent=2))
    (OUT / "impact-fs-014.json").write_text(json.dumps(impact_a.to_dict(), indent=2))
    (OUT / "impact-fs-015.json").write_text(json.dumps(impact_c.to_dict(), indent=2))

    print(f"fixture: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
    print(f"case A flags: {got_a}")
    print(f"case A annotations: {annot}")
    print(f"case C flags: {got_c}")
    print(f"case C annotations: {impact_c.annotation_map()}")
    print(f"trace exhibit FS-014 -> TEST-221: {' -> '.join(path_test or [])}")
    print(f"trace exhibit FS-014 -> code: {' -> '.join(path_code or [])}")
    print()
    failed = 0
    for name, ok, detail in CHECKS:
        mark = "PASS" if ok else "FAIL"
        if not ok:
            failed += 1
        print(f"[{mark}] {name}" + (f"  ({detail})" if detail and not ok else ""))
    verdict = "PASS" if failed == 0 else "FAIL"
    print(f"\nS1 verdict: {verdict} ({len(CHECKS) - failed}/{len(CHECKS)} checks)")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
