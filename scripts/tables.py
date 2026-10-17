"""Extract tables from an EDGAR HTML exhibit into grids with column periods.

EDGAR earnings tables split one printed value across cells ("$", "94,930", ")"), put the
period in stacked header rows ("Three Months Ended September 27," over "2025"), and use
colspan to line headers up with numbers. This module expands colspans into a grid, reads
each data column's header to get its period (duration + end date), and turns cells into
numbers while keeping the printed text.

    python scripts/tables.py <exhibit.htm> [--grep TEXT]   # print what was found
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from dataclasses import dataclass, field

import lxml.html
from lxml import etree

BLOCK_TAGS = {"p", "div", "br", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "li", "table", "center"}
MONTHS = {m: i for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"], 1)}
MONTH_ABBR = {k[:3]: v for k, v in MONTHS.items()} | {"sept": 9}
DATE_RE = re.compile(r"(January|February|March|April|May|June|July|August|September|Sept?\.?|October|November|December|Jan\.?|Feb\.?|Mar\.?|Apr\.?|Jun\.?|Jul\.?|Aug\.?|Oct\.?|Nov\.?|Dec\.?)\s+(\d{1,2}),?\s*(\d{4})", re.I)
DURATION_RE = re.compile(r"\b(three|six|nine|twelve|3|6|9|12)[\s-]+months?\b|\bquarters?\b|\b(\d{1,2})[\s-]+weeks?\b|\b(fiscal\s+)?years?\s+ended\b", re.I)
NUM_RE = re.compile(r"^\(?\s*-?\s*\$?\s*\(?\s*(\d{1,3}(?:,\d{3})+|\d+)(\.\d+)?\s*\)?\s*%?\s*\)?$")
DASH = {"—", "–", "-", "— ", "−"}
MONTH_DAY_RE = re.compile(r"(January|February|March|April|May|June|July|August|September|October|November|December|Sept?\.?|Jan\.?|Feb\.?|Mar\.?|Apr\.?|Jun\.?|Jul\.?|Aug\.?|Oct\.?|Nov\.?|Dec\.?)\s+\d{1,2},?(\s|$)", re.I)
NUMDATE_RE = re.compile(r"(?<![\d/])(\d{1,2})/(\d{1,2})/(\d{4}|\d{2})(?![\d/])")
SCALE_RE = re.compile(r"\bin\s+(millions|thousands|billions)\b", re.I)


def clean(text: str) -> str:
    text = text.replace("\xa0", " ").replace("​", "").replace(" ", " ")
    return re.sub(r"\s+", " ", text).strip()


@dataclass
class Num:
    value: float | None  # None for a printed dash
    text: str
    negative: bool
    percent: bool


def parse_num(text: str, open_paren_before: bool = False) -> Num | None:
    t = clean(text)
    if t in DASH:
        return Num(None, t, False, False)
    if not t or not NUM_RE.match(t):
        return None
    digits = re.sub(r"[^\d.]", "", t)
    if not digits or digits == ".":
        return None
    neg = t.startswith("(") or "(" in t[:3] or t.lstrip("$ ").startswith("-") or (open_paren_before and not t.startswith("("))
    val = float(digits)
    return Num(-val if neg else val, t, neg, t.endswith("%") or t.endswith("%)"))


@dataclass
class Column:
    index: int
    header: str
    end_date: dt.date | None
    months: int | None  # 3 for a quarter, 12 for a year, None if unknown
    is_change: bool


@dataclass
class Row:
    index: int
    label: str
    section: str | None
    values: dict[int, Num] = field(default_factory=dict)


@dataclass
class Table:
    index: int
    title: str
    context: list[str]
    grid: list[list[str]]
    header_rows: list[int]
    columns: dict[int, Column]
    rows: list[Row]
    scale: str | None
    exhibit: str | None = None  # set by parse_release when the table comes from a second exhibit

    def quarter_columns(self) -> list[Column]:
        return [c for c in self.columns.values() if c.months == 3 and not c.is_change and c.end_date]

    def find_row(self, label: str, section: str | None = None) -> Row | None:
        hits = [r for r in self.rows if r.label == label and (section is None or r.section == section)]
        return hits[0] if hits else None


def parse_date(text: str) -> dt.date | None:
    m = DATE_RE.search(text)
    if not m:
        n = NUMDATE_RE.search(text)
        if not n:
            return None
        year = int(n.group(3))
        year = year + 2000 if year < 100 else year
        try:
            return dt.date(year, int(n.group(1)), int(n.group(2)))
        except ValueError:
            return None
    name = m.group(1).lower().rstrip(".")
    month = MONTHS.get(name) or MONTH_ABBR.get(name[:4] if name.startswith("sept") else name[:3])
    try:
        return dt.date(int(m.group(3)), month, int(m.group(2)))
    except (TypeError, ValueError):
        return None


def parse_months(text: str) -> int | None:
    m = DURATION_RE.search(text)
    if not m:
        return None
    word = (m.group(1) or "").lower()
    if word:
        return {"three": 3, "six": 6, "nine": 9, "twelve": 12}.get(word, int(word) if word.isdigit() else None)
    if m.group(2):  # N weeks
        weeks = int(m.group(2))
        return 3 if weeks <= 17 else 6 if weeks <= 28 else 9 if weeks <= 40 else 12
    if "quarter" in m.group(0).lower():
        return 3
    return 12  # "year ended"


def _text_blocks(doc) -> tuple[list[str], dict]:
    """Document-order text blocks outside tables, and for each table the blocks before it."""
    blocks: list[str] = []
    current: list[str] = []
    before: dict = {}
    depth = 0

    def flush():
        if current:
            t = clean(" ".join(current))
            if t:
                blocks.append(t)
            current.clear()

    since = 0  # first block after the previous table
    for event, el in etree.iterwalk(doc, events=("start", "end")):
        tag = el.tag if isinstance(el.tag, str) else ""
        if event == "start":
            if tag == "table":
                if depth == 0:
                    flush()
                    before[el] = list(blocks[since:][-6:])
                depth += 1
            elif depth == 0:
                if tag in BLOCK_TAGS:
                    flush()
                if el.text:
                    current.append(el.text)
        else:
            if tag == "table":
                depth -= 1
                if depth == 0:
                    since = len(blocks)
            elif depth == 0 and tag in BLOCK_TAGS:
                flush()
            if depth == 0 and el.tail:
                current.append(el.tail)
    flush()
    return blocks, before


def _grid(table) -> tuple[list[list[str]], list[list[int]]]:
    grid, origin = [], []
    for tr in table.iter("tr"):
        if tr.getparent() is not None and any(p.tag == "table" and p is not table for p in tr.iterancestors("table") if p is not table and False):
            continue
        row, orow = [], []
        for cell in tr:
            if not isinstance(cell.tag, str) or cell.tag not in ("td", "th"):
                continue
            text = clean(cell.text_content())
            try:
                span = max(1, int(cell.get("colspan", "1")))
            except ValueError:
                span = 1
            start = len(row)
            for _ in range(span):
                row.append(text)
                orow.append(start)
        grid.append(row)
        origin.append(orow)
    width = max((len(r) for r in grid), default=0)
    for r, o in zip(grid, origin):
        while len(r) < width:
            o.append(len(r))
            r.append("")
    return grid, origin


def _is_year(text: str) -> bool:
    return bool(re.fullmatch(r"(19|20)\d{2}", text))


def build_table(index: int, el, context: list[str]) -> Table | None:
    grid, origin = _grid(el)
    if not grid or len(grid[0]) < 2:
        return None
    # Parse every row into label + numbers (origin cells only, so colspans count once).
    parsed: list[tuple[str, dict[int, Num]]] = []
    for r, (row, orow) in enumerate(zip(grid, origin)):
        label, values, open_paren = "", {}, False
        seen = set()
        for c, (text, o) in enumerate(zip(row, orow)):
            if o in seen:
                continue
            seen.add(o)
            if not text:
                continue
            if text in ("(", "$(", "$ ("):
                open_paren = True
                continue
            num = parse_num(text, open_paren)
            open_paren = False
            if num is None:
                if not label and not values and text not in ("$", ")", "%", ")%"):
                    label = text
                continue
            values[o] = num
        parsed.append((label, values))

    def is_data(label: str, values: dict[int, Num]) -> bool:
        return bool(label) and any(v.value is not None and not _is_year(v.text) for v in values.values())

    first_data = next((i for i, (l, v) in enumerate(parsed) if is_data(l, v)), None)
    if first_data is None:
        return None
    def periodish(i: int) -> bool:
        joined = " ".join(grid[i])
        return bool(DATE_RE.search(joined) or NUMDATE_RE.search(joined) or MONTH_DAY_RE.search(joined) or DURATION_RE.search(joined) or any(_is_year(x) for x in grid[i])
                    or re.search(r"\bended\b|\bchange\b|%", joined, re.I))

    # Before the first data row: period rows are headers; a lone label ("Net sales:") is a
    # section heading for the rows below; anything else is title text.
    header_rows, pre_sections, title_rows = [], [], []
    for i in range(first_data):
        if not any(grid[i]):
            continue
        label, values = parsed[i]
        if periodish(i):
            header_rows.append(i)
        elif label and not values and header_rows:
            pre_sections.append(label)
        else:
            title_rows.append(i)
    # Some filers leave out the empty cell above the row labels in a header row, so its
    # dates sit one column group too far left. A header row whose first cell holds period
    # text, while data rows keep their label there, gets shifted right by the label width.
    label_span = 0
    while label_span < len(origin[first_data]) and origin[first_data][label_span] == 0:
        label_span += 1
    width = len(grid[0])
    prefix: dict[int, str] = {}  # a period heading in the label column applies to every column of its row
    for hr in header_rows:
        first = grid[hr][0]
        if not first or not label_span:
            continue
        if DATE_RE.search(first) or NUMDATE_RE.search(first) or _is_year(first):
            grid[hr] = ([""] * label_span + grid[hr])[:width]  # one column's date sitting in the label column
        elif MONTH_DAY_RE.search(first) or DURATION_RE.search(first):
            prefix[hr] = first
            grid[hr] = [""] * label_span + grid[hr][label_span:]
    data_cols = sorted({c for l, v in parsed[first_data:] for c in v})
    columns: dict[int, Column] = {}
    for c in data_cols:
        parts = []
        for hr in header_rows:
            t = grid[hr][c] if c < len(grid[hr]) else ""
            if not t:
                # header cell may sit just left of the number (e.g. over the "$" cell)
                k = c - 1
                while k >= 0 and not grid[hr][k] and k > c - 3:
                    k -= 1
                t = grid[hr][k] if k >= 0 and k > c - 3 else ""
            if hr in prefix:
                t = f"{prefix[hr]} {t}".strip()
            if t and (not parts or parts[-1] != t):
                parts.append(t)
        header = clean(" ".join(parts))
        # Header rows above the period may carry a durations row shared by several columns.
        columns[c] = Column(
            index=c,
            header=header,
            end_date=parse_date(header),
            months=parse_months(header),
            is_change=bool(re.search(r"change|%|growth|variance|inc\.?\s*/\s*\(?\s*dec|fav\.?\s*/", header, re.I)),
        )
    # A printed value often spans two grid columns ("$" in one, the number in the next), so
    # merge consecutive data columns with the same header into one logical column.
    group_of: dict[int, int] = {}
    merged: dict[int, Column] = {}
    prev = None
    for c in data_cols:
        col = columns[c]
        if prev is not None and col.header == columns[prev].header and c - prev <= 2:
            group_of[c] = group_of[prev]
        else:
            group_of[c] = c
            merged[c] = col
        prev = c
    columns = merged
    # Only the first column says "Quarter Ended" in some tables. If every labeled column in
    # the table is a quarter, dated columns without a duration are quarters too. Tables
    # that also have year-to-date columns are left alone.
    durations = {c.months for c in columns.values() if c.months and not c.is_change}
    if durations == {3}:
        for c in columns.values():
            if c.months is None and c.end_date and not c.is_change:
                c.months = 3

    rows: list[Row] = []
    section = pre_sections[-1] if pre_sections else None
    for i in range(first_data, len(parsed)):
        label, values = parsed[i]
        if not label and not values:
            continue
        real: dict[int, Num] = {}
        for c, v in values.items():
            g = group_of.get(c)
            if g is not None and g not in real:
                real[g] = v
        if label and not real:
            section = label
            continue
        if label:
            rows.append(Row(i, label, section, real))
            if label.lower().startswith("total"):
                section = None  # a "Total ..." row closes its block
    title_parts = [t for t in context if len(t) < 300] + [clean(" ".join(dict.fromkeys(t for t in grid[h] if t))) for h in title_rows]
    title = " | ".join(t for t in title_parts if t)
    scale_m = SCALE_RE.search(title) or SCALE_RE.search(" ".join(" ".join(grid[h]) for h in header_rows))
    return Table(index, title, context, grid, header_rows, columns, rows, scale_m.group(1).lower() if scale_m else None)


def extract_tables(html: bytes | str) -> list[Table]:
    doc = lxml.html.fromstring(html)
    _, before = _text_blocks(doc)
    tables = []
    carry: list[str] = []  # text of layout tables (some filers put statement titles in one)
    for i, el in enumerate(doc.iter("table")):
        if any(a.tag == "table" for a in el.iterancestors()):
            continue
        context = before.get(el, [])
        t = build_table(i, el, (carry[-3:] + context)[-6:] if not context else context if not carry else (carry[-3:] + context)[-6:])
        if t:
            tables.append(t)
            carry = []
        else:
            text = clean(el.text_content())
            if text and len(text) < 400:
                carry.append(text)
    return tables


def describe(t: Table) -> str:
    out = [f"## table {t.index}  scale={t.scale}", f"title: {t.title[:400]}"]
    for c in t.columns.values():
        out.append(f"  col {c.index:>3}: months={c.months} end={c.end_date} change={c.is_change}  [{c.header[:90]}]")
    for r in t.rows:
        vals = "  ".join(f"{c}:{v.text}" for c, v in r.values.items())
        out.append(f"  row {r.index:>3} [{r.section or ''}] > {r.label[:70]!r}  {vals[:120]}")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--grep", default="", help="only tables whose title or rows contain this text")
    args = ap.parse_args()
    data = open(args.path, "rb").read()
    for t in extract_tables(data):
        blob = t.title + " " + " ".join(r.label for r in t.rows)
        if args.grep.lower() in blob.lower():
            print(describe(t))
            print()
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
