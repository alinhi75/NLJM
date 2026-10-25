from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health(db_session):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_stats_counts_jobs(db_session):
    assert client.get("/stats").json() == {"jobs": 0}
