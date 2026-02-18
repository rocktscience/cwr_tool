from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class Severity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class Pointer(BaseModel):
    record_type: str | None = None
    path: str | None = None
    field: str | None = None
    index: int | None = None


class ValidationIssue(BaseModel):
    code: str
    severity: Severity
    message: str
    pointer: Pointer = Field(default_factory=Pointer)
    context: dict[str, Any] = Field(default_factory=dict)


class ValidationReport(BaseModel):
    ok: bool
    version: str = "0.1"
    issues: list[ValidationIssue] = Field(default_factory=list)

    def add(self, issue: ValidationIssue) -> None:
        self.issues.append(issue)
        if issue.severity == Severity.ERROR:
            self.ok = False
