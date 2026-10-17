"""Structural checks on project memory, skills, agents and config (brief §5)."""

import json
import pathlib

import pytest
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROJECT_SKILLS = ["earnings-ingest", "money-map", "post-pack", "newsletter-issue", "earnings-calendar"]
SIDE_EFFECT_SKILLS = {"earnings-ingest", "money-map", "earnings-calendar"}
AGENTS = ["numbers-auditor", "compliance-reviewer"]


def frontmatter(path: pathlib.Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{path} has no frontmatter"
    _, fm, body = text.split("---\n", 2)
    return yaml.safe_load(fm), body


def test_claude_md_is_short():
    lines = (ROOT / "CLAUDE.md").read_text(encoding="utf-8").splitlines()
    assert len(lines) < 150


@pytest.mark.parametrize("name", PROJECT_SKILLS)
def test_project_skill(name):
    path = ROOT / ".claude" / "skills" / name / "SKILL.md"
    meta, body = frontmatter(path)
    assert meta["name"] == name
    assert meta["description"]
    assert meta.get("argument-hint")
    assert len(path.read_text(encoding="utf-8").splitlines()) < 500
    assert bool(meta.get("disable-model-invocation")) == (name in SIDE_EFFECT_SKILLS)
    assert "allowed-tools" not in meta  # no broad pre-approvals
    json.loads((path.parent / "evals" / "evals.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("name", AGENTS)
def test_agents_are_read_only(name):
    meta, body = frontmatter(ROOT / ".claude" / "agents" / f"{name}.md")
    assert meta["name"] == name
    tools = {t.strip() for t in meta["tools"].split(",")}
    assert tools == {"Read", "Grep", "Glob"}
    assert body.strip()


def test_auditor_is_guarded_and_blind():
    meta, _ = frontmatter(ROOT / ".claude" / "agents" / "numbers-auditor.md")
    assert meta.get("omitClaudeMd") is True
    hook = meta["hooks"]["PreToolUse"][0]
    assert "Read" in hook["matcher"] and "Grep" in hook["matcher"] and "Glob" in hook["matcher"]
    assert "auditor_guard.py" in hook["hooks"][0]["command"]


def test_settings_deny_risky_hyperframes_commands():
    settings = json.loads((ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
    deny = settings["permissions"]["deny"]
    for cmd in ["usage", "publish", "cloud", "lambda", "auth", "skills", "init"]:
        assert f"Bash(npx hyperframes {cmd} *)" in deny
    assert settings["env"]["HYPERFRAMES_NO_TELEMETRY"] == "1"


def test_watchlist_has_the_20_companies():
    data = yaml.safe_load((ROOT / "config" / "watchlist.yaml").read_text(encoding="utf-8"))
    tickers = [c["ticker"] for c in data["companies"]]
    assert len(tickers) == 20 and len(set(tickers)) == 20
    for c in data["companies"]:
        assert {"ticker", "name", "cik", "fye", "ir_url", "lines", "segments", "verified"} <= set(c)


def test_tokens_parse_and_meet_readability_floor():
    tokens = json.loads((ROOT / "brand" / "tokens.json").read_text(encoding="utf-8"))
    assert tokens["type_scale_px"]["label_min"] >= 44
    assert tokens["type_scale_px"]["number_min"] >= 72
    for theme in tokens["themes"].values():
        assert {"background", "revenue", "cost", "profit", "loss", "accent"} <= set(theme)


def test_scaffold_exists():
    for rel in [
        "STATUS.md", "DECISIONS.md", "SKILLS.md", "CORRECTIONS.md", "NEXT.md", "INBOX.md", "README.md",
        ".env.example", ".gitignore", "docs/KICKOFF.md", "docs/platform-specs.md", "docs/posting-checklist.md",
        "docs/sponsor-kit.md", "docs/plan-30-days.md", "brand/tokens.json", "brand/fonts/OFL.txt",
        "config/watchlist.yaml", "analytics/posts.csv", "schemas", "data/normalized", "scripts", "templates/money-map",
        "templates/dollar-split", "templates/kpi-cards", "templates/carousel", "newsletter/issues", "tests/fixtures",
    ]:
        assert (ROOT / rel).exists(), rel
