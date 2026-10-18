"""S1 spike — impact_preview: change propagation over the extracted graph.

Implements doc 10 §5: a semantic change to node X is classified, then a
bounded reverse walk over typed edges produces an impact set, each entry
classified. Spike decisions (recorded in docs/spikes/s1-graph-extraction.md):

  flags (need owner action, block gates):
    REQUIRES_REVIEW    rev covers/satisfies/depends_on/contradicts, and
                       rev derives_from on non-evidence nodes
                       ("dependent requires review", status=stale)
    EVIDENCE_EXPIRED   rev verifies, and rev derives_from from verification
                       evidence (acceptance criteria, tests)
                       ("item change ⇒ evidence expired")
  annotations (no owner action):
    ROLLUP             rev contains ancestors: summary/status regeneration
                       queued (auto — derived projections always auto-update)
    NOTIFY             rev relates_to / supersedes ("notification only")
    SUSPECT            implements closure into the code/implementation lane
                       ("design change ⇒ implementation suspect",
                        "code node is suspect, not auto-edited")
  decision-context rule (the doc's "(decided_by C-3 context)"):
    a flagged node's decided_by targets are flagged REQUIRES_REVIEW —
    the decision's context may no longer fit.

Inferred edges never drive flags (doc 10 §2). Editorial changes do not
propagate. Propagation creates staleness/proposals only — it never edits
signed nodes and never carries approvals across a change.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from extract import Graph

FLAG_CLASSES = ("EVIDENCE_EXPIRED", "REQUIRES_REVIEW")
ANNOTATION_CLASSES = ("ROLLUP", "NOTIFY", "SUSPECT")
DRIVING_SOURCES = ("declared", "parsed")
EVIDENCE_KINDS = ("acceptance-criterion", "test")

REVERSE_RULES = {
    "covers": "REQUIRES_REVIEW",
    "satisfies": "REQUIRES_REVIEW",
    "depends_on": "REQUIRES_REVIEW",
    "contradicts": "REQUIRES_REVIEW",
    "verifies": "EVIDENCE_EXPIRED",
    "derives_from": "REQUIRES_REVIEW",  # overridden to EVIDENCE_EXPIRED for evidence kinds below
    "decided_by": "REQUIRES_REVIEW",
    "implements": "SUSPECT",
    "contains": "ROLLUP",
    "relates_to": "NOTIFY",
    "supersedes": "NOTIFY",
}

# flag class beats annotation class; within flags, evidence expiry first
_CLASS_RANK = {"EVIDENCE_EXPIRED": 0, "REQUIRES_REVIEW": 1, "ROLLUP": 2, "NOTIFY": 3, "SUSPECT": 4}


@dataclass
class ImpactEntry:
    node: str
    node_kind: str
    node_type: str
    cls: str
    via: list = field(default_factory=list)  # edge dicts on the propagation path

    def to_dict(self) -> dict:
        return self.__dict__.copy()


@dataclass
class ImpactResult:
    changed: str
    change_kind: str
    entries: dict = field(default_factory=dict)  # node -> ImpactEntry
    notes: list = field(default_factory=list)

    def add(self, graph: Graph, node_id: str, cls: str, edge) -> None:
        node = graph.nodes.get(node_id)
        if node is None:
            raise ValueError(f"impact hit unknown node {node_id}")
        entry = self.entries.get(node_id)
        via = {"type": edge.type, "frm": edge.frm, "to": edge.to, "source": edge.source}
        if entry is None:
            self.entries[node_id] = ImpactEntry(
                node=node_id, node_kind=node.kind, node_type=node.type,
                cls=cls, via=[via],
            )
        else:
            entry.via.append(via)
            if _CLASS_RANK[cls] < _CLASS_RANK[entry.cls]:
                entry.cls = cls

    @property
    def flags(self) -> list[ImpactEntry]:
        return [e for e in self.entries.values() if e.cls in FLAG_CLASSES]

    @property
    def annotations(self) -> list[ImpactEntry]:
        return [e for e in self.entries.values() if e.cls in ANNOTATION_CLASSES]

    def flag_map(self) -> dict:
        return {e.node: e.cls for e in self.flags}

    def annotation_map(self) -> dict:
        out: dict = {}
        for e in self.annotations:
            out.setdefault(e.cls, []).append(e.node)
        return {k: sorted(v) for k, v in out.items()}

    def to_dict(self) -> dict:
        return {
            "changed": self.changed,
            "change_kind": self.change_kind,
            "flags": [e.to_dict() for e in sorted(self.flags, key=lambda e: e.node)],
            "annotations": [e.to_dict() for e in sorted(self.annotations, key=lambda e: e.node)],
            "notes": self.notes,
        }


def impact_preview(graph: Graph, node_id: str, change_kind: str = "semantic",
                   max_implements_depth: int = 2) -> ImpactResult:
    if node_id not in graph.nodes:
        raise ValueError(f"unknown node {node_id}")
    result = ImpactResult(changed=node_id, change_kind=change_kind)

    if change_kind == "editorial":
        result.notes.append("editorial change: no propagation (doc 10 §5 step 1)")
        return result

    # 1) reverse walk over typed edges into the changed node
    for edge in graph.edges_into(node_id):
        if edge.source not in DRIVING_SOURCES:
            result.notes.append(f"ignored inferred edge {edge.type} {edge.frm}->{edge.to}")
            continue
        cls = REVERSE_RULES.get(edge.type)
        if cls is None:
            continue
        if edge.type == "derives_from":
            kind = graph.nodes[edge.frm].kind
            cls = "EVIDENCE_EXPIRED" if kind in EVIDENCE_KINDS else "REQUIRES_REVIEW"
        result.add(graph, edge.frm, cls, edge)
        if edge.type == "contains":
            # rollup keeps walking up the containment chain (summaries)
            ancestor = edge.frm
            for _ in range(8):
                parents = [e for e in graph.edges_into(ancestor) if e.type == "contains"]
                if not parents:
                    break
                result.add(graph, parents[0].frm, "ROLLUP", parents[0])
                ancestor = parents[0].frm

    # 2) decision-context rule: flagged node's decided_by targets are flagged
    flagged_ids = [e.node for e in result.flags]
    for flagged in flagged_ids:
        for edge in graph.edges_from(flagged):
            if edge.type == "decided_by" and edge.source in DRIVING_SOURCES:
                result.add(graph, edge.to, "REQUIRES_REVIEW", edge)
                result.notes.append(f"decision-context rule fired for {edge.to} via {flagged}")

    # 3) suspect closure: implements chain into the implementation/code lane
    frontier = {node_id, *flagged_ids}
    for depth in range(max_implements_depth):
        next_frontier = set()
        for current in frontier:
            for edge in graph.edges_into(current):
                if edge.type == "implements" and edge.source in DRIVING_SOURCES:
                    result.add(graph, edge.frm, "SUSPECT", edge)
                    next_frontier.add(edge.frm)
        frontier = next_frontier
        if not frontier:
            break

    return result
