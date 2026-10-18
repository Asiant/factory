# Pilot fixture — "Idempotent order submission with partial fulfilment"

Fallback fixture for the walking skeleton (doc 12 §3), FS-014 family from
doc 10. Written as **full doc-04 templates** in Git markdown: this is the
doc-08 Git-home fallback until the pilot Confluence space exists (discovery
item 3), and the S1 graph-extraction spike runs against exactly these files.

| File | Artifact node | Gate state in fixture |
|---|---|---|
| `mission.md` | MISSION-003 | signed (G0) |
| `fs-nfs.md` | FS-NFS@v3 — §2 Ordering (FS-014, FS-015), §3 (FS-016/020/021/022), §5 (FS-017/018/019), §4/§6/§7 (NFS-007/011/013) | signed (G1) |
| `hld.md` | HLD@v2 — C-1..C-4, coverage matrix | signed (G2) |
| `kdd-002.md` | KDD-002 partial-fulfilment policy | signed (G3) |
| `adr-014.md` | ADR-014 idempotency design | accepted (G4) |
| `u1.md`, `u2.md`, `u3.md` | U1..U3 (+ acceptance criteria AC-*) | signed (G5) |
| `lld-u3.md` | LLD-U3@v1 — API-OP-09 | signed (G6) |
| `tests.md` | TESTS-001 — TEST-220, TEST-221 | signed (evidence) |
| `verification-u3.md` | VER-U3 | signed |
| `code/order_service.py` | code symbol `OrderService.submit()` | external |

Deliberate shape (S1 oracle): FS-014's declared neighbourhood is exactly
`C-3 (covers)`, `U3 (covers)`, `AC-U3-1 (derives_from)`, `TEST-221 (verifies)`,
with `ADR-014` reachable via `C-3.decided_by` and the implementation lane
`API-OP-09 → OrderService.submit()` via `implements`. Everything else
(FS-015 family, NFS-*, KDD-002, U1/U2, TEST-220, C-1/C-2/C-4) is the
false-positive control set: signed, and must NOT be flagged when FS-014
changes.
