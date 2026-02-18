from __future__ import annotations

from cwr_tool.generation.writer import render_hello_control_file


def test_hello_writer_has_control_records_in_order() -> None:
    text = render_hello_control_file(sender="SUB", receiver="000", cwr_version="2.1")
    lines = [ln for ln in text.split("\r\n") if ln]
    assert lines[0].startswith("HDR")
    assert lines[1].startswith("GRH")
    assert lines[2].startswith("GRT")
    assert lines[3].startswith("TRL")
