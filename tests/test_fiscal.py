import datetime as dt

import pytest

from fiscal import calendar_label, display_period, fiscal_label, fiscal_year_quarter, fye_month


@pytest.mark.parametrize(
    "fye,period_end,expected",
    [
        ("0926", dt.date(2025, 9, 27), "FY2025Q4"),  # Apple, 52/53-week year
        ("0926", dt.date(2025, 12, 27), "FY2026Q1"),
        ("0630", dt.date(2025, 9, 30), "FY2026Q1"),  # Microsoft
        ("0125", dt.date(2025, 10, 26), "FY2026Q3"),  # Nvidia, FY named by the January it ends in
        ("0131", dt.date(2026, 1, 31), "FY2026Q4"),  # Walmart
        ("1227", dt.date(2025, 9, 6), "FY2025Q3"),  # PepsiCo, 12-week Q3 ending in early September
        ("0927", dt.date(2022, 10, 1), "FY2022Q4"),  # Disney, year ending Oct 1
        ("0831", dt.date(2025, 11, 23), "FY2026Q1"),  # Costco
        ("0930", dt.date(2025, 9, 30), "FY2025Q4"),  # Visa
        ("1231", dt.date(2022, 9, 30), "FY2022Q3"),  # Uber
        ("0103", dt.date(2025, 3, 29), "FY2025Q1"),  # FYE in early January counts as December
    ],
)
def test_fiscal_labels(fye, period_end, expected):
    assert fiscal_label(*fiscal_year_quarter(period_end, fye_month(fye))) == expected


@pytest.mark.parametrize(
    "start,end,expected",
    [
        (dt.date(2025, 6, 29), dt.date(2025, 9, 27), "Jul–Sep 2025"),
        (dt.date(2025, 7, 1), dt.date(2025, 9, 30), "Jul–Sep 2025"),
        (dt.date(2022, 7, 3), dt.date(2022, 10, 1), "Jul–Sep 2022"),
        (dt.date(2025, 11, 1), dt.date(2026, 1, 31), "Nov 2025–Jan 2026"),
        (dt.date(2025, 6, 15), dt.date(2025, 9, 6), "Jun 15–Sep 6, 2025"),  # PepsiCo-style 12-week quarter
    ],
)
def test_calendar_labels(start, end, expected):
    assert calendar_label(start, end) == expected


def test_display_period():
    assert display_period(2025, 4, "Jul–Sep 2025") == "Fiscal Q4 2025 (Jul–Sep 2025)"
