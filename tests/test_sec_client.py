"""SEC fair-access behavior, tested offline with a mock transport."""

import httpx
import pytest

from sec_client import SecClient, SecError, cik10, submissions_url


class FakeClock:
    def __init__(self):
        self.t = 0.0
        self.sleeps = []

    def now(self):
        return self.t

    def sleep(self, s):
        self.sleeps.append(s)
        self.t += s


def make(handler, tmp_path, clock=None, **kw):
    clock = clock or FakeClock()
    client = SecClient(
        user_agent="Test Person test@example.org",
        cache_dir=tmp_path,
        transport=httpx.MockTransport(handler),
        sleep=clock.sleep,
        clock=clock.now,
        **kw,
    )
    return client, clock


def test_sends_user_agent_and_caches(tmp_path):
    seen = []

    def handler(request):
        seen.append(request.headers["User-Agent"])
        return httpx.Response(200, json={"ok": True})

    client, _ = make(handler, tmp_path)
    url = submissions_url(320193)
    assert client.get_json(url) == {"ok": True}
    assert client.get_json(url) == {"ok": True}  # second call from disk
    assert seen == ["Test Person test@example.org"]
    assert (tmp_path / "data.sec.gov" / "submissions" / "CIK0000320193.json").exists()


def test_rate_limit_spaces_requests(tmp_path):
    client, clock = make(lambda r: httpx.Response(200, content=b"x"), tmp_path, max_rps=5)
    for i in range(4):
        client.get(f"https://www.sec.gov/Archives/f{i}.htm")
    # 4 requests at 5/s => at least 3 waits of 0.2 s
    assert sum(clock.sleeps) >= 0.6 - 1e-9


@pytest.mark.parametrize("status", [403, 429, 500, 503])
def test_backs_off_and_retries(tmp_path, status):
    calls = {"n": 0}

    def handler(request):
        calls["n"] += 1
        return httpx.Response(status if calls["n"] < 3 else 200, content=b"ok")

    client, clock = make(handler, tmp_path)
    assert client.get("https://www.sec.gov/Archives/x.htm") == b"ok"
    assert calls["n"] == 3
    assert any(s >= 2 for s in clock.sleeps)  # exponential backoff, not just throttling


def test_honors_retry_after(tmp_path):
    calls = {"n": 0}

    def handler(request):
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(429, headers={"Retry-After": "7"})
        return httpx.Response(200, content=b"ok")

    client, clock = make(handler, tmp_path)
    client.get("https://www.sec.gov/Archives/y.htm")
    assert 7 in clock.sleeps


def test_gives_up_on_404(tmp_path):
    client, _ = make(lambda r: httpx.Response(404), tmp_path)
    with pytest.raises(SecError):
        client.get("https://www.sec.gov/Archives/missing.htm")


def test_refuses_placeholder_user_agent(monkeypatch, tmp_path):
    monkeypatch.setenv("SEC_USER_AGENT", "Firstname Lastname you@example.com")
    with pytest.raises(SecError):
        SecClient(cache_dir=tmp_path)


def test_refuses_rate_at_or_above_sec_limit(tmp_path):
    with pytest.raises(ValueError):
        SecClient(user_agent="a b@c.d", cache_dir=tmp_path, max_rps=10)


def test_cik_padding():
    assert cik10(320193) == "0000320193"
