from __future__ import annotations

from cwr_tool.reporting.models import Pointer, Severity, ValidationIssue, ValidationReport
from cwr_tool.spec.registry import SpecRegistry


def validate_minimal(payload: dict, *, version: str = "2.1") -> ValidationReport:
    """
    MVP validation entry point.

    - Loads version spec (fails early if unsupported)
    - Runs minimal schema checks (works array, required fields)
    """
    report = ValidationReport(ok=True)

    # Ensure version is supported
    try:
        SpecRegistry.get(version)
    except ValueError as e:
        report.add(
            ValidationIssue(
                code="SPEC.VERSION.UNSUPPORTED",
                severity=Severity.ERROR,
                message=str(e),
                pointer=Pointer(path="/"),
            )
        )
        return report

    if (
        "works" not in payload
        or not isinstance(payload["works"], list)
        or len(payload["works"]) == 0
    ):
        report.add(
            ValidationIssue(
                code="SCHEMA.WORKS.MISSING",
                severity=Severity.ERROR,
                message="Input must include a non-empty 'works' array.",
                pointer=Pointer(path="/works"),
            )
        )
        return report

    for i, work in enumerate(payload["works"]):
        if not isinstance(work, dict):
            report.add(
                ValidationIssue(
                    code="SCHEMA.WORK.NOT_OBJECT",
                    severity=Severity.ERROR,
                    message="Each work must be an object.",
                    pointer=Pointer(path="/works", index=i),
                )
            )
            continue

        title = work.get("title")
        if not title or not isinstance(title, str):
            report.add(
                ValidationIssue(
                    code="WORK.TITLE.REQUIRED",
                    severity=Severity.ERROR,
                    message="Work title is required.",
                    pointer=Pointer(path="/works/title", index=i),
                )
            )

        swn = work.get("submitter_work_number")
        if not swn or not isinstance(swn, str):
            report.add(
                ValidationIssue(
                    code="WORK.SUBMITTER_WORK_NUMBER.REQUIRED",
                    severity=Severity.ERROR,
                    message="submitter_work_number is required (string).",
                    pointer=Pointer(path="/works/submitter_work_number", index=i),
                )
            )

    return report
