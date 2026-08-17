from pathlib import Path

from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

from analyzer import analyze_log_lines

db = SQLAlchemy()

SEVERITIES = ["low", "medium", "high"]
DEFAULT_LOG_PATH = Path(__file__).parent / "sample_logs" / "auth.log"


class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    alert_type = db.Column(db.String(40), nullable=False)
    severity = db.Column(db.String(10), nullable=False)
    source_ip = db.Column(db.String(45), nullable=False)
    username = db.Column(db.String(80), nullable=True)
    message = db.Column(db.String(255), nullable=False)
    occurred_at = db.Column(db.DateTime, nullable=False)
    raw_line = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "alert_type": self.alert_type,
            "severity": self.severity,
            "source_ip": self.source_ip,
            "username": self.username,
            "message": self.message,
            "occurred_at": self.occurred_at.isoformat(),
            "raw_line": self.raw_line,
        }


def create_app(db_uri="sqlite:///security_monitor.db", log_path=None):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["LOG_PATH"] = log_path or DEFAULT_LOG_PATH

    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.post("/api/analyze")
    def analyze():
        log_path = Path(app.config["LOG_PATH"])
        if not log_path.exists():
            return jsonify({"error": "Arquivo de log não encontrado"}), 404

        lines = log_path.read_text(encoding="utf-8").splitlines()
        alerts = analyze_log_lines(lines)

        Alert.query.delete()
        for alert in alerts:
            db.session.add(Alert(**alert))
        db.session.commit()

        return jsonify({"lines_processed": len(lines), "alerts_found": len(alerts)}), 201

    @app.get("/api/alerts")
    def list_alerts():
        query = Alert.query

        severity = request.args.get("severity")
        if severity:
            query = query.filter_by(severity=severity)

        alert_type = request.args.get("type")
        if alert_type:
            query = query.filter_by(alert_type=alert_type)

        alerts = query.order_by(Alert.occurred_at.desc()).all()
        return jsonify([a.to_dict() for a in alerts])

    @app.get("/api/summary")
    def summary():
        alerts = Alert.query.all()

        by_severity = {s: 0 for s in SEVERITIES}
        by_ip = {}
        for alert in alerts:
            by_severity[alert.severity] = by_severity.get(alert.severity, 0) + 1
            by_ip[alert.source_ip] = by_ip.get(alert.source_ip, 0) + 1

        top_ips = sorted(by_ip.items(), key=lambda kv: kv[1], reverse=True)[:5]

        return jsonify({
            "total": len(alerts),
            "by_severity": by_severity,
            "top_ips": [{"ip": ip, "count": count} for ip, count in top_ips],
        })

    @app.delete("/api/alerts")
    def clear_alerts():
        Alert.query.delete()
        db.session.commit()
        return "", 204

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5001)
