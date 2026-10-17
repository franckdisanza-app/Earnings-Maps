"""Table layouts and reporting conventions met in the watchlist's releases (Coca-Cola, McDonald's,
Starbucks, PepsiCo, Disney, Walmart, Tesla), as synthetic cases."""

import copy

from earnings_model import Earnings
from find_releases import ResultsFiling, choose
from parse_release import dash_zero
from tables import extract_tables, parse_num
from test_validate import BASE, line, status


def table(html):
    (t,) = extract_tables(f"<html><body><p>STATEMENTS OF INCOME</p><p>(In millions)</p><table>{html}</table></body></html>")
    return t


def test_date_in_label_column_is_shifted_right():
    # Coca-Cola: the date row leaves out the empty cell above the labels
    t = table("""
    <tr><td colspan="3">Three Months Ended</td></tr>
    <tr><td colspan="3">July 3, 2026</td><td colspan="3">June 27, 2025</td><td colspan="3">% Fav.</td></tr>
    <tr><td colspan="3">EMEA</td><td>$</td><td colspan="2">3,240</td><td>$</td><td colspan="2">3,176</td><td colspan="3">2</td></tr>
    """)
    q = {str(c.end_date): c.index for c in t.quarter_columns()}
    row = t.find_row("EMEA")
    assert row.values[q["2026-07-03"]].value == 3240
    assert row.values[q["2025-06-27"]].value == 3176


def test_period_heading_in_label_column_applies_to_every_column():
    # McDonald's: "Quarters Ended June 30," sits in the label column, years over the numbers
    t = table("""
    <tr><td colspan="3">Quarters Ended June 30,</td><td colspan="3">2026</td><td colspan="3">2025</td><td colspan="3">Inc/ (Dec)</td></tr>
    <tr><td colspan="3">TOTAL REVENUES</td><td>$</td><td colspan="2">7,099</td><td>$</td><td colspan="2">6,843</td><td colspan="3">256</td></tr>
    """)
    q = {str(c.end_date): c.index for c in t.quarter_columns()}
    assert set(q) == {"2026-06-30", "2025-06-30"}
    row = t.find_row("TOTAL REVENUES")
    assert row.values[q["2026-06-30"]].value == 7099 and row.values[q["2025-06-30"]].value == 6843
    assert any(c.is_change for c in t.columns.values())  # "Inc/ (Dec)" is a change column


def test_numeric_dates_and_week_counts():
    # PepsiCo: "12 Weeks Ended" over "9/5/2026"
    t = table("""
    <tr><td></td><td colspan="2">12 Weeks Ended</td><td colspan="2">12 Weeks Ended</td></tr>
    <tr><td></td><td colspan="2">9/5/2026</td><td colspan="2">9/6/2025</td></tr>
    <tr><td>Net Revenue</td><td>$</td><td>25,274</td><td>$</td><td>23,937</td></tr>
    """)
    assert sorted(str(c.end_date) for c in t.quarter_columns()) == ["2025-09-06", "2026-09-05"]


def test_quarter_label_inherited_only_when_table_has_no_ytd_columns():
    # Starbucks: only the first column says "Quarter Ended"
    t = table("""
    <tr><td></td><td colspan="2">Quarter Ended</td><td colspan="2"></td></tr>
    <tr><td></td><td colspan="2">Jun 28, 2026</td><td colspan="2">Jun 29, 2025</td></tr>
    <tr><td>Net revenues</td><td></td><td>17.1</td><td></td><td>34.5</td></tr>
    """)
    assert len(t.quarter_columns()) == 2
    mixed = table("""
    <tr><td></td><td colspan="2">Quarter Ended</td><td colspan="2">Nine Months Ended</td><td colspan="2"></td></tr>
    <tr><td></td><td colspan="2">Jun 28, 2026</td><td colspan="2">Jun 28, 2026</td><td colspan="2">Jun 29, 2025</td></tr>
    <tr><td>Net revenues</td><td></td><td>17.1</td><td></td><td>82.9</td><td></td><td>65.6</td></tr>
    """)
    assert len(mixed.quarter_columns()) == 1  # the undated-duration column stays unknown


def test_printed_dash_counts_as_zero():
    n = dash_zero(parse_num("—"))
    assert n.value == 0.0 and n.text == "—"


def test_expense_printed_negative_counts_by_magnitude():
    # Disney/Netflix print costs and taxes as negative numbers
    d = copy.deepcopy(BASE)
    for l in d["lines"]:
        if l["id"] == "income_tax":
            l["value"], l["prior_year_value"], l["expense_printed_negative"] = -6, -5, True
    assert status(d)["net_income"] == "pass"


def test_consolidated_net_income_and_minority_interest():
    d = copy.deepcopy(BASE)
    d["lines"] = [l for l in d["lines"] if l["id"] != "net_income"] + [
        line("net_income_consolidated", 30, 22), line("nci", 2, -1), line("net_income", 28, 23)]
    d["derived"]["net_margin"] = {"current": 0.28, "prior_year": 23 / 80}
    s = status(d)
    assert s["net_income"] == "pass" and s["net_income_attributable"] == "pass"
    for l in d["lines"]:
        if l["id"] == "net_income":
            l["value"] = 30  # forgot to subtract the minority share
    d["derived"]["net_margin"]["current"] = 0.30
    assert status(d)["net_income_attributable"] == "fail"


def test_items_added_to_operating_income():
    # Starbucks: income from equity investees sits inside operating income
    d = copy.deepcopy(BASE)
    d["lines"] = [l for l in d["lines"] if l["id"] != "operating_income"] + [line("op_plus_equity", 2, 1), line("operating_income", 37, 27)]
    d["derived"]["operating_margin"] = {"current": 0.37, "prior_year": 27 / 80}
    assert status(d)["operating_income"] == "pass"


def test_operating_income_without_any_total_line():
    # Costco/Netflix: revenue − cost of revenue − Σ opex
    d = copy.deepcopy(BASE)
    d["lines"] = [line("revenue_total", 100, 80), line("cost_of_revenue_total", 40, 34), line("opex_sga", 25, 20), line("operating_income", 35, 26)]
    d["segments"], d["segments_status"] = [], "pending_mapping"
    d["derived"] = {"revenue_yoy": 0.25, "gross_margin": None, "operating_margin": {"current": 0.35, "prior_year": 26 / 80}, "net_margin": None}
    assert status(d)["operating_income"] == "pass"
    assert Earnings.model_validate(d).segments_status == "pending_mapping"


def rf(date, label, end, prelim=False, form="8-K"):
    return ResultsFiling("TSLA", 1, form, f"acc-{date}", date, ["2.02"], end, "", "", "", label, 2026, 2, "", "", 13.0, "", preliminary=prelim)


def test_choose_skips_preliminary_updates_and_amendments():
    filings = [
        rf("2026-10-02", "FY2026Q3", "2026-09-30", prelim=True),  # deliveries update
        rf("2026-07-25", "FY2026Q2", "2026-06-30", form="8-K/A"),
        rf("2026-07-22", "FY2026Q2", "2026-06-30"),
        rf("2026-07-02", "FY2026Q2", "2026-06-30", prelim=True),
    ]
    assert choose(filings).filing_date == "2026-07-22"  # newest period with a full release
    assert choose(filings, "FY2026Q2").filing_date == "2026-07-22"
    assert choose(filings, "FY2026Q3").filing_date == "2026-10-02"  # only a preliminary exists: return it (flagged)
    assert choose(filings, "FY2025Q4") is None
