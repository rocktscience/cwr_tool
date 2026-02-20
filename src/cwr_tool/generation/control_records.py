from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


def _fmt_dt(dt: datetime) -> str:
    return dt.strftime("%Y%m%d%H%M%S")


@dataclass(frozen=True, slots=True)
class HDRRecord:
    sender: str
    receiver: str
    version: str
    created: datetime

    def render(self) -> str:
        sender = self.sender.strip().upper()
        receiver = self.receiver.strip().upper()
        ver = self.version.strip()
        dt = _fmt_dt(self.created)
        return f"HDR SENDER={sender} RECEIVER={receiver} VER={ver} DT={dt}"


@dataclass(frozen=True, slots=True)
class GRHRecord:
    group: int = 1
    type_: str = "WRK"

    def render(self) -> str:
        return f"GRH GROUP={self.group:05d} TYPE={self.type_}"


@dataclass(frozen=True, slots=True)
class GRTRecord:
    group: int = 1
    txcount: int = 0
    reccount: int = 0

    def render(self) -> str:
        return f"GRT GROUP={self.group:05d} TXCOUNT={self.txcount:08d} RECCOUNT={self.reccount:08d}"


@dataclass(frozen=True, slots=True)
class TRLRecord:
    groups: int = 1
    txtotal: int = 0
    rectotal: int = 4

    def render(self) -> str:
        return (
            f"TRL GROUPS={self.groups:05d} TXTOTAL={self.txtotal:08d} RECTOTAL={self.rectotal:08d}"
        )
