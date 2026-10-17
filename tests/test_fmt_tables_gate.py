"""Formatting rules, table-parsing edge cases, schema sync and the Gate A tools."""

import json

import pytest

import common
from fmt import change, money, per_share, percent, yoy
from tables import extract_tables, parse_num


@pytest.mark.parametrize(
    "value,scale,expected",
    [
        (102466, "millions", "$102.5B"),
        (94930, "millions", "$94.9B"),
        (94950, "millions", "$95.0B"),  # half-up, not banker's rounding
        (1000, "millions", "$1.0B"),
        (812, "millions", "$812M"),
        (-1206, "millions", "−$1.2B"),
        (-495, "millions", "−$495M"),
    ],
)
def test_money(value, scale, expected):
    assert money(value, scale) == expected


def test_changes_and_percents():
    assert change(0.0794) == "+8%"
    assert change(-0.031) == "−3%"
    assert change(0.004) == "+0.4%"
    assert yoy(6952, 6950) == "+0.0%"  # tiny but positive keeps its sign
    assert yoy(-495, -572) == "n/m"  # change across a loss isn't meaningful
    assert per_share(-0.61) == "−$0.61"
    assert percent(0.4718, 1) == "47.2%"


def test_parse_num():
    assert parse_num("(1,234)").value == -1234
    assert parse_num("$ 94,930").value == 94930
    assert parse_num("1.85").value == 1.85
    assert parse_num("—").value is None
    assert parse_num("17%").percent
    assert parse_num("Products") is None


HTML = """
<html><body>
<p>ACME CORP</p><p>CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS</p><p>(In millions, except per share amounts)</p>
<table>
<tr><td></td><td colspan="3">Three Months Ended</td><td colspan="3">Nine Months Ended</td></tr>
<tr><td></td><td colspan="3">September 30,</td><td colspan="3">September 30,</td></tr>
<tr><td></td><td colspan="2">2025</td><td>2026</td><td colspan="2">2025</td><td>2026</td></tr>
<tr><td>Revenue:</td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td>Product</td><td>$</td><td>1,000</td><td>1,200</td><td>$</td><td>3,000</td><td>3,500</td></tr>
<tr><td>Total revenue</td><td>$</td><td>1,000</td><td>1,200</td><td>$</td><td>3,000</td><td>3,500</td></tr>
<tr><td>Loss from operations</td><td>(</td><td>50</td><td>(20)</td><td></td><td>(150)</td><td>(60)</td></tr>
</table></body></html>
"""


def test_stacked_headers_split_cells_and_old_year_first():
    (t,) = extract_tables(HTML)
    assert "STATEMENTS OF OPERATIONS" in t.title and t.scale == "millions"
    q = sorted(t.quarter_columns(), key=lambda c: c.end_date)
    assert [str(c.end_date) for c in q] == ["2025-09-30", "2026-09-30"]
    prod = t.find_row("Product", "Revenue:")
    assert prod.values[q[0].index].value == 1000 and prod.values[q[1].index].value == 1200
    loss = t.find_row("Loss from operations")
    assert loss.values[q[0].index].value == -50  # "(" in its own cell
    assert loss.values[q[1].index].value == -20
    assert t.find_row("Total revenue").section == "Revenue:"


def test_schema_file_matches_model():
    from export_schema import SCHEMA_PATH, schema_text

    assert SCHEMA_PATH.read_text(encoding="utf-8") == schema_text(), "run scripts/export_schema.py"


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    """Point the pipeline's data/ and out/ at a temp folder with one fixture quarter."""
    norm, out = tmp_path / "normalized", tmp_path / "out"
    norm.mkdir()
    monkeypatch.setattr(common, "NORMALIZED", norm)
    monkeypatch.setattr(common, "OUT", out)
    src = common.ROOT / "data" / "normalized" / "UBER-FY2022Q3.json"
    if not src.exists():
        pytest.skip("run parse_release.py UBER FY2022Q3 first")
    (norm / "UBER-FY2022Q3.json").write_bytes(src.read_bytes())
    return norm, out


def test_gate_a_refuses_without_audit(sandbox):
    import approve

    assert approve.approve("UBER-FY2022Q3", "Owner") == 1
    assert not (sandbox[0] / "UBER-FY2022Q3.approval.json").exists()


def test_gate_a_full_cycle(sandbox):
    import approve
    import audit_diff

    norm, out = sandbox
    aud = common.ROOT / "out" / "UBER-FY2022Q3" / "auditor.json"
    if not aud.exists():
        pytest.skip("no auditor.json")
    md, summary = audit_diff.diff("UBER-FY2022Q3", aud)
    assert summary["unresolved"] == 0
    (out / "UBER-FY2022Q3").mkdir(parents=True)
    (out / "UBER-FY2022Q3" / "audit.json").write_text(json.dumps(summary), encoding="utf-8")

    assert approve.approve("UBER-FY2022Q3", "Owner") == 0
    ok, _ = approve.verify("UBER-FY2022Q3")
    assert ok

    # any edit after approval breaks the gate
    p = norm / "UBER-FY2022Q3.json"
    p.write_text(p.read_text(encoding="utf-8").replace('"value": 8343.0', '"value": 8344.0', 1), encoding="utf-8")
    ok, msg = approve.verify("UBER-FY2022Q3")
    assert not ok and "changed after approval" in msg


def test_audit_catches_a_mismatch(sandbox, tmp_path):
    import audit_diff

    aud = json.loads((common.ROOT / "out" / "UBER-FY2022Q3" / "auditor.json").read_text(encoding="utf-8"))
    aud["items"][0]["value_current"] = 8334  # transposed digits
    bad = tmp_path / "auditor-bad.json"
    bad.write_text(json.dumps(aud), encoding="utf-8")
    _, summary = audit_diff.diff("UBER-FY2022Q3", bad)
    assert summary["unresolved"] == 1 and summary["mismatched"] == ["revenue_total"]


def test_auditor_request_reveals_no_values_or_labels():
    import audit_diff
    from earnings_model import Earnings

    data = Earnings.model_validate_json((common.ROOT / "data" / "normalized" / "UBER-FY2022Q3.json").read_text(encoding="utf-8"))
    req = audit_diff.request(data)
    for l in data.lines:
        assert f"{l.value:,.0f}" not in req and str(int(abs(l.value))) not in req.replace("2022-09-30", "")
    assert "Cost of revenue, exclusive" not in req and "Loss from operations" not in req
