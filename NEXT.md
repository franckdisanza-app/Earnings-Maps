# Next

**Resume at Phase 3: data pipeline** (docs/KICKOFF.md §6).

1. Ask the owner for their name and email for `SEC_USER_AGENT` and write it to `.env` (never echo it).
2. Check the SEC endpoints and field names against https://www.sec.gov/edgar/sec-api-documentation before coding.
3. Build `scripts/sec_client.py` (User-Agent, <10 req/s, disk cache in `data/raw/`, backoff on 403/429/5xx), `find_releases.py`, `parse_release.py`, `validate.py`, `audit_diff.py`, and `approve.py` (writes and `--verify`s `data/normalized/<ID>.approval.json`).
4. Write `schemas/earnings.schema.json` plus the pydantic mirror. The `approval` record lives in the sidecar `<ID>.approval.json`, not inside the hashed file (see DECISIONS.md).
5. Fill and verify `config/watchlist.yaml`: CIKs, FYE, IR URLs, line mappings, segments.
6. Fixtures from four past releases with different shapes (clean segments; products/services cost split; no cost-of-revenue line; a net loss), plus tests for parsing and every validation identity.
7. First real runs: `/earnings-ingest` on three companies' past releases, including the `numbers-auditor` subagent (its guard is tested in `tests/test_auditor_guard.py`), and run the skill's `evals/evals.json` prompts.

Open items for the owner: authenticate beehiiv (`/mcp`) before Phase 6. Gate 2 will ask for a style frame and one of the three voices in `brand/voice-samples/`.
