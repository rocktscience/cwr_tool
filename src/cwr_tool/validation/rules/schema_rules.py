from __future__ import annotations

from cwr_tool.reporting.models import Pointer, Severity, ValidationReport
from cwr_tool.validation.rules.base import RuleContext, add_issue


class WorksRequiredRule:
    code = "SCHEMA.WORKS.MISSING"

    def apply(self, report: ValidationReport, ctx: RuleContext, payload: object) -> None:
        if not isinstance(payload, dict):
            add_issue(
                report,
                code="SCHEMA.PAYLOAD.NOT_OBJECT",
                severity=Severity.ERROR,
                message="Top-level payload must be an object.",
                pointer=Pointer(path="/"),
            )
            return

        works = payload.get("works")
        if not isinstance(works, list) or len(works) == 0:
            add_issue(
                report,
                code=self.code,
                severity=Severity.ERROR,
                message="Input must include a non-empty 'works' array.",
                pointer=Pointer(path="/works"),
            )


class WorkFieldsRule:
    code = "SCHEMA.WORK.FIELD"

    def apply(self, report: ValidationReport, ctx: RuleContext, payload: object) -> None:
        if not isinstance(payload, dict):
            return

        works = payload.get("works")
        if not isinstance(works, list):
            return

        for i, w in enumerate(works):
            if not isinstance(w, dict):
                add_issue(
                    report,
                    code="SCHEMA.WORK.NOT_OBJECT",
                    severity=Severity.ERROR,
                    message="Each work must be an object.",
                    pointer=Pointer(path="/works", index=i),
                )
                continue

            title = w.get("title")
            if not isinstance(title, str) or not title.strip():
                add_issue(
                    report,
                    code="WORK.TITLE.REQUIRED",
                    severity=Severity.ERROR,
                    message="Work title is required.",
                    pointer=Pointer(path="/works/title", index=i),
                )

            swn = w.get("submitter_work_number")
            if not isinstance(swn, str) or not swn.strip():
                add_issue(
                    report,
                    code="WORK.SUBMITTER_WORK_NUMBER.REQUIRED",
                    severity=Severity.ERROR,
                    message="submitter_work_number is required (string).",
                    pointer=Pointer(path="/works/submitter_work_number", index=i),
                )
