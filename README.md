# AI Critical Infrastructure Predictive Maintenance

Independent research laboratory for AI-assisted predictive maintenance of **synthetic critical-energy assets**.

Features:
- synthetic OT telemetry generation
- Isolation Forest anomaly detection
- Random Forest failure-risk prediction
- interpretable RUL estimate
- asset health index
- maintenance priority engine
- data-quality and drift monitoring
- model metrics and feature importance
- human-in-the-loop governance
- scenario simulator
- REST API
- browser dashboard
- SQLite persistence
- Docker
- GitHub Actions
- automated tests

**Safety:** This is a synthetic laboratory. It does not connect to or control real SCADA/ICS equipment and does not use proprietary operational data.

## Run

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q
python run.py
```

Windows PowerShell:
```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pytest -q
python run.py
```

Dashboard: http://127.0.0.1:8003/
API docs: http://127.0.0.1:8002/docs

## Scenarios

- healthy_fleet
- bearing_degradation
- pump_cavitation
- compressor_overheat
- sensor_drift

## Research framing

The project treats AI as decision support. It may identify anomalies, estimate failure probability and RUL, and prioritize maintenance, but it has **no direct equipment-control interface**.

See `docs/references.md` for NIST sources on energy-sector asset management, situational awareness, condition monitoring, and trustworthy AI in critical infrastructure.
