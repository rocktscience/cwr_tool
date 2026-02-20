from __future__ import annotations

from datetime import UTC, datetime

from cwr_tool.generation.writer import render_minimal_wrk_file


def test_minimal_wrk_file_renders_expected_lines() -> None:
    fixed_time = datetime(2026, 1, 1, 12, 30, 45, tzinfo=UTC)

    payload = {
        "works": [
            {"title": "HELLO WORLD", "submitter_work_number": "0000000001", "language_code": "EN"},
            {"title": "SECOND WORK", "submitter_work_number": "0000000002", "language_code": "ES"},
        ]
    }

    text = render_minimal_wrk_file(
        payload=payload,
        sender="sub",  # intentionally lower to verify normalization happens in HDR
        receiver="000",
        cwr_version="2.1",
        now=fixed_time,
    )

    lines = [ln for ln in text.splitlines() if ln]

    assert lines[0] == "HDR SENDER=SUB RECEIVER=000 VER=2.1 DT=20260101123045"
    assert lines[1] == "GRH GROUP=00001 TYPE=WRK"

    # Two NWR “transactions”
    assert lines[2] == "NWR TITLE=HELLO WORLD SWK=0000000001 LANG=EN"
    assert lines[3] == "NWR TITLE=SECOND WORK SWK=0000000002 LANG=ES"

    # Counts reflect 2 NWR records
    assert lines[4] == "GRT GROUP=00001 TXCOUNT=00000002 RECCOUNT=00000002"

    # RECTOTAL includes: HDR, GRH, 2xNWR, GRT, TRL = 6
    assert lines[5] == "TRL GROUPS=00001 TXTOTAL=00000002 RECTOTAL=00000006"
