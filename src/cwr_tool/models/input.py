from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class CWRVersion(StrEnum):
    V21 = "2.1"
    V22 = "2.2"
    V30 = "3.0"
    V31 = "3.1"


class WorkInput(BaseModel):
    """
    Minimal normalized Work input for MVP.

    We will expand this to include:
    - writers, publishers, shares, identifiers (ISWC), territories, recordings, etc.
    - version-specific fields mapped by SpecRegistry
    """

    title: str = Field(min_length=1)
    submitter_work_number: str = Field(min_length=1)

    # optional metadata
    language_code: str = Field(default="EN", min_length=1)

    # optional transaction lines inside WRK
    alternate_titles: list[str] = Field(default_factory=list)
    comment: str | None = None

    # room for forward-compatible input (ignored by default)
    extra: dict[str, Any] = Field(default_factory=dict)


class SPUInput(BaseModel):
    """
    Minimal SPU group input (publisher statements).
    We'll expand later with identifiers, societies, addresses, etc.
    """

    publisher_name: str = Field(min_length=1)


class MinimalPayload(BaseModel):
    """
    Current accepted payload contract.

    NOTE:
    - We intentionally keep this minimal now.
    - We'll add normalized sections for interested parties, writer shares, etc.
    """

    works: list[WorkInput] = Field(min_length=1)
    spu: list[SPUInput] = Field(default_factory=list)
