from __future__ import annotations

from dataclasses import dataclass

from cwr_tool.generation.control_records import GRHRecord, GRTRecord
from cwr_tool.generation.records import CountableRecord, RenderableRecord


@dataclass(frozen=True, slots=True)
class GroupResult:
    """Rendered group output plus derived counts for totals."""

    records: list[RenderableRecord]  # GRH + body + GRT
    txcount: int
    reccount: int
    line_count: int  # physical lines in this group including GRH/GRT


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
        return len(self.records)


def sum_counts(transactions: list[Transaction]) -> tuple[int, int]:
    tx = sum(t.txcount() for t in transactions)
    rec = sum(t.reccount() for t in transactions)
    return tx, rec


class GroupBuilder:
    """Build GRH + body + GRT and compute counts for a group."""

    @staticmethod
    def build(
        *,
        group_number: int,
        group_type: str,
        transactions: list[Transaction],
    ) -> GroupResult:
        txcount, reccount = sum_counts(transactions)

        body_records: list[RenderableRecord] = []
        for t in transactions:
            # Transaction records are renderable; emit them as body lines.
            body_records.extend(t.records)

        group_records: list[RenderableRecord] = [
            GRHRecord(group=group_number, type_=group_type),
            *body_records,
            GRTRecord(group=group_number, txcount=txcount, reccount=reccount),
        ]

        line_count = 2 + reccount  # GRH + body + GRT

        return GroupResult(
            records=group_records,
            txcount=txcount,
            reccount=reccount,
            line_count=line_count,
        )
