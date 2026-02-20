from __future__ import annotations

from dataclasses import dataclass


def _req(value: str, field: str) -> str:
    v = value.strip()
    if not v:
        raise ValueError(f"{field} is required")
    return v


@dataclass(frozen=True, slots=True)
class NWRRecord:
    title: str
    submitter_work_number: str
    language_code: str = "EN"

    def render(self) -> str:
        title = _req(self.title, "title")
        swk = _req(self.submitter_work_number, "submitter_work_number")
        lang = (self.language_code or "EN").strip().upper()

        return f"NWR TITLE={title} SWK={swk} LANG={lang}"
