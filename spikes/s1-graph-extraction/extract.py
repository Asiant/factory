"""S1 spike — graph extraction from doc-04 template markdown.

Parser for Confluence-export/Git markdown pilot artifacts → nodes/edges
(doc 12 §2 spike S1). Extraction sources, per doc 10 §6:

  * front-matter            → artifact/decision/delivery nodes + declared links
  * heading nesting         → container `contains` edges (parsed structural)
  * item link fields        → declared typed edges (covers/derives_from/...)
  * HLD coverage matrix     → declared `covers` edges
  * `# graph:` annotations  → code-symbol nodes + `implements` edges

Throwaway-grade spike code (doc 12 §2); the production pipeline is B3.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

LINK_FIELDS = {
    "derives_from": "derives_from",
    "covers": "covers",
    "satisfies": "covers",
    "decided_by": "decided_by",
    "depends_on": "depends_on",
    "implements": "implements",
    "verifies": "verifies",
    "contradicts": "contradicts",
    "supersedes": "supersedes",
    "relates_to": "relates_to",
    "compliance-with": "relates_to",  # ADR→KDD compliance is informational
}

ITEM_HEADING_RE = re.compile(r"^###\s+([A-Z][A-Z0-9-]*\d[A-Z0-9-]*)\s*(?:[—–-]\s*(.*))?$")
FIELD_RE = re.compile(r"^([A-Za-z][\w-]*):\s*(.*)$")
LIST_RE = re.compile(r"^\[(.*)\]$")
CODE_ANNOTATION_RE = re.compile(r"^#\s*graph:\s*symbol\s+(\S+)\s+implements\s+(\S+)\s*$")

# node kind by id prefix (doc 10 §1 table)
ID_KIND_RULES = [
    (re.compile(r"^MISSION-"), ("container", "mission")),
    (re.compile(r"^FS-NFS$"), ("container", "fs-nfs")),
    (re.compile(r"^HLD$"), ("container", "hld")),
    (re.compile(r"^KDD-"), ("decision", "kdd")),
    (re.compile(r"^ADR-"), ("decision", "adr")),
    (re.compile(r"^U\d"), ("delivery", "unit")),
    (re.compile(r"^LLD-"), ("delivery", "lld")),
    (re.compile(r"^TESTS-"), ("delivery", "test-plan")),
    (re.compile(r"^VER-"), ("delivery", "verification-report")),
    (re.compile(r"^FS-"), ("item", "requirement")),
    (re.compile(r"^NFS-"), ("item", "requirement")),
    (re.compile(r"^AC-"), ("item", "acceptance-criterion")),
    (re.compile(r"^C-"), ("design", "component")),
    (re.compile(r"^API-OP-"), ("design", "api-operation")),
    (re.compile(r"^TEST-"), ("delivery", "test")),
]


@dataclass
class Node:
    id: str
    type: str
    kind: str
    title: str
    artifact: str
    status: str = "draft"
    version: int = 1
    fields: dict = field(default_factory=dict)
    source_file: str = ""
    content_hash: str = ""
    address: str = ""

    def to_dict(self) -> dict:
        return self.__dict__.copy()


@dataclass
class Edge:
    type: str
    frm: str
    to: str
    source: str  # declared | parsed | inferred
    at_hash: str = ""

    def key(self) -> tuple:
        return (self.type, self.frm, self.to)

    def to_dict(self) -> dict:
        return self.__dict__.copy()


def classify_id(node_id: str) -> tuple[str, str]:
    for pattern, (ntype, kind) in ID_KIND_RULES:
        if pattern.match(node_id):
            return ntype, kind
    return "item", "unknown"


def slug(text: str) -> str:
    text = text.replace("§", "s").strip().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


class Graph:
    def __init__(self) -> None:
        self.nodes: dict[str, Node] = {}
        self.edges: list[Edge] = []

    def add_node(self, node: Node) -> Node:
        if node.id in self.nodes:
            raise ValueError(f"duplicate node id {node.id}")
        self.nodes[node.id] = node
        return node

    def add_edge(self, type_: str, frm: str, to: str, source: str, at_hash: str = "") -> None:
        edge = Edge(type_, frm, to, source, at_hash)
        if edge.key() not in {e.key() for e in self.edges}:
            self.edges.append(edge)

    def edges_into(self, node_id: str) -> list[Edge]:
        return [e for e in self.edges if e.to == node_id]

    def edges_from(self, node_id: str) -> list[Edge]:
        return [e for e in self.edges if e.frm == node_id]

    def to_dict(self) -> dict:
        return {
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": [e.to_dict() for e in self.edges],
        }


def _parse_list(value: str) -> list[str]:
    match = LIST_RE.match(value.strip())
    if not match:
        return []
    return [item.strip() for item in match.group(1).split(",") if item.strip()]


def _content_hash(text: str) -> str:
    normalized = "\n".join(line.rstrip() for line in text.splitlines() if line.strip())
    return "sha256:" + hashlib.sha256(normalized.encode()).hexdigest()[:16]


def extract_file(graph: Graph, path: Path, body_text: str, front: dict, body: str) -> None:
    artifact_id = front["id"]
    mission = front.get("mission", artifact_id)
    at_hash = _content_hash(body_text)
    ntype, kind = classify_id(artifact_id)
    artifact = graph.add_node(Node(
        id=artifact_id, type=ntype, kind=kind,
        title=body.splitlines()[0].lstrip("# ").strip() if body else artifact_id,
        artifact=artifact_id, status=front.get("status", "draft"),
        version=int(front.get("version", 1)), source_file=str(path),
        content_hash=at_hash,
        address=f"mission://{mission}/{slug(artifact_id)}",
    ))
    if artifact_id != mission:
        graph.add_edge("contains", mission, artifact_id, "parsed", at_hash)
    for link_type, targets in (front.get("links") or {}).items():
        edge_type = LINK_FIELDS.get(link_type, link_type)
        for target in targets or []:
            graph.add_edge(edge_type, artifact_id, target, "declared", at_hash)

    current_section: Node | None = None
    current_item: Node | None = None
    in_fence = False
    in_matrix = False
    lines = body.splitlines()
    for line in lines:
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        heading2 = re.match(r"^##\s+(.*)$", line)
        if heading2:
            title = heading2.group(1).strip()
            current_section = graph.add_node(Node(
                id=f"{artifact_id}#{slug(title)}", type="container", kind="section",
                title=title, artifact=artifact_id, status=artifact.status,
                source_file=str(path), content_hash=_content_hash(title),
                address=f"mission://{mission}/{slug(artifact_id)}#{slug(title)}",
            ))
            graph.add_edge("contains", artifact_id, current_section.id, "parsed", at_hash)
            current_item = None
            in_matrix = "coverage matrix" in title.lower()
            continue

        heading3 = ITEM_HEADING_RE.match(line)
        if heading3:
            item_id, title = heading3.group(1), (heading3.group(2) or "").strip()
            ntype, kind = classify_id(item_id)
            parent = current_section or artifact
            current_item = graph.add_node(Node(
                id=item_id, type=ntype, kind=kind, title=title,
                artifact=artifact_id, status=artifact.status,
                source_file=str(path), content_hash=_content_hash(title),
                address=f"mission://{mission}/{slug(artifact_id)}#{item_id}",
            ))
            graph.add_edge("contains", parent.id, item_id, "parsed", at_hash)
            continue

        if in_matrix:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 2 and classify_id(cells[0])[1] != "unknown":
                for target in _parse_list(f"[{cells[1]}]"):
                    graph.add_edge("covers", cells[0], target, "declared", at_hash)
            continue

        field_match = FIELD_RE.match(line)
        if field_match:
            key, value = field_match.group(1), field_match.group(2).strip()
            target_node = current_item or artifact
            if key in LINK_FIELDS:
                edge_type = LINK_FIELDS[key]
                for dest in _parse_list(value):
                    graph.add_edge(edge_type, target_node.id, dest, "declared", at_hash)
            else:
                target_node.fields[key] = value


def extract_code_file(graph: Graph, path: Path, text: str) -> None:
    at_hash = _content_hash(text)
    for line in text.splitlines():
        match = CODE_ANNOTATION_RE.match(line.strip())
        if match:
            symbol, implements = match.group(1), match.group(2)
            if symbol not in graph.nodes:
                graph.add_node(Node(
                    id=symbol, type="external", kind="code-symbol", title=symbol,
                    artifact="", source_file=str(path), content_hash=at_hash,
                    address=f"code://{path.name}#{symbol}",
                ))
            graph.add_edge("implements", symbol, implements, "declared", at_hash)


def extract_fixture(fixture_dir: Path) -> Graph:
    graph = Graph()
    for path in sorted(fixture_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix == ".py":
            extract_code_file(graph, path, path.read_text())
            continue
        if path.suffix != ".md" or path.name == "README.md":
            continue
        text = path.read_text()
        if not text.startswith("---"):
            continue
        _, front_raw, body = text.split("---", 2)
        extract_file(graph, path, text, yaml.safe_load(front_raw) or {}, body.strip())
    return graph


def classify_change(old: Node, new: Node) -> str:
    """Diff classification (doc 10 §5 step 1) — rules-only spike version."""
    if old.status != new.status or old.version != new.version or old.title != new.title:
        return "semantic"
    if old.fields != new.fields:
        return "semantic"
    return "editorial"
