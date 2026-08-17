from analyzer import analyze_log_lines


def test_no_alerts_for_clean_log():
    lines = [
        "Aug 16 02:14:01 web01 sshd[1190]: Accepted password for gabriel from 198.51.100.20 port 51322 ssh2",
    ]
    alerts = analyze_log_lines(lines, year=2026)
    assert alerts == []


def test_failed_login_generates_low_severity_alert():
    lines = [
        "Aug 16 02:14:01 web01 sshd[1190]: Failed password for gabriel from 198.51.100.20 port 51322 ssh2",
    ]
    alerts = analyze_log_lines(lines, year=2026)
    assert len(alerts) == 1
    assert alerts[0]["alert_type"] == "failed_login"
    assert alerts[0]["severity"] == "low"
    assert alerts[0]["source_ip"] == "198.51.100.20"


def test_invalid_user_generates_medium_severity_alert():
    lines = [
        "Aug 16 02:14:01 web01 sshd[1190]: Failed password for invalid user admin from 45.33.12.9 port 40011 ssh2",
    ]
    alerts = analyze_log_lines(lines, year=2026)
    assert len(alerts) == 1
    assert alerts[0]["alert_type"] == "invalid_user"
    assert alerts[0]["severity"] == "medium"
    assert alerts[0]["username"] == "admin"


def test_brute_force_detected_after_threshold_failures():
    ip = "203.0.113.7"
    lines = [
        f"Aug 16 03:12:{10 + i:02d} web01 sshd[220{i}]: Failed password for invalid user admin from {ip} port 5432{i} ssh2"
        for i in range(5)
    ]
    alerts = analyze_log_lines(lines, year=2026)

    brute_force_alerts = [a for a in alerts if a["alert_type"] == "brute_force"]
    assert len(brute_force_alerts) == 1
    assert brute_force_alerts[0]["severity"] == "high"
    assert brute_force_alerts[0]["source_ip"] == ip


def test_brute_force_not_triggered_below_threshold():
    ip = "203.0.113.7"
    lines = [
        f"Aug 16 03:12:{10 + i:02d} web01 sshd[220{i}]: Failed password for invalid user admin from {ip} port 5432{i} ssh2"
        for i in range(4)
    ]
    alerts = analyze_log_lines(lines, year=2026)
    assert all(a["alert_type"] != "brute_force" for a in alerts)


def test_success_after_multiple_failures_flags_possible_compromise():
    ip = "203.0.113.7"
    lines = [
        f"Aug 16 03:12:{10 + i:02d} web01 sshd[220{i}]: Failed password for root from {ip} port 5432{i} ssh2"
        for i in range(3)
    ]
    lines.append(f"Aug 16 03:13:00 web01 sshd[2210]: Accepted password for root from {ip} port 54330 ssh2")

    alerts = analyze_log_lines(lines, year=2026)
    compromise_alerts = [a for a in alerts if a["alert_type"] == "possible_compromise"]
    assert len(compromise_alerts) == 1
    assert compromise_alerts[0]["severity"] == "high"


def test_success_without_prior_failures_is_not_flagged():
    lines = [
        "Aug 16 02:14:01 web01 sshd[1190]: Accepted password for gabriel from 198.51.100.20 port 51322 ssh2",
    ]
    alerts = analyze_log_lines(lines, year=2026)
    assert alerts == []


def test_failures_outside_window_do_not_count_towards_brute_force():
    ip = "203.0.113.7"
    lines = [
        f"Aug 16 03:{10 + i:02d}:00 web01 sshd[220{i}]: Failed password for invalid user admin from {ip} port 5432{i} ssh2"
        for i in range(5)
    ]
    alerts = analyze_log_lines(lines, year=2026)
    assert all(a["alert_type"] != "brute_force" for a in alerts)


def test_alerts_sorted_by_time():
    lines = [
        "Aug 16 10:00:00 web01 sshd[1]: Failed password for root from 1.2.3.4 port 1 ssh2",
        "Aug 16 02:00:00 web01 sshd[2]: Failed password for root from 1.2.3.5 port 2 ssh2",
    ]
    alerts = analyze_log_lines(lines, year=2026)
    assert [a["source_ip"] for a in alerts] == ["1.2.3.5", "1.2.3.4"]
