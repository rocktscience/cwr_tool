from __future__ import annotations

from dataclasses import dataclass


class FixedWidthError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class FieldSpec:
    """
    Fixed-width field spec.

    - width: exact width in characters
    - align: "left" or "right"
    - pad: pad character (usually space, sometimes '0' for numerics)
    - required: if True, empty/blank is error
    """

    width: int
    align: str = "left"
    pad: str = " "
    required: bool = False

    def __post_init__(self) -> None:
        if self.width <= 0:
            raise FixedWidthError("Field width must be > 0")
        if self.align not in ("left", "right"):
            raise FixedWidthError("align must be 'left' or 'right'")
        if len(self.pad) != 1:
            raise FixedWidthError("pad must be a single character")


def _to_ascii(s: str) -> str:
    try:
        s.encode("ascii")
    except UnicodeEncodeError as e:
        raise FixedWidthError(f"Non-ASCII character: {e}") from None
    return s


def fmt_text(value: str | None, spec: FieldSpec) -> str:
    raw = "" if value is None else str(value)
    raw = raw.strip()

    if spec.required and not raw:
        raise FixedWidthError("Required field is blank")

    raw = _to_ascii(raw)

    if len(raw) > spec.width:
        raw = raw[: spec.width]

    if spec.align == "left":
        return raw.ljust(spec.width, spec.pad)
    return raw.rjust(spec.width, spec.pad)


def fmt_int(value: int | str | None, spec: FieldSpec) -> str:
    raw = "" if value is None else str(value).strip()

    if spec.required and not raw:
        raise FixedWidthError("Required numeric field is blank")

    if raw and not raw.isdigit():
        raise FixedWidthError(f"Numeric field must be digits only: {raw}")

    raw = _to_ascii(raw)

    if len(raw) > spec.width:
        # keep rightmost digits (common for numeric truncation)
        raw = raw[-spec.width :]

    # numeric defaults: right aligned
    align = spec.align or "right"
    pad = spec.pad or "0"

    if align == "left":
        return raw.ljust(spec.width, pad)
    return raw.rjust(spec.width, pad)
