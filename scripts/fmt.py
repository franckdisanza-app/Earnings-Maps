"""Display formatting from brand/tokens.json `format` (one place, so the numbers sheet,
captions and videos print the same thing).

money: billions with one decimal ($94.9B); below $1B, whole millions ($812M).
change: whole percent with sign (+6%, −3%); one decimal when under 1% (+0.4%).
Minus is U+2212. Rounding is half-up on the exact printed value, never float rounding.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

MINUS = "−"
SCALE = {"units": Decimal(1), "thousands": Decimal(10) ** 3, "millions": Decimal(10) ** 6, "billions": Decimal(10) ** 9}


def _d(x: float) -> Decimal:
    return Decimal(repr(x)) if isinstance(x, float) else Decimal(x)


def _q(x: Decimal, places: int) -> Decimal:
    return x.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP)


def to_units(value: float, scale: str) -> Decimal:
    return _d(value) * SCALE[scale]


def money(value: float | None, scale: str = "millions") -> str:
    if value is None:
        return "—"
    dollars = to_units(value, scale)
    sign = MINUS if dollars < 0 else ""
    a = abs(dollars)
    if a >= Decimal(10) ** 9:
        return f"{sign}${_q(a / Decimal(10) ** 9, 1)}B"
    if a >= Decimal(10) ** 6:
        return f"{sign}${_q(a / Decimal(10) ** 6, 0)}M"
    return f"{sign}${_q(a / Decimal(10) ** 3, 0)}K"


def per_share(value: float | None) -> str:
    if value is None:
        return "—"
    d = _d(value)
    return f"{MINUS if d < 0 else ''}${_q(abs(d), 2)}"


def change(ratio: float | None) -> str:
    """ratio = current/prior − 1."""
    if ratio is None:
        return "—"
    pct = _d(ratio) * 100
    places = 1 if abs(pct) < 1 else 0
    q = _q(abs(pct), places)
    if pct == 0:
        return "0%"
    return f"{'+' if pct > 0 else MINUS}{q}%"  # keeps the sign even when it rounds to 0.0%


def yoy(current: float | None, prior: float | None) -> str:
    if current is None or not prior:
        return "—"
    if prior < 0 or current < 0:
        return "n/m"  # percent change across a loss isn't meaningful
    return change(current / prior - 1)


def percent(ratio: float | None, places: int = 0) -> str:
    if ratio is None:
        return "—"
    pct = _d(ratio) * 100
    q = _q(abs(pct), places)
    return f"{MINUS if pct < 0 else ''}{q}%"


def number(value: float | None, scale: str) -> str:
    """Printed-style number with thousands separators, e.g. 94,930 (millions)."""
    if value is None:
        return "—"
    d = _d(value)
    places = max(0, -d.as_tuple().exponent) if d != d.to_integral() else 0
    s = f"{abs(d):,.{places}f}"
    return f"({s})" if d < 0 else s


def line_value(value: float | None, unit: str, scale: str) -> str:
    if unit == "USD/share":
        return per_share(value)
    if unit == "USD":
        return money(value, scale)
    return number(value, scale)


# ---- spoken forms for the voiceover --------------------------------------------------------

def money_spoken(value: float | None, scale: str = "units", unit_word: bool = False) -> str:
    """'$102.5B' -> '102.5 billion' ('102.5 billion dollars' with unit_word); '$812M' -> '812 million'."""
    if value is None:
        return ""
    dollars = to_units(value, scale)
    a = abs(dollars)
    if a >= Decimal(10) ** 9:
        q = _q(a / Decimal(10) ** 9, 1)
        word = "billion"
    else:
        q = _q(a / Decimal(10) ** 6, 0)
        word = "million"
    num = format(q.normalize(), "f") if q == q.to_integral() else str(q)
    return f"{'minus ' if dollars < 0 else ''}{num} {word}{' dollars' if unit_word else ''}"


def change_spoken(ratio: float | None) -> str:
    """+0.079 -> 'up 8 percent'; -0.031 -> 'down 3 percent'."""
    if ratio is None:
        return ""
    pct = _d(ratio) * 100
    q = _q(abs(pct), 1 if abs(pct) < 1 else 0)
    num = format(q.normalize(), "f")
    return f"{'up' if pct > 0 else 'down'} {num} percent" if pct != 0 else "flat"
