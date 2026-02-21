from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

from cwr_tool.generation.control_records import GRHRecord, GRTRecord
from cwr_tool.generation.records import RenderableRecord
from cwr_tool.generation.transaction import Transaction, sum_counts


def _get_list(payload: dict[str, Any], key: str) -> list[Any]:
    value = payload.get(key)
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"'{key}' must be a list")
    return value


def _get_objects(payload: dict[str, Any], key: str) -> list[dict[str, Any]]:
    raw = _get_list(payload, key)
    out: list[dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, dict):
            raise ValueError(f"Each item in '{key}' must be an object")
        out.append(item)
    return out


BuildTransactions = Callable[[dict[str, Any]], list[Transaction]]


@dataclass(frozen=True, slots=True)
class GroupSpec:
    """
    Declarative group spec.

    - group_type: e.g. WRK, SPU
    - build_transactions(payload) returns transactions for that group.
      If empty, the group is omitted and group numbers stay compact.
    """

    group_type: str
    build_transactions: BuildTransactions


@dataclass(frozen=True, slots=True)
class BuiltGroup:
    """A group that exists in the final file (has transactions)."""

    group_number: int
    group_type: str
    transactions: list[Transaction]


def build_groups(payload: dict[str, Any], specs: Sequence[GroupSpec]) -> list[BuiltGroup]:
    """
    Build groups in the order of specs, assigning sequential group numbers
    only to groups that actually have transactions.
    """
    built: list[BuiltGroup] = []
    next_group_num = 1

    for spec in specs:
        txs = spec.build_transactions(payload)
        if not txs:
            continue

        built.append(
            BuiltGroup(
                group_number=next_group_num,
                group_type=spec.group_type,
                transactions=txs,
            )
        )
        next_group_num += 1

    return built


def render_group(
    *,
    group_number: int,
    group_type: str,
    transactions: list[Transaction],
) -> tuple[list[RenderableRecord], int, int]:
    """
    Render a group as:
      GRH
      <all transaction record lines>
      GRT

    Returns:
      (records, txcount, reccount)

    Note:
      - txcount/reccount are group totals excluding GRH/GRT (CWR convention)
      - reccount is based on Transaction.counts() (record-driven)
    """
    txcount, reccount = sum_counts(transactions)

    body_records: list[RenderableRecord] = []
    for t in transactions:
        body_records.extend(t.records)

    records: list[RenderableRecord] = [
        GRHRecord(group=group_number, type_=group_type),
        *body_records,
        GRTRecord(group=group_number, txcount=txcount, reccount=reccount),
    ]
    return records, txcount, reccount


def total_physical_line_count(groups: Sequence[BuiltGroup]) -> int:
    """
    Physical lines across groups INCLUDING GRH/GRT per group.
    For each group: GRH(1) + body(reccount) + GRT(1) = 2 + reccount
    """
    total = 0
    for g in groups:
        _tx, rec = sum_counts(g.transactions)
        total += 2 + rec
    return total
