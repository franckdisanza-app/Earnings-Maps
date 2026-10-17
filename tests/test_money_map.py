"""Money map view model and layout: correct story, labelled calculations, deterministic geometry
that keeps every label inside the safe zone and off the bars."""

import json
import subprocess

import pytest

import common
from money_map_model import build

ROOT = common.ROOT


def model(id_):
    if not common.data_path(id_).exists():
        pytest.skip(f"{id_} not normalized")
    return build(id_)


def test_apple_story_and_labels():
    m = model("AAPL-FY2025Q4")
    ids = [n["id"] for n in m["nodes"]]
    assert ids[:5] == ["seg:iPhone", "seg:Mac", "seg:iPad", "seg:Wearables, Home and Accessories", "seg:Services"]
    by = {n["id"]: n for n in m["nodes"]}
    assert by["revenue"]["display"] == "$102.5B" and by["revenue"]["change"] == "+8%"
    assert by["gross_profit"]["note"] is None  # Apple prints gross margin
    assert by["cost:net_income"]["label"] == "Tax and other" and by["cost:net_income"]["note"] == "our calculation"
    assert by["net_income"]["share"] == "27% of revenue" and by["net_income"]["change"] is None  # margin, not YoY
    assert by["seg:Wearables, Home and Accessories"]["label"] == "Wearables"  # display short name
    assert m["hook"]["number"] == "$102.5B" and m["insight"]["node"] == "seg:Services"
    # flows conserve value at every node
    for n in m["nodes"]:
        inflow = sum(l["value"] for l in m["links"] if l["target"] == n["id"])
        outflow = sum(l["value"] for l in m["links"] if l["source"] == n["id"])
        if inflow and outflow:
            assert abs(inflow - outflow) <= 2e6, n["id"]


def test_loss_is_hatched_cost_story():
    m = model("UBER-FY2022Q3")
    by = {n["id"]: n for n in m["nodes"]}
    assert by["operating_income"]["kind"] == "loss" and by["operating_income"]["label"] == "Operating loss"
    assert {l["kind"] for l in m["links"] if l["target"] == "cost:operating_income"} == {"cost", "loss"}


def test_no_gross_profit_company_goes_straight_to_operating_income():
    m = model("V-FY2025Q4")
    assert "gross_profit" not in {n["id"] for n in m["nodes"]}
    assert {l["target"] for l in m["links"] if l["source"] == "revenue"} == {"operating_income", "cost:operating_income"}


def run_layout(id_):
    m = model(id_)
    out = common.out_dir(id_) / "build"
    out.mkdir(parents=True, exist_ok=True)
    (out / "model.json").write_text(json.dumps(m, ensure_ascii=False), encoding="utf-8")
    subprocess.run(["node", "scripts/layout.mjs", id_], cwd=ROOT, check=True, capture_output=True)
    return (out / "layout.json").read_text(encoding="utf-8")


@pytest.mark.parametrize("id_", ["AAPL-FY2025Q4", "MSFT-FY2026Q1", "V-FY2025Q4", "UBER-FY2022Q3"])
def test_layout_is_deterministic_and_inside_the_safe_zone(id_):
    first = run_layout(id_)
    assert run_layout(id_) == first  # same data, same bytes
    lay = json.loads(first)
    tokens = json.loads((ROOT / "brand" / "tokens.json").read_text(encoding="utf-8"))
    safe = tokens["safe_zone_9x16"]
    x0, x1 = safe["left_px"], 1080 - safe["right_px"]
    y0, y1 = safe["top_px"], 1920 - safe["bottom_px"]
    for t in lay["labels"]:
        assert t["size"] >= 34
        assert y0 <= t["y"] <= y1, t
        if t["anchor"] == "start":
            assert t["x"] >= x0 - 1, t
        if t["anchor"] == "end":
            assert t["x"] <= x1 + 1, t
    for n in lay["nodes"]:
        assert n["x"] >= x0 - 1 and n["x"] + n["w"] <= x1 + 1


def test_apple_layout_has_no_warnings_and_no_label_on_a_bar():
    lay = json.loads(run_layout("AAPL-FY2025Q4"))
    assert lay["warnings"] == []
    bars = [(n["x"], n["y"], n["x"] + n["w"], n["y"] + n["h"], n["id"]) for n in lay["nodes"]]
    for t in lay["labels"]:
        if t["role"] == "on-fill":
            continue  # inside its own bar on purpose
        for bx0, by0, bx1, by1, nid in bars:
            inside_x = bx0 + 2 < t["x"] < bx1 - 2
            inside_y = by0 + 2 < t["y"] < by1 + 8
            assert not (inside_x and inside_y), (t["text"], nid)
