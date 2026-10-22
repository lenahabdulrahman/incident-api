from fastapi.testclient import TestClient
from api.index import app

client = TestClient(app)

SAMPLE = """2026-10-20 10:01:02 INFO Service started
2026-10-20 10:05:11 ERROR Database connection timeout
2026-10-20 10:07:45 ERROR Database connection timeout
2026-10-20 11:02:10 WARN High memory usage
2026-10-20 11:03:00 CRITICAL Disk full"""


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_analyze():
    r = client.post("/analyze", json={"logs": SAMPLE}).json()
    assert r["by_level"]["ERROR"] == 2
    assert r["top_errors"][0]["count"] == 2
    assert r["peak_error_hour"] == "10:00"


def test_sla_breached():
    r = client.post("/sla", json={
        "priority": "P1",
        "opened_at": "2026-10-20T08:00:00",
        "resolved_at": "2026-10-20T14:00:00",
    }).json()
    assert r["status"] == "breached"