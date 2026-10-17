"""Fiscal-period arithmetic.

Companies on 52/53-week years end their quarters near, not on, month ends (Apple's
fiscal Q4 2025 ended Sep 27; Disney's fiscal 2022 ended Oct 1). A period end is mapped to
its *nominal month* by stepping back 7 days, so Oct 1 counts as September and Sep 27
stays September.

Fiscal years are named by the calendar year in which they end (Nvidia's FY2026 ends in
January 2026; Microsoft's FY2026 ends June 2026).
"""

from __future__ import annotations

import datetime as dt
import math

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def nominal_month(d: dt.date) -> tuple[int, int]:
    """(year, month) a period end belongs to."""
    shifted = d - dt.timedelta(days=7)
    return shifted.year, shifted.month


def fye_month(fiscal_year_end_mmdd: str) -> int:
    """SEC `fiscalYearEnd` (e.g. '0926', '0131', '1231', '0103') -> nominal month."""
    month, day = int(fiscal_year_end_mmdd[:2]), int(fiscal_year_end_mmdd[2:])
    ref = dt.date(2001, month, min(day, 28 if month == 2 else day))
    return nominal_month(ref)[1]


def fiscal_year_quarter(period_end: dt.date, fy_end_month: int) -> tuple[int, int]:
    year, month = nominal_month(period_end)
    months_into_fy = (month - fy_end_month) % 12 or 12  # 1..12
    quarter = math.ceil(months_into_fy / 3)
    fiscal_year = year if month <= fy_end_month else year + 1
    return fiscal_year, quarter


def fiscal_label(fiscal_year: int, quarter: int) -> str:
    return f"FY{fiscal_year}Q{quarter}"


def parse_label(label: str) -> tuple[int, int]:
    if not (len(label) == 8 and label.startswith("FY") and label[6] == "Q"):
        raise ValueError(f"bad fiscal label {label!r}")
    return int(label[2:6]), int(label[7])


def calendar_label(start: dt.date, end: dt.date) -> str:
    """'Jul–Sep 2025' when the quarter sits within a week of month boundaries,
    otherwise exact dates ('Jun 15–Sep 6, 2025')."""
    # within a week of a month start / month end (either side)
    start_aligned = start.day <= 8 or (start + dt.timedelta(days=7)).month != start.month
    end_aligned = end.day <= 7 or (end + dt.timedelta(days=7)).month != end.month
    if start_aligned and end_aligned:
        s = start + dt.timedelta(days=7)
        e = end - dt.timedelta(days=7)
        if s.year == e.year:
            return f"{MONTHS[s.month - 1]}–{MONTHS[e.month - 1]} {e.year}"
        return f"{MONTHS[s.month - 1]} {s.year}–{MONTHS[e.month - 1]} {e.year}"
    if start.year == end.year:
        return f"{MONTHS[start.month - 1]} {start.day}–{MONTHS[end.month - 1]} {end.day}, {end.year}"
    return f"{MONTHS[start.month - 1]} {start.day}, {start.year}–{MONTHS[end.month - 1]} {end.day}, {end.year}"


def display_period(fiscal_year: int, quarter: int, cal_label: str) -> str:
    """On-screen period: 'Fiscal Q4 2025 (Jul–Sep 2025)'."""
    return f"Fiscal Q{quarter} {fiscal_year} ({cal_label})"


def weeks_between(start: dt.date, end: dt.date) -> float:
    return ((end - start).days + 1) / 7
