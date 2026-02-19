from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

CRLF = "\r\n"


@dataclass(frozen=True, slots=True)
class RecordLine:
    record_type: str
    payload: str = ""

    def render(self) -> str:
        return f"{self.record_type}{self.payload}" if self.payload else self.record_type


def join_records(records: Iterable[RecordLine]) -> str:
    rendered = [r.render() for r in records]
    return CRLF.join(rendered) + CRLF
