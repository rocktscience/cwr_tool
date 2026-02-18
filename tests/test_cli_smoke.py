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
