from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from cwr_tool.generation.alt_record import ALTRecord
from cwr_tool.generation.com_record import COMRecord
from cwr_tool.generation.control_records import GRHRecord, GRTRecord, HDRRecord, TRLRecord
from cwr_tool.generation.nwr_record import NWRRecord
from cwr_tool.generation.records import CountableRecord, RenderableRecord, join_records
from cwr_tool.generation.spu_record import SPURecord
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


def _get_str_list(work: dict[str, Any], key: str) -> list[str]:
    value = work.get(key)
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"'{key}' must be a list of strings")
    out: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise ValueError(f"Each item in '{key}' must be a string")
        s = item.strip()
        if s:
            out.append(s)
    return out


def _render_group(
    *,
    group_number: int,
    group_type: str,
    transactions: list[Transaction],
) -> tuple[list[RenderableRecord], int, int]:
    """
    Render a group:

      GRH
      (transaction body lines...)
      GRT

    Returns:
      - group_records: physical lines for this group (includes GRH and GRT)
      - txcount: group transaction count
      - group_line_count: number of physical lines in this group
    """
    txcount, body_reccount = sum_counts(transactions)

    body_lines: list[RenderableRecord] = []
    for t in transactions:
        body_lines.extend(t.records)

    group_records: list[RenderableRecord] = [
        GRHRecord(group=group_number, type_=group_type),
        *body_lines,
        GRTRecord(group=group_number, txcount=txcount, reccount=body_reccount),
    ]

    # Robust: physical lines in the group is literally what we output.
    group_line_count = len(group_records)
    return group_records, txcount, group_line_count


def render_minimal_wrk_file(
    payload: dict[str, Any],
    sender: str,
    receiver: str,
    cwr_version: str = "2.1",
    now: datetime | None = None,
) -> str:
    """
    Render a minimal CWR file with:
      - WRK group from payload["works"]
      - optional SPU group from payload["spu"]

    WRK group supports:
      - alternate_titles -> ALT lines (non-tx lines inside transaction)
      - comment -> COM line (non-tx line inside transaction)
    """
    if now is None:
        now = datetime.now(UTC)

    records: list[RenderableRecord] = [
        HDRRecord(sender=sender, receiver=receiver, version=cwr_version, created=now),
    ]

    groups_count = 0
    total_tx = 0
    total_group_lines = 0
    next_group_number = 1

    # ---------------------------
    # Group: WRK
    # ---------------------------
    works = _get_objects(payload, "works")
    if works:
        wrk_transactions: list[Transaction] = []
        for w in works:
            title = str(w.get("title", "")).strip()
            swk = str(w.get("submitter_work_number", "")).strip()
            lang = str(w.get("language_code", "EN")).strip() or "EN"

            tx_records: list[CountableRecord] = [
                NWRRecord(title=title, submitter_work_number=swk, language_code=lang),
            ]

            for alt in _get_str_list(w, "alternate_titles"):
                tx_records.append(ALTRecord(title=alt))

            comment = w.get("comment")
            if isinstance(comment, str) and comment.strip():
                tx_records.append(COMRecord(comment=comment))

            wrk_transactions.append(Transaction(records=tx_records))

        wrk_group, wrk_tx, wrk_group_lines = _render_group(
            group_number=next_group_number,
            group_type="WRK",
            transactions=wrk_transactions,
        )
        records.extend(wrk_group)

        groups_count += 1
        total_tx += wrk_tx
        total_group_lines += wrk_group_lines
        next_group_number += 1

    # ---------------------------
    # Group: SPU (optional)
    # ---------------------------
    spu_items = _get_objects(payload, "spu")
    if spu_items:
        spu_transactions: list[Transaction] = []
        for item in spu_items:
            name = str(item.get("publisher_name", "")).strip()
            spu_transactions.append(Transaction(records=[SPURecord(publisher_name=name)]))

        spu_group, spu_tx, spu_group_lines = _render_group(
            group_number=next_group_number,
            group_type="SPU",
            transactions=spu_transactions,
        )
        records.extend(spu_group)

        groups_count += 1
        total_tx += spu_tx
        total_group_lines += spu_group_lines
        next_group_number += 1

    # File total physical lines = HDR(1) + groups + TRL(1)
    rectotal = 2 + total_group_lines

    records.append(TRLRecord(groups=groups_count, txtotal=total_tx, rectotal=rectotal))

    return join_records(records)


def render_hello_control_file(
    sender: str,
    receiver: str,
    cwr_version: str = "2.1",
    now: datetime | None = None,
) -> str:
    """Convenience writer used by tests (includes ALT + COM)."""
    payload: dict[str, Any] = {
        "works": [
            {
                "title": "HELLO WORLD",
                "submitter_work_number": "0000000001",
                "language_code": "EN",
                "alternate_titles": ["HELLO WORLD (ALT)"],
                "comment": "NON_TX_LINE",
            }
        ]
    }
    return render_minimal_wrk_file(
        payload=payload,
        sender=sender,
        receiver=receiver,
        cwr_version=cwr_version,
        now=now,
    )
