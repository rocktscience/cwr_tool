from __future__ import annotations

from datetime import UTC, datetime

from cwr_tool.generation.writer import render_minimal_wrk_file


def test_two_groups_wrk_and_spu_counts_and_totals() -> None:
    fixed_time = datetime(2026, 1, 1, 12, 30, 45, tzinfo=UTC)

    payload = {
        "works": [
            {"title": "HELLO WORLD", "submitter_work_number": "0000000001", "language_code": "EN"},
        ],
        "spu": [
            {"publisher_name": "ACME PUBLISHING"},
        ],
    }

    text = render_minimal_wrk_file(
        payload=payload,
        sender="SUB",
        receiver="000",
        cwr_version="2.1",
        now=fixed_time,
    )

    lines = [ln for ln in text.splitlines() if ln]

    # Expected layout:
    # 0 HDR
    # 1 GRH (WRK group 1)
    # 2 NWR
    # 3 GRT (group 1 tx=1 rec=1)
    # 4 GRH (SPU group 2)
    # 5 SPU
    # 6 GRT (group 2 tx=1 rec=1)
    # 7 TRL (groups=2 txtotal=2 rectotal=8)
    assert lines[0].startswith("HDR")

    assert lines[1] == "GRH GROUP=00001 TYPE=WRK"
    assert lines[2].startswith("NWR")
    assert lines[3] == "GRT GROUP=00001 TXCOUNT=00000001 RECCOUNT=00000001"

    assert lines[4] == "GRH GROUP=00002 TYPE=SPU"
    assert lines[5].startswith("SPU")
    assert lines[6] == "GRT GROUP=00002 TXCOUNT=00000001 RECCOUNT=00000001"

    # rectotal = HDR(1) +  +  + TRL(1) = 8
    assert lines[7] == "TRL GROUPS=00002 TXTOTAL=00000002 RECTOTAL=00000008"
