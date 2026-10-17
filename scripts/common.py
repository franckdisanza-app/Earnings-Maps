"""Shared paths and config loading for the Earnings Maps pipeline."""

from __future__ import annotations

import os
import pathlib
import re

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
NORMALIZED = ROOT / "data" / "normalized"
OUT = ROOT / "out"
WATCHLIST = ROOT / "config" / "watchlist.yaml"

ID_RE = re.compile(r"^(?P<ticker>[A-Z.]{1,6})-(?P<period>FY\d{4}Q[1-4])$")


def load_env(path: pathlib.Path = ROOT / ".env") -> dict[str, str]:
    """Minimal .env reader (KEY=VALUE, optional quotes, # comments). Process env wins."""
    values: dict[str, str] = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            values[key.strip()] = value
    for key in list(values):
        if key in os.environ:
            values[key] = os.environ[key]
    return values


def load_watchlist() -> dict:
    return yaml.safe_load(WATCHLIST.read_text(encoding="utf-8"))


def company(ticker: str) -> dict:
    ticker = ticker.upper()
    for entry in load_watchlist()["companies"]:
        if entry["ticker"] == ticker:
            return entry
    raise SystemExit(f"{ticker} is not in config/watchlist.yaml")


def split_id(id_: str) -> tuple[str, str]:
    m = ID_RE.match(id_)
    if not m:
        raise SystemExit(f"bad ID {id_!r}; expected TICKER-FY2026Q3")
    return m.group("ticker"), m.group("period")


def raw_dir(ticker: str, period: str) -> pathlib.Path:
    return RAW / ticker.upper() / period


def data_path(id_: str) -> pathlib.Path:
    return NORMALIZED / f"{id_}.json"


def approval_path(id_: str) -> pathlib.Path:
    return NORMALIZED / f"{id_}.approval.json"


def out_dir(id_: str) -> pathlib.Path:
    return OUT / id_
