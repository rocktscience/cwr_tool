from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, Any, cast

import typer

from cwr_tool.generation.pipeline import generate_cwr_file
from cwr_tool.validation.engine import validate_minimal

app = typer.Typer(no_args_is_help=True)


def _read_json(path: Path) -> dict[str, Any]:
    """Read a JSON file and ensure the top-level value is an object (dict)."""
    try:
        data: Any = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise typer.BadParameter(f"File not found: {path}") from None
    except json.JSONDecodeError as e:
        raise typer.BadParameter(
            f"Invalid JSON in {path}: {e.msg} (line {e.lineno}, col {e.colno})"
        ) from None

    if not isinstance(data, dict):
        raise typer.BadParameter(f"Input JSON must be an object at the top level: {path}")

    return cast(dict[str, Any], data)


@app.command()
def validate(
    input_path: Annotated[Path, typer.Argument(help="Path to input JSON payload")],
) -> None:
    """Validate an input JSON payload and print a structured JSON report."""
    payload = _read_json(input_path)
    report = validate_minimal(payload)
    typer.echo(report.model_dump_json(indent=2))
    raise typer.Exit(code=0 if report.ok else 2)


@app.command()
def generate(
    input_path: Annotated[Path, typer.Argument(help="Path to input JSON payload")],
    out: Annotated[
        Path | None,
        typer.Option(
            "--out",
            "-o",
            help="Output .Vxx file path. If omitted, uses suggested filename in CWD.",
        ),
    ] = None,
    version: Annotated[
        str, typer.Option("--version", "-v", help="CWR version (2.1, 2.2, 3.0, 3.1)")
    ] = "2.1",
    sender: Annotated[
        str, typer.Option("--sender", help="Sender code (3 chars recommended)")
    ] = "SUB",
    receiver: Annotated[
        str, typer.Option("--receiver", help="Receiver code (3 chars recommended)")
    ] = "000",
    file_seq: Annotated[int, typer.Option("--file-seq", help="File sequence number (1-9999)")] = 1,
) -> None:
    """Generate a minimal 'hello CWR' file via the pipeline."""
    if not (1 <= file_seq <= 9999):
        raise typer.BadParameter("file-seq must be between 1 and 9999")

    payload = _read_json(input_path)

    report, cwr_text, suggested_name = generate_cwr_file(
        payload=payload,
        cwr_version=version,
        sender=sender,
        receiver=receiver,
        file_sequence=file_seq,
    )

    if not report.ok:
        typer.echo(report.model_dump_json(indent=2))
        raise typer.Exit(code=2)

    output_path = out or (Path.cwd() / suggested_name)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(cwr_text, encoding="ascii", errors="strict")

    report_path = output_path.with_suffix(output_path.suffix + ".report.json")
    report_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")

    typer.echo(f"Wrote: {output_path}")
    typer.echo(f"Wrote: {report_path}")
    typer.echo(f"Suggested filename: {suggested_name}")


@app.command()
def hello(
    out: Annotated[
        Path | None,
        typer.Option("--out", "-o", help="If provided, writes a generated file to this path."),
    ] = None,
) -> None:
    """Create a tiny input JSON and (optionally) generate a file, for smoke testing."""
    sample: dict[str, Any] = {
        "works": [
            {"title": "HELLO WORLD", "submitter_work_number": "0000000001", "language_code": "EN"},
        ]
    }

    report = validate_minimal(sample)
    typer.echo(report.model_dump_json(indent=2))
    if not report.ok:
        raise typer.Exit(code=2)

    if out:
        report2, cwr_text, suggested_name = generate_cwr_file(
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
        typer.echo(f"Suggested filename: {suggested_name}")
