import tempfile
from pathlib import Path

import pytest

from app import create_app, db

SAMPLE_LOG = """\
Aug 16 03:12:10 web01 sshd[2201]: Failed password for invalid user admin from 203.0.113.7 port 54321 ssh2
Aug 16 03:12:14 web01 sshd[2202]: Failed password for invalid user admin from 203.0.113.7 port 54322 ssh2
Aug 16 03:12:18 web01 sshd[2203]: Failed password for invalid user admin from 203.0.113.7 port 54323 ssh2
Aug 16 03:12:22 web01 sshd[2204]: Failed password for invalid user admin from 203.0.113.7 port 54324 ssh2
Aug 16 03:12:26 web01 sshd[2205]: Failed password for invalid user admin from 203.0.113.7 port 54325 ssh2
Aug 16 03:12:30 web01 sshd[2206]: Accepted password for admin from 203.0.113.7 port 54326 ssh2
Aug 16 08:22:44 web01 sshd[3310]: Accepted password for gabriel from 198.51.100.20 port 51890 ssh2
"""


@pytest.fixture
def client(tmp_path):
    log_file = tmp_path / "auth.log"
    log_file.write_text(SAMPLE_LOG, encoding="utf-8")

    app = create_app(db_uri="sqlite:///:memory:", log_path=log_file)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client
    with app.app_context():
        db.drop_all()


def test_index_page(client):
    res = client.get("/")
    assert res.status_code == 200


def test_alerts_empty_before_analysis(client):
    res = client.get("/api/alerts")
    assert res.status_code == 200
    assert res.get_json() == []


def test_analyze_populates_alerts(client):
    res = client.post("/api/analyze")
    assert res.status_code == 201
    body = res.get_json()
    assert body["lines_processed"] == 7
    assert body["alerts_found"] > 0

    res = client.get("/api/alerts")
    alerts = res.get_json()
    types = {a["alert_type"] for a in alerts}
    assert "brute_force" in types
    assert "possible_compromise" in types


def test_analyze_missing_log_file_returns_404(tmp_path):
    app = create_app(db_uri="sqlite:///:memory:", log_path=tmp_path / "missing.log")
    app.config["TESTING"] = True
    with app.test_client() as client:
        res = client.post("/api/analyze")
        assert res.status_code == 404
    with app.app_context():
        db.drop_all()


def test_filter_alerts_by_severity(client):
    client.post("/api/analyze")
    res = client.get("/api/alerts?severity=high")
    alerts = res.get_json()
    assert len(alerts) > 0
    assert all(a["severity"] == "high" for a in alerts)


def test_summary_counts(client):
    client.post("/api/analyze")
    res = client.get("/api/summary")
    body = res.get_json()
    assert body["total"] > 0
    assert sum(body["by_severity"].values()) == body["total"]
    assert body["top_ips"][0]["ip"] == "203.0.113.7"


def test_clear_alerts(client):
    client.post("/api/analyze")
    res = client.delete("/api/alerts")
    assert res.status_code == 204

    res = client.get("/api/alerts")
    assert res.get_json() == []
