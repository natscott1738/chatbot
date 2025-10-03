from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    r = client.get("/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_metrics():
    r = client.get("/v1/metrics")
    assert r.status_code == 200
    assert "requests" in r.json()
