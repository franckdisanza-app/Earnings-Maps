"""Every identity in validate.py, on a small synthetic company, including the failure paths."""

import copy

import pytest

from earnings_model import Earnings
from validate import run_checks


def loc(label):
    return {"table_title": "Statements of Operations", "row_label": label, "column_current": "Three Months Ended Sep 30, 2026", "column_prior_year": "Three Months Ended Sep 30, 2025"}


def line(id_, value, prior, label=None):
    return {"id": id_, "label_as_printed": label or id_, "value": value, "prior_year_value": prior, "locator": loc(label or id_)}


BASE = {
    "company": {"ticker": "TEST", "name": "Test Co", "cik": 1},
    "period": {"fiscal_label": "FY2026Q3", "fiscal_year": 2026, "fiscal_quarter": 3, "start_date": "2026-07-01", "end_date": "2026-09-30",
               "start_date_source": "test", "calendar_label": "Jul–Sep 2026", "display": "Fiscal Q3 2026 (Jul–Sep 2026)", "weeks": 13.1},
    "scale": "millions",
    "release": {"form": "8-K", "filing_date": "2026-10-20", "accession": "0000000001-26-000001", "url": "https://www.sec.gov/Archives/x.htm", "exhibit": "EX-99.1", "local_path": "x"},
    "lines": [
        line("revenue_a", 60, 50), line("revenue_b", 40, 30), line("revenue_total", 100, 80),
        line("cost_a", 30, 25), line("cost_b", 10, 9), line("cost_of_revenue_total", 40, 34),
        line("gross_profit", 60, 46),
        line("opex_rd", 10, 8), line("opex_sga", 15, 12), line("operating_expenses_total", 25, 20),
        line("operating_income", 35, 26),
        line("income_before_tax", 36, 27), line("income_tax", 6, 5), line("net_income", 30, 22),
    ],
    "segments_status": "in_release",
    "segments": [
        {"group": "segment", "name": "A", "label_as_printed": "A", "value": 70, "prior_year_value": 55, "locator": loc("A")},
        {"group": "segment", "name": "B", "label_as_printed": "B", "value": 30, "prior_year_value": 25, "locator": loc("B")},
    ],
    "derived": {"revenue_yoy": 100 / 80 - 1, "gross_margin": {"current": 0.6, "prior_year": 46 / 80},
                "operating_margin": {"current": 35 / 100, "prior_year": 26 / 80}, "net_margin": {"current": 30 / 100, "prior_year": 22 / 80}},
}


def status(data_dict):
    return {c.id: c.status for c in run_checks(Earnings.model_validate(data_dict))}


def with_line(d, id_, value=None, prior=None):
    d = copy.deepcopy(d)
    for l in d["lines"]:
        if l["id"] == id_:
            if value is not None:
                l["value"] = value
            if prior is not None:
                l["prior_year_value"] = prior
    return d


def test_clean_company_passes_everything():
    s = status(BASE)
    for check in ["revenue_components", "cost_components", "gross_profit", "opex_components", "operating_income", "net_income", "segments_sum:segment", "revenue_yoy", "operating_margin", "net_margin"]:
        assert s[check] == "pass", check


@pytest.mark.parametrize(
    "id_,value,prior,check",
    [
        ("revenue_a", 62, None, "revenue_components"),
        ("cost_b", 13, None, "cost_components"),
        ("gross_profit", 58, None, "gross_profit"),
        ("opex_rd", None, 11, "opex_components"),
        ("operating_income", 33, None, "operating_income"),
        ("net_income", None, 25, "net_income"),
    ],
)
def test_each_identity_catches_a_wrong_number(id_, value, prior, check):
    assert status(with_line(BASE, id_, value, prior))[check] == "fail"


def test_rounding_tolerance():
    # printed numbers are rounded: off by one unit in a 3-term identity is fine, by 3 isn't
    assert status(with_line(BASE, "gross_profit", 61))["gross_profit"] == "pass"
    assert status(with_line(BASE, "gross_profit", 63))["gross_profit"] == "fail"


def test_segments_must_sum_to_revenue():
    d = copy.deepcopy(BASE)
    d["segments"][0]["value"] = 75
    assert status(d)["segments_sum:segment"] == "fail"


def test_yoy_must_come_from_prior_year_column():
    d = copy.deepcopy(BASE)
    d["derived"]["revenue_yoy"] = 0.20
    assert status(d)["revenue_yoy"] == "fail"


def test_no_gross_profit_company_uses_costs_and_expenses():
    d = copy.deepcopy(BASE)
    d["lines"] = [line("revenue_total", 100, 80), line("cost_of_revenue_total", 40, 34), line("opex_rd", 25, 20),
                  line("costs_and_expenses_total", 65, 54), line("operating_income", 35, 26)]
    d["derived"]["gross_margin"] = None
    d["derived"]["net_margin"] = None
    s = status(d)
    assert s["gross_profit"] == "n/a"
    assert s["costs_and_expenses"] == "pass" and s["operating_income"] == "pass"


def test_operating_expenses_only_company():
    d = copy.deepcopy(BASE)
    d["lines"] = [line("revenue_total", 100, 80), line("opex_a", 20, 15), line("opex_b", 5, 5), line("operating_expenses_total", 25, 20), line("operating_income", 75, 60)]
    d["segments"], d["segments_status"] = [], "single_segment"
    d["derived"] = {"revenue_yoy": 0.25, "gross_margin": None, "operating_margin": {"current": 0.75, "prior_year": 0.75}, "net_margin": None}
    s = status(d)
    assert s["operating_income"] == "pass" and s["opex_components"] == "pass"


def test_missing_prior_year_value_fails():
    assert status(with_line(BASE, "opex_rd", prior=None) | {"lines": [l if l["id"] != "opex_rd" else {**l, "prior_year_value": None} for l in BASE["lines"]]})["prior_year_values"] == "fail"


def test_explained_exception_is_not_a_failure():
    d = with_line(BASE, "gross_profit", 58)
    d["validation_exceptions"] = [{"check": "gross_profit", "reason": "company rounds gross profit separately", "locator": "footnote 3"}]
    assert status(d)["gross_profit"] == "exception"
