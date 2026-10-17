"""SEC EDGAR client that follows the fair-access rules (KICKOFF §2.3).

- Every request sends the User-Agent from SEC_USER_AGENT (.env or environment).
- Requests are spaced to stay well under SEC's 10 requests/second (default 5/s).
- Responses are cached on disk; immutable Archives files are never re-downloaded.
- 403, 429 and 5xx responses back off exponentially (honoring Retry-After) and retry.
"""

from __future__ import annotations

import hashlib
import pathlib
import threading
import time
from typing import Callable
from urllib.parse import urlparse

import httpx

from common import RAW, load_env

PLACEHOLDER = "you@example.com"
RETRY_STATUSES = {403, 429, 500, 502, 503, 504}


class SecError(RuntimeError):
    pass


def user_agent_from_env() -> str:
    ua = load_env().get("SEC_USER_AGENT", "").strip()
    if not ua or PLACEHOLDER in ua or "@" not in ua:
        raise SecError("SEC_USER_AGENT is missing or still the placeholder; set 'Name email' in .env")
    return ua


def cik10(cik: int | str) -> str:
    return f"{int(cik):010d}"


def submissions_url(cik: int | str) -> str:
    return f"https://data.sec.gov/submissions/CIK{cik10(cik)}.json"


def companyfacts_url(cik: int | str) -> str:
    return f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik10(cik)}.json"


def filing_folder_url(cik: int | str, accession: str) -> str:
    return f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession.replace('-', '')}/"


TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"


class SecClient:
    def __init__(
        self,
        user_agent: str | None = None,
        cache_dir: pathlib.Path = RAW / "_sec",
        max_rps: float = 5.0,
        max_retries: int = 5,
        transport: httpx.BaseTransport | None = None,
        sleep: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if max_rps <= 0 or max_rps >= 10:
            raise ValueError("max_rps must be between 0 and 10 (SEC limit)")
        self.user_agent = user_agent or user_agent_from_env()
        self.cache_dir = cache_dir
        self.min_interval = 1.0 / max_rps
        self.max_retries = max_retries
        self.sleep = sleep
        self.clock = clock
        self._last = -1e9
        self._lock = threading.Lock()
        self.requests_made = 0
        self.http = httpx.Client(
            headers={"User-Agent": self.user_agent, "Accept-Encoding": "gzip, deflate"},
            timeout=30.0,
            follow_redirects=True,
            transport=transport,
        )

    # -- cache -------------------------------------------------------------
    def cache_path(self, url: str) -> pathlib.Path:
        parsed = urlparse(url)
        rel = parsed.path.lstrip("/") or "index"
        if parsed.query:
            rel += "_" + hashlib.sha256(parsed.query.encode()).hexdigest()[:12]
        return self.cache_dir / parsed.netloc / rel

    @staticmethod
    def _fresh(path: pathlib.Path, max_age: float | None) -> bool:
        if not path.exists():
            return False
        if max_age is None:
            return True
        return (time.time() - path.stat().st_mtime) < max_age

    # -- requests ----------------------------------------------------------
    def _throttle(self) -> None:
        with self._lock:
            wait = self._last + self.min_interval - self.clock()
            if wait > 0:
                self.sleep(wait)
            self._last = self.clock()

    def _fetch(self, url: str) -> bytes:
        delay = 2.0
        for attempt in range(self.max_retries + 1):
            self._throttle()
            self.requests_made += 1
            try:
                resp = self.http.get(url)
            except httpx.TransportError as exc:
                if attempt == self.max_retries:
                    raise SecError(f"network error for {url}: {exc}") from exc
                self.sleep(delay)
                delay = min(delay * 2, 60)
                continue
            if resp.status_code == 200:
                return resp.content
            if resp.status_code in RETRY_STATUSES and attempt < self.max_retries:
                retry_after = resp.headers.get("Retry-After", "")
                wait = float(retry_after) if retry_after.isdigit() else delay
                self.sleep(min(wait, 120))
                delay = min(delay * 2, 60)
                continue
            raise SecError(f"HTTP {resp.status_code} for {url}")
        raise SecError(f"gave up on {url}")

    def get(self, url: str, dest: pathlib.Path | None = None, max_age: float | None = None) -> bytes:
        """Return the body of `url`, from cache when fresh.

        dest: where to keep the file (defaults to the URL-shaped cache path).
        max_age: seconds before a cached copy is stale; None = never stale (Archives files).
        """
        path = dest or self.cache_path(url)
        if self._fresh(path, max_age):
            return path.read_bytes()
        body = self._fetch(url)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".part")
        tmp.write_bytes(body)
        tmp.replace(path)
        return body

    def get_json(self, url: str, dest: pathlib.Path | None = None, max_age: float | None = None):
        import json

        return json.loads(self.get(url, dest=dest, max_age=max_age))

    def close(self) -> None:
        self.http.close()

    def __enter__(self) -> "SecClient":
        return self

    def __exit__(self, *exc) -> None:
        self.close()
