"""Order Service submission slice (fixture code node source).

The graph extractor reads `# graph:` annotations (doc 10 §6: "code
annotations") to create code-symbol nodes and `implements` edges. This file
stands in for the real module the skeleton builds in B8.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
from typing import Dict, Optional, Tuple


@dataclass
class Order:
    id: str
    payload_hash: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class DedupStore:
    """idempotency_keys table (24h TTL) per ADR-014."""

    def __init__(self) -> None:
        self._rows: Dict[str, Tuple[str, str]] = {}

    def lookup(self, key: str) -> Optional[Tuple[str, str]]:
        return self._rows.get(key)

    def put(self, key: str, order_id: str, payload_hash: str) -> None:
        self._rows[key] = (order_id, payload_hash)


class IdempotencyConflict(Exception):
    """Same key, different payload (ADR-014: 409)."""


# graph: symbol OrderService.submit() implements API-OP-09
class OrderService:
    def __init__(self, dedup: DedupStore) -> None:
        self._dedup = dedup
        self._orders: Dict[str, Order] = {}
        self._seq = 0

    def submit(self, idempotency_key: str, payload: dict) -> str:
        """Submit an order; retry-safe per AC-U3-1 / AC-U3-2.

        201 path: first accepted submission. 200 path: replay returns the
        original order id. 409 path: key reuse with a different payload.
        """
        payload_hash = sha256(sorted(payload.items()).__repr__().encode()).hexdigest()
        existing = self._dedup.lookup(idempotency_key)
        if existing is not None:
            order_id, known_hash = existing
            if known_hash != payload_hash:
                raise IdempotencyConflict(idempotency_key)
            return order_id  # replay: original order id (FS-020)

        self._seq += 1
        order = Order(id=f"O-{self._seq}", payload_hash=payload_hash)
        self._orders[order.id] = order
        self._dedup.put(idempotency_key, order.id, payload_hash)
        return order.id
