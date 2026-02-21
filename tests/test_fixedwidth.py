from __future__ import annotations

import pytest

from cwr_tool.format.fixedwidth import FieldSpec, FixedWidthError, fmt_int, fmt_text


def test_fmt_text_left_pads_and_truncates() -> None:
    spec = FieldSpec(width=5, align="left", pad=" ")
    assert fmt_text("AB", spec) == "AB   "
    assert fmt_text("ABCDEFG", spec) == "ABCDE"


def test_fmt_text_required_raises() -> None:
    spec = FieldSpec(width=3, required=True)
    with pytest.raises(FixedWidthError):
        fmt_text("", spec)


def test_fmt_int_right_zero_pads() -> None:
    spec = FieldSpec(width=4, align="right", pad="0")
    assert fmt_int(12, spec) == "0012"


def test_fmt_int_digits_only() -> None:
    spec = FieldSpec(width=4, align="right", pad="0")
    with pytest.raises(FixedWidthError):
        fmt_int("12A", spec)


def test_fmt_int_truncates_rightmost() -> None:
    spec = FieldSpec(width=3, align="right", pad="0")
    assert fmt_int("12345", spec) == "345"
