from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from cwr_tool.generation.writer import render_minimal_wrk_file
from cwr_tool.reporting.models import ValidationReport
from cwr_tool.validation.engine import validate_minimal


def _ensure_utc(dt: datetime) -> datetime:
    """Return a timezone-aware datetime in UTC.

    - If `dt` is naive, assume it is already UTC.
    - If `dt` is timezone-aware, convert it to UTC.
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def suggest_filename(
    cwr_version: str,
    sender: str,
    receiver: str,
    file_sequence: int,
    created: datetime,
) -> str:
    """Suggest a CWR filename.

    Current convention used by this tool:
    - CWR 2.1 / 2.2: `CWyynnnnsss_rrr.V21|V22`
    - CWR 3.0 / 3.1: `CWyynnnnsss_rrr.V30|V31`

    Notes:
    - `sender` and `receiver` are normalized to uppercase.
    - `file_sequence` is formatted as a 4-digit, zero-padded number.
    """
    created = _ensure_utc(created)

    sender = sender.strip().upper()
    receiver = receiver.strip().upper()

    yy = created.strftime("%y")
    nnnn = f"{file_sequence:04d}"

    if cwr_version == "2.1":
        return f"CW{yy}{nnnn}{sender}_{receiver}.V21"
    if cwr_version == "2.2":
        return f"CW{yy}{nnnn}{sender}_{receiver}.V22"
    if cwr_version == "3.0":
        return f"CW{yy}{nnnn}{sender}_{receiver}.V30"
    if cwr_version == "3.1":
        return f"CW{yy}{nnnn}{sender}_{receiver}.V31"

    safe_ver = cwr_version.replace(".", "-")
    return f"CW{yy}{nnnn}{sender}_{receiver}.V{safe_ver}"


def generate_cwr_file(
    payload: dict[str, Any],
    cwr_version: str,
    sender: str,
    receiver: str,
    file_sequence: int,
    created: datetime | None = None,
) -> tuple[ValidationReport, str, str]:
    """Validate payload, render minimal WRK file, and suggest output filename."""
    report = validate_minimal(payload, version=cwr_version)
    if not report.ok:
        return report, "", ""

    if created is None:
        created = datetime.now(UTC)

    created = _ensure_utc(created)

    cwr_text = render_minimal_wrk_file(
        payload=payload,
        sender=sender,
        receiver=receiver,
        cwr_version=cwr_version,
        now=created,
    )

    filename = suggest_filename(
        cwr_version=cwr_version,
        sender=sender,
        receiver=receiver,
        file_sequence=file_sequence,
        created=created,
    )

    return report, cwr_text, filename
