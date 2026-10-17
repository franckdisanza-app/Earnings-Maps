"""Build the money map's view model from a normalized data file.

    python scripts/money_map_model.py <ID>            # writes out/<ID>/build/model.json

The model is the only thing the template reads: nodes and flows in dollars, every on-screen
string already formatted by fmt.py (so videos, captions and the numbers sheet agree), and
every subtotal we compute marked "our calculation".

The story is the income statement read top to bottom: segments → revenue → gross profit →
operating income → net income, with a cost peeling off at each step. A step the company
doesn't report is skipped; the cost of a step is printed when a company line matches it,
otherwise it is our calculation.
"""

from __future__ import annotations

import json
import sys

from common import company, data_path, out_dir
from earnings_model import Earnings
import json as _json

from fmt import change, change_spoken, money, money_spoken, percent, to_units


def units(v, scale):
    return float(to_units(v, scale)) if v is not None else None


def build(id_: str) -> dict:
    data = Earnings.model_validate_json(data_path(id_).read_text(encoding="utf-8"))
    entry = company(data.company.ticker)
    L = {l.id: l for l in data.lines}
    comp = {c.id: c for c in data.derived.computed_lines}

    def val(i, prior=False):
        l = L.get(i)
        if l is None:
            return None
        v = l.prior_year_value if prior else l.value
        if v is not None and l.expense_printed_negative:
            v = -v
        return units(v, l.scale)

    def tol(i):
        return float(to_units(1.5, L[i].scale)) if i in L else 1.5e6

    rev = val("revenue_total")
    rev_p = val("revenue_total", True)
    nodes, links, notes = [], [], []

    def node(id_, label, value, kind, *, note=None, change_text=None, share=None, printed_id=None):
        nodes.append({
            "id": id_, "label": label, "value": value, "display": money(value, "units"), "kind": kind,
            "note": note, "change": change_text, "share": share, "printed": printed_id,
        })

    def yoy(cur, prior):
        if cur is None or not prior or prior <= 0 or cur <= 0:
            return None
        return change(cur / prior - 1)

    # Segments (the breakdown chosen in the watchlist), only when they sum to revenue with no negatives.
    group = entry.get("show_segments")
    segs = [s for s in data.segments if s.group == group] if group else []
    if segs and all(s.value > 0 for s in segs):
        total = sum(units(s.value, s.scale) for s in segs)
        if abs(total - rev) <= float(to_units(0.5 * (len(segs) + 1), segs[0].scale)):
            short = {i.get("name"): i.get("short") for g in entry.get("segments", []) for i in g.get("items", [])}
            for s in segs:
                v = units(s.value, s.scale)
                node(f"seg:{s.name}", short.get(s.name) or s.name, v, "segment",
                     change_text=yoy(v, units(s.prior_year_value, s.scale)), printed_id=f"segment:{s.group}:{s.name}")
                links.append({"source": f"seg:{s.name}", "target": "revenue", "value": v, "kind": "revenue"})
        else:
            notes.append(f"segments ({group}) don't sum to revenue; segment row skipped")
    elif segs:
        notes.append("segment breakdown has negative items (eliminations or hedging); segment row skipped")

    node("revenue", "Revenue", rev, "revenue", change_text=yoy(rev, rev_p), printed_id="revenue_total")

    # The profit chain, top to bottom.
    chain = [("revenue", rev)]
    if "gross_profit" in L:
        chain.append(("gross_profit", val("gross_profit")))
    elif "gross_profit" in comp:
        chain.append(("gross_profit", units(comp["gross_profit"].value, comp["gross_profit"].scale)))
    if "operating_income" in L:
        chain.append(("operating_income", val("operating_income")))
    elif "income_before_tax" in L:
        chain.append(("income_before_tax", val("income_before_tax")))
    if "net_income" in L:
        chain.append(("net_income", val("net_income")))

    labels = {"gross_profit": "Gross profit", "operating_income": "Operating income", "income_before_tax": "Pre-tax income", "net_income": "Net income"}
    loss_labels = {"operating_income": "Operating loss", "income_before_tax": "Pre-tax loss", "net_income": "Net loss"}

    def opex_total():
        if "operating_expenses_total" in L:
            return val("operating_expenses_total"), "operating_expenses_total", "Operating expenses"
        parts = [i for i in L if i.startswith("opex_")]
        if parts:
            return sum(val(i) for i in parts), None, "Operating expenses"
        return None, None, None

    def cost_step(parent_id, child_id, parent_v, child_v):
        """The cost between two chain levels: a printed line when one matches, else our calculation."""
        gap = parent_v - child_v
        if parent_id == "revenue" and child_id == "gross_profit":
            if "cost_of_revenue_total" in L and abs(val("cost_of_revenue_total") - gap) <= tol("cost_of_revenue_total"):
                return "Cost of revenue", None, "cost_of_revenue_total"
            return "Cost of revenue", "our calculation", None
        if child_id in ("operating_income", "income_before_tax"):
            candidates = []
            if parent_id == "gross_profit":
                v, pid, label = opex_total()
                if v is not None:
                    candidates.append((v, pid, label))
            else:
                for pid, label in (("costs_and_expenses_total", "Costs and expenses"), ("operating_expenses_total", "Operating expenses")):
                    if pid in L:
                        candidates.append((val(pid), pid, label))
            for v, pid, label in candidates:
                if abs(v - gap) <= (tol(pid) if pid else 3e6):
                    return label, (None if pid else "our calculation"), pid
            return ("Operating expenses" if parent_id == "gross_profit" else "Costs and expenses"), "our calculation", None
        if child_id == "net_income":
            if "income_tax" in L and abs(val("income_tax") - gap) <= tol("income_tax"):
                return "Income tax", None, "income_tax"
            return "Tax and other", "our calculation", None
        return "Costs", "our calculation", None

    for (pid, pv), (cid, cv) in zip(chain, chain[1:]):
        if pv is None or cv is None:
            break
        if pv <= 0:
            # Below a loss the flow picture stops; the loss line is shown as text.
            notes.append(f"{cid} after a loss is shown as text only")
            break
        if cv >= 0:
            if cid != "revenue":
                share = percent(cv / rev, 0) + " of revenue" if rev else None
                comp_note = "our calculation" if (cid == "gross_profit" and "gross_profit" not in L) else None
                node(cid, labels[cid], cv, "profit", note=comp_note, share=share, printed_id=cid if cid in L else None)
            if cv <= pv:
                label, note, printed = cost_step(pid, cid, pv, cv)
                if pv - cv > 0:
                    node(f"cost:{cid}", label, pv - cv, "cost", note=note, printed_id=printed)
                    links.append({"source": pid, "target": f"cost:{cid}", "value": pv - cv, "kind": "cost"})
                links.append({"source": pid, "target": cid, "value": cv, "kind": "profit"})
            else:
                # Net income above operating income: other income adds to it.
                node(f"other:{cid}", "Other income, net", cv - pv, "other", note="our calculation")
                links.append({"source": pid, "target": cid, "value": pv, "kind": "profit"})
                links.append({"source": f"other:{cid}", "target": cid, "value": cv - pv, "kind": "other"})
        else:
            # A loss: costs exceed the parent; the shortfall is a hatched loss node feeding the costs.
            label, note, printed = cost_step(pid, cid, pv, cv)
            node(f"cost:{cid}", label, pv - cv, "cost", note=note, printed_id=printed)
            node(cid, loss_labels.get(cid, "Loss"), -cv, "loss", printed_id=cid if cid in L else None)
            links.append({"source": pid, "target": f"cost:{cid}", "value": pv, "kind": "cost"})
            links.append({"source": cid, "target": f"cost:{cid}", "value": -cv, "kind": "loss"})
            break

    # One insight: the fastest-growing big segment, else the operating-margin change.
    insight = None
    # Growth the auditor flagged as not like-for-like (acquisitions, one-off benefits) isn't an insight.
    audit_file = out_dir(id_) / "audit.json"
    warnings = _json.loads(audit_file.read_text(encoding="utf-8")).get("auditor_warnings", []) if audit_file.exists() else []
    flags = ("acquisition", "acquired", "like-for-like", "not comparable", "benefit", "one-time", "one-off", "accrual release")
    def flagged(name):
        return any(name.lower() in w.lower() and any(f in w.lower() for f in flags) for w in warnings)
    seg_nodes = [n for n in nodes if n["kind"] == "segment" and n["change"] and n["value"] >= 0.1 * rev and not flagged(n["label"])]
    rev_growth = rev / rev_p - 1 if rev_p else None
    growth = {}
    for s in segs:
        v, p = units(s.value, s.scale), units(s.prior_year_value, s.scale)
        if p and p > 0:
            growth[f"seg:{s.name}"] = v / p - 1
    if seg_nodes and rev_growth is not None:
        best = max(seg_nodes, key=lambda n: growth.get(n["id"], -9))
        if growth.get(best["id"], -9) > rev_growth:
            insight = {"node": best["id"], "headline": f"{best['label']} grew {change(growth[best['id']]).lstrip('+')}",
                       "sub": f"vs {change(rev_growth).lstrip('+')} for all revenue",
                       "spoken": f"{best['label']} grew {change_spoken(growth[best['id']]).replace('up ', '')}. Revenue grew {change_spoken(rev_growth).replace('up ', '')}."}
    if insight is None and data.derived.operating_margin and data.derived.operating_margin.current is not None and data.derived.operating_margin.prior_year is not None:
        om = data.derived.operating_margin
        diff = (om.current - om.prior_year) * 100
        direction = "up" if diff > 0 else "down"
        insight = {"node": "operating_income", "headline": f"Operating margin {percent(om.current, 1)}",
                   "sub": f"{direction} from {percent(om.prior_year, 1)} a year ago",
                   "spoken": f"Operating margin was {percent(om.current, 1).replace('%', ' percent').replace(chr(0x2212), 'minus ')}, {direction} from {percent(om.prior_year, 1).replace('%', ' percent').replace(chr(0x2212), 'minus ')} a year ago."}

    # ---- voiceover: one short line per beat, narrating what's left at each step -------------
    # The costs are labelled on screen; the voice follows the profit spine so the video stays
    # inside 25-35 s (Kokoro needs over a second for a number like "102.5 billion").
    by = {n["id"]: n for n in nodes}
    voice = [{"beat": "hook", "nodes": [], "text": f"{data.company.name} made {money_spoken(rev, unit_word=True)} in three months."}]
    seg_ns = sorted([n for n in nodes if n["kind"] == "segment"], key=lambda n: -n["value"])
    if seg_ns:
        lead = seg_ns[0]
        text = f"Most of it from {lead['label']}: {money_spoken(lead['value'])}." if lead["value"] > 0.5 * rev else f"{lead['label']} led with {money_spoken(lead['value'])}."
        voice.append({"beat": "row", "nodes": [n["id"] for n in seg_ns], "text": text})
    voice.append({"beat": "row", "nodes": ["revenue"], "text": (f"That's {change_spoken(rev / rev_p - 1)} on a year ago." if rev_p and rev_p > 0 else "That's all revenue.")})
    for cid in [c[0] for c in chain[1:]]:
        n = by.get(cid)
        cost = by.get(f"cost:{cid}")
        if n is None and cost is None:
            continue
        ids = [i for i in (cid, f"cost:{cid}", f"other:{cid}") if i in by]
        if n and n["kind"] == "loss":
            voice.append({"beat": "row", "nodes": ids, "text": f"Costs topped revenue: an {n['label'].lower()} of {money_spoken(n['value'])}."})
            break
        voice.append({"beat": "row", "nodes": ids, "text": f"{n['label']}: {money_spoken(n['value'])}."})
    if insight:
        voice.append({"beat": "insight", "nodes": [insight["node"]], "text": insight.get("spoken") or f"{insight['headline']}."})
    voice.append({"beat": "end", "nodes": [], "text": "Not investment advice."})

    # ---- carousel data: segments, margins, cents of each dollar, sources ---------------------
    carousel = {"segments": [], "margins": [], "dollar": [], "sources": {}}
    for n in sorted([n for n in nodes if n["kind"] == "segment"], key=lambda n: -n["value"]):
        carousel["segments"].append({"name": n["label"], "display": n["display"], "change": n["change"], "value": n["value"]})
    d = data.derived
    for label, ratio in (("Gross margin", d.gross_margin), ("Operating margin", d.operating_margin), ("Net margin", d.net_margin)):
        if ratio and ratio.current is not None and ratio.prior_year is not None:
            carousel["margins"].append({"label": label, "current": ratio.current, "prior": ratio.prior_year,
                                        "current_display": percent(ratio.current, 1), "prior_display": percent(ratio.prior_year, 1),
                                        "our_calculation": label == "Gross margin" and "gross_profit" not in L})
    # cents of each dollar: only when every step is positive and nothing is added below revenue
    parts = [n for n in nodes if n["kind"] == "cost"] + [n for n in nodes if n["id"] == "net_income" and n["kind"] == "profit"]
    if parts and not any(n["kind"] in ("loss", "other") for n in nodes) and abs(sum(n["value"] for n in parts) - rev) <= 3e6:
        raw = [n["value"] / rev * 100 for n in parts]
        cents = [int(x) for x in raw]
        for i in sorted(range(len(raw)), key=lambda i: raw[i] - cents[i], reverse=True)[: 100 - sum(cents)]:
            cents[i] += 1  # largest remainder, so the cents add up to exactly 100
        carousel["dollar"] = [{"label": n["label"], "cents": cnt, "kind": n["kind"]} for n, cnt in zip(parts, cents)]
    carousel["sources"] = {"form": data.release.form, "filed": data.release.filing_date.isoformat(), "accession": data.release.accession,
                           "exhibit": data.release.exhibit, "url": data.release.url}

    p, r, c = data.period, data.release, data.company
    filed = r.filing_date.strftime("%b %-d, %Y") if sys.platform != "win32" else r.filing_date.strftime("%b %#d, %Y")
    bases = {l.basis for l in data.lines}
    return {
        "id": id_,
        "company": {"name": c.name, "ticker": c.ticker},
        "period_display": p.display,
        "source_line": f"Source: {c.name} earnings release, filed {filed}",
        "basis_line": "All figures GAAP" if bases == {"GAAP"} else "Includes non-GAAP figures (labeled)",
        "disclaimer": "Not investment advice",
        "hook": {"pre": f"{c.name} made", "number": money(rev, "units"), "post": "in 3 months.", "sub": "Here's where every dollar went.",
                 "line": f"{c.name} made {money(rev, 'units')} in 3 months."},
        "insight": insight,
        "cta": "Follow for more maps",
        "voice": voice,
        "carousel": carousel,
        "nodes": nodes,
        "links": links,
        "notes": notes + list(data.notes),
        "data_file": f"data/normalized/{id_}.json",
    }


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print(__doc__)
        return 2
    id_ = args[0]
    model = build(id_)
    out = out_dir(id_) / "build"
    out.mkdir(parents=True, exist_ok=True)
    (out / "model.json").write_text(json.dumps(model, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote out/{id_}/build/model.json ({len(model['nodes'])} nodes, {len(model['links'])} flows)")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
