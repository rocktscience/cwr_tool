from __future__ import annotations

from dataclasses import dataclass


def _req(value: str, field: str) -> str:
    v = value.strip()
    if not v:
        raise ValueError(f"{field} is required")
    return v


@dataclass(frozen=True, slots=True)
class ALTRecord:
    """Alternate title record within a WRK transaction."""

    title: str

    def counts(self) -> tuple[int, int]:
        # Does not start a transaction; counts as one record line
        return 0, 1

    def render(self) -> str:
        t = _req(self.title, "title")
        return f"ALT TITLE={t}"
