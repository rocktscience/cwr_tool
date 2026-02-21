from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from cwr_tool.reporting.models import Pointer, Severity, ValidationIssue, ValidationReport


@dataclass(frozen=True, slots=True)
class RuleContext:
    """
    Context provided to rules.

    We will extend this with:
    - spec (VersionSpec)
    - normalized/derived indexes (writer totals, publisher totals, etc.)
    - path tracking helpers
    """

    version: str


class Rule(Protocol):
    code: str

    def apply(self, report: ValidationReport, ctx: RuleContext, payload: object) -> None: ...


@dataclass(frozen=True, slots=True)
class RulePack:
    """
    A pack of rules to run in order (schema, semantics, cross-record, etc.).
    """

    name: str
    rules: list[Rule]

    def run(self, report: ValidationReport, ctx: RuleContext, payload: object) -> None:
        for r in self.rules:
            r.apply(report, ctx, payload)


def add_issue(
    report: ValidationReport,
    *,
    code: str,
    severity: Severity,
    message: str,
    pointer: Pointer | None = None,
) -> None:
    report.add(
        ValidationIssue(
            code=code,
            severity=severity,
            message=message,
            pointer=pointer or Pointer(),
        )
    )
