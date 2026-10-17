"""Normalized earnings data model (pydantic). `schemas/earnings.schema.json` is generated
from this file by `scripts/export_schema.py`; a test keeps the two in sync.

Values are stored exactly as printed, in the scale named on the line (usually the table's
"in millions"). Nothing here is rounded for display; formatting happens in fmt.py.
"""

from __future__ import annotations

import datetime as dt
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Scale = Literal["units", "thousands", "millions", "billions"]
Basis = Literal["GAAP", "non-GAAP"]
Unit = Literal["USD", "USD/share", "shares", "percent", "count"]


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Company(Strict):
    ticker: str
    name: str
    cik: int


class Period(Strict):
    fiscal_label: str = Field(pattern=r"^FY\d{4}Q[1-4]$")
    fiscal_year: int
    fiscal_quarter: int = Field(ge=1, le=4)
    start_date: dt.date
    end_date: dt.date
    start_date_source: str = Field(description="how start_date was established, e.g. 'prior 10-Q reportDate + 1 day'")
    calendar_label: str = Field(description="e.g. 'Jul–Sep 2025'")
    display: str = Field(description="on-screen label, e.g. 'Fiscal Q4 2025 (Jul–Sep 2025)'")
    weeks: float


class Release(Strict):
    form: Literal["8-K", "8-K/A", "6-K", "10-Q", "10-K"]
    filing_date: dt.date
    accession: str
    items: list[str] = []
    url: str = Field(description="URL of the exhibit the numbers come from")
    exhibit: str = Field(description="exhibit type, e.g. 'EX-99.1'")
    local_path: str = Field(description="cached copy under data/raw/")


class Locator(Strict):
    table_title: str
    row_label: str = Field(description="row label exactly as printed")
    section: str | None = Field(default=None, description="label of the heading row above, as printed")
    column_current: str
    column_prior_year: str


class Line(Strict):
    id: str
    label_as_printed: str
    value: float
    prior_year_value: float | None
    unit: Unit = "USD"
    scale: Scale = "millions"
    basis: Basis = "GAAP"
    locator: Locator
    printed_negative: bool = Field(default=False, description="printed in parentheses or with a minus")


class Segment(Strict):
    group: str = Field(description="which breakdown: 'segment', 'category', 'geography', ...")
    name: str = Field(description="display name")
    label_as_printed: str
    value: float
    prior_year_value: float | None
    unit: Unit = "USD"
    scale: Scale = "millions"
    basis: Basis = "GAAP"
    locator: Locator


class Ratio(Strict):
    current: float | None
    prior_year: float | None


class ComputedLine(Strict):
    """A subtotal the company doesn't print. Shown on screen only as 'our calculation'."""

    id: str
    label: str
    formula: str
    value: float
    prior_year_value: float | None
    scale: Scale = "millions"
    our_calculation: Literal[True] = True


class Derived(Strict):
    revenue_yoy: float | None
    gross_margin: Ratio | None
    operating_margin: Ratio | None
    net_margin: Ratio | None
    computed_lines: list[ComputedLine] = []


class Guidance(Strict):
    paraphrase: str = Field(description="our own words; never a copied sentence")
    locator: str


class ValidationException(Strict):
    check: str
    reason: str
    locator: str


class Earnings(Strict):
    schema_version: Literal[1] = 1
    company: Company
    period: Period
    currency: Literal["USD"] = "USD"
    scale: Scale = Field(description="default scale of money lines, from the table header")
    release: Release
    lines: list[Line]
    segments_status: Literal["in_release", "not_in_release", "single_segment"]
    segments: list[Segment] = []
    derived: Derived
    guidance: Guidance | None = None
    validation_exceptions: list[ValidationException] = []
    notes: list[str] = []
    approval: None = Field(default=None, description="always null here; the Gate A record is the sidecar <ID>.approval.json")

    def line(self, id_: str) -> Line | None:
        return next((l for l in self.lines if l.id == id_), None)
