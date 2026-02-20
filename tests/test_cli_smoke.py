from __future__ import annotations

import json
import subprocess
from pathlib import Path


def test_cli_validate_smoke(tmp_path: Path) -> None:
    payload = {"works": [{"title": "HELLO WORLD", "submitter_work_number": "0000000001"}]}
    p = tmp_path / "in.json"
    p.write_text(json.dumps(payload), encoding="utf-8")

    proc = subprocess.run(
        [".venv/bin/cwr-tool", "validate", str(p)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 0
    assert '"ok": true' in proc.stdout


def test_cli_generate_smoke(tmp_path: Path) -> None:
    payload = {
        "works": [
            {
                "title": "HELLO WORLD",
                "submitter_work_number": "0000000001",
                "alternate_titles": ["HELLO WORLD (ALT)"],
                "comment": "NON_TX_LINE",
            }
        ]
    }
    p = tmp_path / "in.json"
    p.write_text(json.dumps(payload), encoding="utf-8")

    out = tmp_path / "out.V21"

    proc = subprocess.run(
        [
            ".venv/bin/cwr-tool",
            "generate",
            str(p),
            "--out",
            str(out),
            "--version",
            "2.1",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 0
    assert out.exists()

    text = out.read_text(encoding="ascii")
    lines = [ln for ln in text.splitlines() if ln]

    assert lines[0].startswith("HDR")
    assert lines[1].startswith("GRH")
    assert lines[2].startswith("NWR")
    assert lines[3].startswith("ALT")
    assert lines[4].startswith("COM")
    assert lines[5].startswith("GRT")
    assert lines[6].startswith("TRL")
