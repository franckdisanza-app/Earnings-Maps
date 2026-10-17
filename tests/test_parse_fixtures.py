"""Regression: the four fixture releases (different income-statement shapes) parse to the
values two independent extractions agreed on, and pass validation."""

import json
import pathlib

import pytest

from parse_release import build
from validate import run_checks

FIXTURES = pathlib.Path(__file__).parent / "fixtures"
CASES = sorted(p.name for p in FIXTURES.iterdir() if (p / "expected.json").exists())


def load(case):
    expected = json.loads((FIXTURES / case / "expected.json").read_text(encoding="utf-8"))
    filing = json.loads((FIXTURES / case / "raw" / "filing.json").read_text(encoding="utf-8"))
    exhibit = FIXTURES / case / "raw" / filing["release_exhibit"]["document"]
    return expected, build(expected["ticker"], expected["period"], exhibit, filing)


def test_four_shapes_are_covered():
    assert set(CASES) == {"apple_fy2025q4", "microsoft_fy2026q1", "visa_fy2025q4", "uber_fy2022q3"}


@pytest.mark.parametrize("case", CASES)
def test_values_match_expected(case):
    expected, data = load(case)
    got_lines = {l.id: [l.value, l.prior_year_value] for l in data.lines}
    assert got_lines == expected["lines"]
    got_segs = {f"{s.group}:{s.name}": [s.value, s.prior_year_value] for s in data.segments}
    assert got_segs == expected["segments"]
    assert str(data.period.end_date) == expected["period_end"]
    assert data.period.calendar_label == expected["calendar_label"]
    assert data.segments_status == expected["segments_status"]


@pytest.mark.parametrize("case", CASES)
def test_every_line_is_traceable(case):
    _, data = load(case)
    for l in data.lines + data.segments:
        assert l.locator.table_title and l.locator.row_label == l.label_as_printed
        assert "Three Months" in l.locator.column_current or "Quarter" in l.locator.column_current
    assert data.release.url.startswith("https://www.sec.gov/Archives/edgar/data/")


@pytest.mark.parametrize("case", CASES)
def test_fixture_validates(case):
    _, data = load(case)
    failed = [c for c in run_checks(data) if c.status == "fail"]
    assert not failed, failed


def test_shapes():
    _, apple = load("apple_fy2025q4")
    assert apple.line("cost_products") and apple.line("cost_services")  # cost split into products/services
    _, visa = load("visa_fy2025q4")
    assert visa.line("cost_of_revenue_total") is None and visa.line("gross_profit") is None  # no cost-of-revenue line
    assert visa.derived.gross_margin is None
    _, uber = load("uber_fy2022q3")
    assert uber.line("net_income").value < 0 and uber.line("operating_income").printed_negative  # net loss
    _, msft = load("microsoft_fy2026q1")
    assert {s.name for s in msft.segments} == {"Productivity and Business Processes", "Intelligent Cloud", "More Personal Computing"}
