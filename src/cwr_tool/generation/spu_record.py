from __future__ import annotations

from dataclasses import dataclass


def _req(value: str, field: str) -> str:
    v = value.strip()
    if not v:
        raise ValueError(f"{field} is required")
    return v


@dataclass(frozen=True, slots=True)
class SPURecord:
    """Minimal SPU transaction record (placeholder)."""

    publisher_name: str

    def counts(self) -> tuple[int, int]:
        return 1, 1

    def render(self) -> str:
        name = _req(self.publisher_name, "publisher_name")
        return f"SPU NAME={name}"
