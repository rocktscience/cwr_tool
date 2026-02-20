from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class CountableRecord(Protocol):
    def render(self) -> str: ...
    def counts(self) -> tuple[int, int]: ...


@dataclass(frozen=True, slots=True)
class Transaction:
    """A CWR transaction: 1 transaction, N record lines."""

    records: list[CountableRecord]

    def __post_init__(self) -> None:
        if not self.records:
            raise ValueError("Transaction must contain at least one record")

    def txcount(self) -> int:
        return 1

    def reccount(self) -> int:
        # physical record lines inside this transaction
        return len(self.records)


def sum_counts(transactions: list[Transaction]) -> tuple[int, int]:
    tx = sum(t.txcount() for t in transactions)
    rec = sum(t.reccount() for t in transactions)
    return tx, rec
