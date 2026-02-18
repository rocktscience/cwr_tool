from __future__ import annotations

import json
from pathlib import Path

import typer

from cwr_tool.generation.pipeline import generate_cwr_file
from cwr_tool.validation.engine import validate_minimal

app = typer.Typer(no_args_is_help=True)


@app.command()
def validate(input_path: Path) -> None:
    """Validate an input JSON payload and print a structured JSON report."""
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    report = validate_minimal(payload)
    typer.echo(report.model_dump_json(indent=2))


@app.command()
def generate(
    input_path: Path,
    out: Path,
    version: str = "2.1",
    sender: str = "SUB",
    receiver: str = "000",
    file_seq: int = 1,
) -> None:
    """
    Generate a minimal 'hello CWR' file via the pipeline.

    Notes:
    - We avoid typer.Option(...) in defaults to satisfy Ruff B008.
    - We'll add richer CLI options (and config profiles) after the core engine is stable.
    """
    if not (1 <= file_seq <= 9999):
        raise typer.BadParameter("file-seq must be between 1 and 9999")

    payload = json.loads(input_path.read_text(encoding="utf-8"))
    report, cwr_text, cwr_filename = generate_cwr_file(
        payload=payload,
        cwr_version=version,
        sender=sender,
        receiver=receiver,
        file_sequence=file_seq,
    )

    if not report.ok:
        typer.echo(report.model_dump_json(indent=2))
        raise typer.Exit(code=2)

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(cwr_text, encoding="ascii", errors="strict")

    report_path = out.with_suffix(out.suffix + ".report.json")
    report_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")

    typer.echo(f"Wrote: {out}")
    typer.echo(f"Wrote: {report_path}")
    typer.echo(f"Suggested filename: {cwr_filename}")


@app.command()
def hello(out: Path | None = None) -> None:
    """Create a tiny input JSON and (optionally) generate a file, for smoke testing."""
    sample = {
        "works": [
            {"title": "HELLO WORLD", "submitter_work_number": "0000000001", "language_code": "EN"}
        ]
    }
    report = validate_minimal(sample)
    typer.echo(report.model_dump_json(indent=2))

    if out:
        report2, cwr_text, cwr_filename = generate_cwr_file(
            payload=sample,
            cwr_version="2.1",
            sender="SUB",
            receiver="000",
            file_sequence=1,
        )
        if not report2.ok:
            raise typer.Exit(code=2)

        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(cwr_text, encoding="ascii", errors="strict")
        typer.echo(f"Wrote: {out}")
        typer.echo(f"Suggested filename: {cwr_filename}")
