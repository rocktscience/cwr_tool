from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from cwr_tool.generation.control_records import GRHRecord, GRTRecord, HDRRecord, TRLRecord
from cwr_tool.generation.nwr_record import NWRRecord
from cwr_tool.generation.records import RenderableRecord, join_records


def _get_works(payload: dict[str, Any]) -> list[dict[str, Any]]:
    works = payload.get("works")
    if works is None:
        return []
    if not isinstance(works, list):
        raise ValueError("'works' must be a list")
    out: list[dict[str, Any]] = []
    for item in works:
        if isinstance(item, dict):
            out.append(item)
        else:
            raise ValueError("Each item in 'works' must be an object")
    return out


def render_minimal_wrk_file(
    payload: dict[str, Any],
    sender: str,
    receiver: str,
    cwr_version: str = "2.1",
    now: datetime | None = None,
) -> str:
    """
    Render a minimal WRK group CWR file based on the input payload.

    Expected payload shape (minimal):
    {
      "works": [
        {"title": "...", "submitter_work_number": "...", "language_code": "EN"},
        ...
      ]
    }
    """
    if now is None:
        now = datetime.now(UTC)

    works = _get_works(payload)

    nwr_records: list[RenderableRecord] = []
    for w in works:
        title = str(w.get("title", "")).strip()
        swk = str(w.get("submitter_work_number", "")).strip()
        lang = str(w.get("language_code", "EN")).strip() or "EN"

        # NWRRecord will raise ValueError if required fields are missing/blank
        nwr_records.append(
            NWRRecord(
                title=title,
                submitter_work_number=swk,
                language_code=lang,
            )
        )

    txcount = len(nwr_records)
    reccount = len(nwr_records)
    rectotal = 4 + len(nwr_records)  # HDR + GRH + GRT + TRL + NWRs

    records: list[RenderableRecord] = [
        HDRRecord(sender=sender, receiver=receiver, version=cwr_version, created=now),
        GRHRecord(group=1, type_="WRK"),
        *nwr_records,
        GRTRecord(group=1, txcount=txcount, reccount=reccount),
        TRLRecord(groups=1, txtotal=txcount, rectotal=rectotal),
    ]

    return join_records(records)


def render_hello_control_file(
    sender: str,
    receiver: str,
    cwr_version: str = "2.1",
    now: datetime | None = None,
) -> str:
    """
    Backwards-compatible "hello" writer used by earlier tests/demos.
    Now implemented via the payload-driven renderer.
    """
    payload: dict[str, Any] = {
        "works": [
            {
                "title": "HELLO WORLD",
                "submitter_work_number": "0000000001",
                "language_code": "EN",
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
