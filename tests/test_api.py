from fastapi.testclient import TestClient
from app.main import app
c=TestClient(app)
def test_health():assert c.get("/api/health").status_code==200
def test_dashboard():assert c.get("/api/dashboard").json()["metrics"]["assets"]>=8
def test_model():assert "version" in c.get("/api/model/status").json()
def test_scenario():assert c.post("/api/scenarios/bearing_degradation").status_code==200
