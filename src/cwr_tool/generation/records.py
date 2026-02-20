from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol

CRLF = "\r\n"


class RenderableRecord(Protocol):
    def render(self) -> str: ...


class CountableRecord(RenderableRecord, Protocol):
    def counts(self) -> tuple[int, int]: ...


@dataclass(frozen=True, slots=True)
class RecordLine:
    record_type: str
    payload: str = ""

    def render(self) -> str:
        return f"{self.record_type}{self.payload}" if self.payload else self.record_type


def join_records(records: Iterable[RenderableRecord]) -> str:
    rendered = [r.render() for r in records]
    return CRLF.join(rendered) + CRLF
