from __future__ import annotations

from datetime import UTC, datetime

from cwr_tool.generation.writer import render_hello_control_file


def test_hello_writer_has_control_records_in_order() -> None:
    fixed_time = datetime(2026, 1, 1, 12, 30, 45, tzinfo=UTC)

    text = render_hello_control_file(
        sender="SUB",
        receiver="000",
        cwr_version="2.1",
        now=fixed_time,
    )

    lines = [ln for ln in text.splitlines() if ln]

    assert lines[0].startswith("HDR")
    assert "SENDER=SUB" in lines[0]
    assert "RECEIVER=000" in lines[0]
    assert "VER=2.1" in lines[0]
    assert "DT=20260101123045" in lines[0]

    assert lines[1].startswith("GRH")
    assert lines[2].startswith("NWR")
    assert lines[3].startswith("GRT")
    assert lines[4].startswith("TRL")
