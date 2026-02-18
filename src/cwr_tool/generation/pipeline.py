from __future__ import annotations

from datetime import datetime

from cwr_tool.generation.writer import render_hello_control_file
from cwr_tool.reporting.models import ValidationReport
from cwr_tool.validation.engine import validate_minimal


def suggest_filename(
    cwr_version: str,
    sender: str,
    receiver: str,
    file_sequence: int,
    created: datetime,
) -> str:
    yy = created.strftime("%y")
    nnnn = f"{file_sequence:04d}"

    if cwr_version in {"2.1", "2.2"}:
        vxx = "V21" if cwr_version == "2.1" else "V22"
        return f"CW{yy}{nnnn}{sender}_{receiver}.{vxx}"

    # Placeholder for v3.x naming until we implement exact conventions per spec
    return f"CW{yy}{nnnn}{sender}_{receiver}_V{cwr_version.replace('.', '-')}-0.CWR"


def generate_cwr_file(
    payload: dict,
    cwr_version: str,
    sender: str,
    receiver: str,
    file_sequence: int,
) -> tuple[ValidationReport, str, str]:
    report = validate_minimal(payload)
    if not report.ok:
        return report, "", ""

    cwr_text = render_hello_control_file(sender=sender, receiver=receiver, cwr_version=cwr_version)
    filename = suggest_filename(
        cwr_version=cwr_version,
        sender=sender,
        receiver=receiver,
        file_sequence=file_sequence,
        created=datetime.utcnow(),
    )
    return report, cwr_text, filename
