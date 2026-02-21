from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from cwr_tool.generation.alt_record import ALTRecord
from cwr_tool.generation.com_record import COMRecord
from cwr_tool.generation.control_records import HDRRecord, TRLRecord
from cwr_tool.generation.group_builder import (
    _get_objects,
    build_groups,
    render_group,
    total_physical_line_count,
)
from cwr_tool.generation.nwr_record import NWRRecord
from cwr_tool.generation.records import CountableRecord, RenderableRecord, join_records
from cwr_tool.generation.spu_record import SPURecord
from cwr_tool.generation.transaction import Transaction


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


def _build_wrk_transactions(payload: dict[str, Any]) -> list[Transaction]:
    works = _get_objects(payload, "works")

    transactions: list[Transaction] = []
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

        # Transaction expects countable records; our record types implement counts().
        transactions.append(Transaction(records=tx_records))  # type: ignore[arg-type]

    return transactions


def _build_spu_transactions(payload: dict[str, Any]) -> list[Transaction]:
    items = _get_objects(payload, "spu")
    if not items:
        return []

    transactions: list[Transaction] = []
    for item in items:
        name = str(item.get("publisher_name", "")).strip()
        transactions.append(Transaction(records=[SPURecord(publisher_name=name)]))

    return transactions


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

    The WRK group supports:
      - alternate_titles -> ALT lines (non-transaction)
      - comment -> COM line (non-transaction)
    """
    if now is None:
        now = datetime.now(UTC)

    records: list[RenderableRecord] = [
        HDRRecord(sender=sender, receiver=receiver, version=cwr_version, created=now),
    ]

    # Build groups (sequential numbering only for present groups)
    specs = [
        # Group 1 (if present): WRK
        # Group 2 (if present): SPU
        # Add more groups later by appending specs.
        # e.g., GroupSpec("PWR", _build_pwr_transactions)
        #       GroupSpec("OPU", _build_opu_transactions)
        #       GroupSpec("REC", _build_rec_transactions)
        # etc.
        #
        # NOTE: group numbers are assigned by build_groups() in the order below.
        #
        # We intentionally keep this declarative so adding groups doesn't touch output math.
        #
        # fmt: off
        # (ruff/black formatting is fine either way; keeping readable)
        # fmt: on
    ]

    from cwr_tool.generation.group_builder import (
        GroupSpec,  # local import avoids circular import risk
    )

    specs = [
        GroupSpec(group_type="WRK", build_transactions=_build_wrk_transactions),
        GroupSpec(group_type="SPU", build_transactions=_build_spu_transactions),
    ]

    built = build_groups(payload, specs)

    total_tx = 0
    for g in built:
        group_records, txcount, _reccount = render_group(
            group_number=g.group_number,
            group_type=g.group_type,
            transactions=g.transactions,
        )
        records.extend(group_records)
        total_tx += txcount

    groups_count = len(built)

    # RECTOTAL = HDR(1) + all groups (including GRH/GRT) + TRL(1)
    group_lines = total_physical_line_count(built)
    rectotal = 2 + group_lines  # HDR + TRL + groups

    records.append(TRLRecord(groups=groups_count, txtotal=total_tx, rectotal=rectotal))
    return join_records(records)


def render_hello_control_file(
    sender: str,
    receiver: str,
    cwr_version: str = "2.1",
    now: datetime | None = None,
) -> str:
    """
    "Hello" convenience writer used by tests.

    Includes ALT + COM so your CLI smoke + writer tests validate ordering.
    """
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
