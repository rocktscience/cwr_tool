from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from cwr_tool.generation.control_records import GRHRecord, GRTRecord
from cwr_tool.generation.records import RenderableRecord
from cwr_tool.generation.transaction import Transaction, sum_counts


@dataclass(frozen=True, slots=True)
class GroupSpec:
    """
    Declarative definition of a group.

    - group_type: "WRK", "SPU", etc.
    - build_transactions: builds Transaction objects from the payload for this group
    """

    group_type: str
    build_transactions: Callable[[dict[str, Any]], list[Transaction]]


@dataclass(frozen=True, slots=True)
class BuiltGroup:
    group_number: int
    group_type: str
    transactions: list[Transaction]


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


def build_groups(payload: dict[str, Any], specs: list[GroupSpec]) -> list[BuiltGroup]:
    """
    Build all groups in order, assigning sequential group numbers only to groups that exist.

    This keeps group numbering consistent even when optional groups are absent.
    """
    built: list[BuiltGroup] = []
    next_group_number = 1

    for spec in specs:
        txs = spec.build_transactions(payload)
        if not txs:
            continue
        built.append(
            BuiltGroup(
                group_number=next_group_number,
                group_type=spec.group_type,
                transactions=txs,
            )
        )
        next_group_number += 1

    return built


def render_group(
    *,
    group_number: int,
    group_type: str,
    transactions: list[Transaction],
) -> tuple[list[RenderableRecord], int, int]:
    """
    Render a group as record objects: GRH + transaction records + GRT

    Returns:
      (group_records, txcount, reccount)

    - txcount/reccount come from Transaction counting logic via sum_counts()
    - reccount is the count of record lines in the group body (excluding GRH/GRT)
    """
    txcount, reccount = sum_counts(transactions)

    body_records: list[RenderableRecord] = []
    for t in transactions:
        # Transaction.records are countable and renderable; safe to treat as RenderableRecord for output.
        body_records.extend(t.records)

    group_records: list[RenderableRecord] = [
        GRHRecord(group=group_number, type_=group_type),
        *body_records,
        GRTRecord(group=group_number, txcount=txcount, reccount=reccount),
    ]

    return group_records, txcount, reccount


def total_physical_line_count(groups: list[BuiltGroup]) -> int:
    """
    Count total *physical* lines across all groups INCLUDING each group’s GRH/GRT,
    but EXCLUDING HDR and TRL.

    This makes RECTOTAL robust and future-proof.
    """
    total = 0
    for g in groups:
        _group_records, _txcount, reccount = render_group(
            group_number=g.group_number,
            group_type=g.group_type,
            transactions=g.transactions,
        )
        # GRH + body(reccount lines) + GRT
        total += 2 + reccount
    return total


# Export helpers used by writer builders
__all__ = [
    "BuiltGroup",
    "GroupSpec",
    "build_groups",
    "render_group",
    "total_physical_line_count",
    "_get_objects",
]
