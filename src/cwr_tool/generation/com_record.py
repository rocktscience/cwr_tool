from __future__ import annotations

from dataclasses import dataclass


def _req_or_blank(value: str) -> str:
    return value.strip()


@dataclass(frozen=True, slots=True)
class COMRecord:
    """Non-transaction comment record (counts as record line, not a transaction)."""

    comment: str

    def counts(self) -> tuple[int, int]:
        # Does not start a transaction; counts as one record line
        return 0, 1

    def render(self) -> str:
        msg = _req_or_blank(self.comment)
        return f"COM COMMENT={msg}" if msg else "COM"
