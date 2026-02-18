from __future__ import annotations

from datetime import datetime


def _prefix(record_type: str, tx_seq: int, rec_seq: int) -> str:
    # 3-char record + 8-digit tx seq + 8-digit record seq
    return f"{record_type}{tx_seq:08d}{rec_seq:08d}"


def render_hello_control_file(sender: str, receiver: str, cwr_version: str) -> str:
    """
    Minimal "hello CWR" output:
    HDR, GRH, GRT, TRL.

    This is a pipeline proving ground. Next steps will implement per-version
    fixed-width layouts from CISAC specs.
    """
    now = datetime.now(datetime.UTC)
    created_date = now.strftime("%Y%m%d")
    created_time = now.strftime("%H%M%S")

    lines: list[str] = []
    lines.append(
        _prefix("HDR", 0, 0)
        + f"SENDER={sender} RECEIVER={receiver} VER={cwr_version} DT={created_date}{created_time}"
    )
    lines.append(_prefix("GRH", 0, 0) + "GROUP=00001 TYPE=WRK")
    lines.append(_prefix("GRT", 0, 0) + "GROUP=00001 TXCOUNT=00000000 RECCOUNT=00000000")
    lines.append(_prefix("TRL", 0, 0) + "GROUPS=00001 TXTOTAL=00000000 RECTOTAL=00000004")
    return "\r\n".join(lines) + "\r\n"
