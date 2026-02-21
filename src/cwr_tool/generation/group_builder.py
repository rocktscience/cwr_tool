from __future__ import annotations

from collections.abc import Sequence
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


@dataclass(frozen=True, slots=True)
class GroupSpec:
    """A single CWR group spec (e.g., WRK, SPU) with its transactions."""

    group_number: int
    group_type: str
    transactions: list[Transaction]


@dataclass(frozen=True, slots=True)
class GroupResult:
    """
    Rendered group records plus derived counts.

    - records include GRH + body record lines + GRT
    - txcount/reccount exclude GRH/GRT (CWR convention for group counts)
    """

    records: list[RenderableRecord]
    txcount: int
    reccount: int
    line_count: int  # physical lines in this group incl GRH/GRT


def render_group(*, spec: GroupSpec) -> GroupResult:
    """
    Build: GRH + (transaction record lines) + GRT.

    Returns counts where:
      txcount = number of transactions
      reccount = number of record lines inside transactions (excludes GRH/GRT)
      line_count = physical lines in group including GRH/GRT
    """
    txcount, reccount = sum_counts(spec.transactions)

    body_records: list[RenderableRecord] = []
    for t in spec.transactions:
        # Transaction records render as body lines.
        body_records.extend(t.records)

    records: list[RenderableRecord] = [
        GRHRecord(group=spec.group_number, type_=spec.group_type),
        *body_records,
        GRTRecord(group=spec.group_number, txcount=txcount, reccount=reccount),
    ]

    line_count = 2 + reccount  # GRH + body + GRT
    return GroupResult(records=records, txcount=txcount, reccount=reccount, line_count=line_count)


def build_groups(specs: Sequence[GroupSpec]) -> tuple[list[RenderableRecord], list[GroupResult]]:
    """
    Render multiple groups in order.

    Returns:
      - all rendered records for groups
      - per-group results (counts, line_count)
    """
    all_records: list[RenderableRecord] = []
    results: list[GroupResult] = []

    for spec in specs:
        res = render_group(spec=spec)
        results.append(res)
        all_records.extend(res.records)

    return all_records, results


def total_physical_line_count(group_results: Sequence[GroupResult]) -> int:
    """Total physical lines across all groups (incl GRH/GRT per group)."""
    return sum(g.line_count for g in group_results)
