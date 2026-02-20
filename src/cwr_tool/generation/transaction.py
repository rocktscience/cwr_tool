from __future__ import annotations

from dataclasses import dataclass

from cwr_tool.generation.records import CountableRecord


@dataclass(frozen=True, slots=True)
class Transaction:
    """
    A CWR transaction: conceptually 1 transaction with N record lines.

    IMPORTANT:
    - Counts are computed from record.counts(), not from len(records).
    - This keeps behavior correct when some lines do NOT start a transaction (ALT/COM),
      or when future transaction rules get more complex.
    """

    records: list[CountableRecord]

    def __post_init__(self) -> None:
        if not self.records:
            raise ValueError("Transaction must contain at least one record")

    def counts(self) -> tuple[int, int]:
        """
        Return:
          (txcount, reccount)

        txcount = sum of per-record tx increments
        reccount = sum of per-record record-line increments
        """
        tx = 0
        rec = 0
        for r in self.records:
            dtx, drec = r.counts()
            tx += dtx
            rec += drec
        return tx, rec

    def txcount(self) -> int:
        return self.counts()[0]

    def reccount(self) -> int:
        return self.counts()[1]

    def render_lines(self) -> list[str]:
        return [r.render() for r in self.records]


def sum_counts(transactions: list[Transaction]) -> tuple[int, int]:
    tx = 0
    rec = 0
    for t in transactions:
        dtx, drec = t.counts()
        tx += dtx
        rec += drec
    return tx, rec
