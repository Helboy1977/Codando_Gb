"""Analisa logs de autenticação estilo SSH (auth.log) e gera alertas de segurança."""

import re
from collections import defaultdict
from datetime import datetime, timedelta

MONTHS = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
}

LINE_RE = re.compile(
    r"^(?P<mon>\w{3})\s+(?P<day>\d{1,2})\s+(?P<time>\d{2}:\d{2}:\d{2})\s+\S+\s+sshd\[\d+\]:\s+(?P<msg>.*)$"
)
FAILED_RE = re.compile(
    r"Failed password for (?P<invalid>invalid user )?(?P<user>\S+) "
    r"from (?P<ip>\d{1,3}(?:\.\d{1,3}){3}) port \d+"
)
ACCEPTED_RE = re.compile(
    r"Accepted password for (?P<user>\S+) from (?P<ip>\d{1,3}(?:\.\d{1,3}){3}) port \d+"
)

BRUTE_FORCE_THRESHOLD = 5
BRUTE_FORCE_WINDOW_SECONDS = 120
COMPROMISE_THRESHOLD = 3

SEVERITY_ORDER = {"low": 0, "medium": 1, "high": 2}


def _parse_timestamp(mon, day, time_str, year):
    month = MONTHS.get(mon)
    if month is None:
        return None
    hh, mm, ss = (int(p) for p in time_str.split(":"))
    return datetime(year, month, int(day), hh, mm, ss)


def _parse_events(lines, year):
    events = []
    for raw in lines:
        line = raw.strip()
        if not line:
            continue

        line_match = LINE_RE.match(line)
        if not line_match:
            continue

        ts = _parse_timestamp(line_match.group("mon"), line_match.group("day"), line_match.group("time"), year)
        if ts is None:
            continue

        msg = line_match.group("msg")

        failed_match = FAILED_RE.search(msg)
        if failed_match:
            events.append({
                "type": "failed",
                "ts": ts,
                "ip": failed_match.group("ip"),
                "user": failed_match.group("user"),
                "invalid_user": bool(failed_match.group("invalid")),
                "raw": line,
            })
            continue

        accepted_match = ACCEPTED_RE.search(msg)
        if accepted_match:
            events.append({
                "type": "accepted",
                "ts": ts,
                "ip": accepted_match.group("ip"),
                "user": accepted_match.group("user"),
                "raw": line,
            })

    return events


def analyze_log_lines(lines, year=None):
    """Recebe as linhas de um auth.log e retorna uma lista de alertas (dicts)."""
    year = year or datetime.now().year
    events = _parse_events(lines, year)

    alerts = []
    failed_by_ip = defaultdict(list)

    for event in events:
        ip = event["ip"]

        if event["type"] == "failed":
            alerts.append({
                "alert_type": "invalid_user" if event["invalid_user"] else "failed_login",
                "severity": "medium" if event["invalid_user"] else "low",
                "source_ip": ip,
                "username": event["user"],
                "message": (
                    f"Falha de autenticação para usuário inexistente '{event['user']}'"
                    if event["invalid_user"]
                    else f"Falha de autenticação para usuário '{event['user']}'"
                ),
                "occurred_at": event["ts"],
                "raw_line": event["raw"],
            })

            window_start = event["ts"] - timedelta(seconds=BRUTE_FORCE_WINDOW_SECONDS)
            failed_by_ip[ip] = [t for t in failed_by_ip[ip] if t >= window_start] + [event["ts"]]

            if len(failed_by_ip[ip]) == BRUTE_FORCE_THRESHOLD:
                alerts.append({
                    "alert_type": "brute_force",
                    "severity": "high",
                    "source_ip": ip,
                    "username": None,
                    "message": (
                        f"Possível força bruta: {BRUTE_FORCE_THRESHOLD} tentativas falhas de {ip} "
                        f"em menos de {BRUTE_FORCE_WINDOW_SECONDS}s"
                    ),
                    "occurred_at": event["ts"],
                    "raw_line": event["raw"],
                })

        elif event["type"] == "accepted":
            window_start = event["ts"] - timedelta(seconds=BRUTE_FORCE_WINDOW_SECONDS)
            recent_failures = [t for t in failed_by_ip.get(ip, []) if t >= window_start]

            if len(recent_failures) >= COMPROMISE_THRESHOLD:
                alerts.append({
                    "alert_type": "possible_compromise",
                    "severity": "high",
                    "source_ip": ip,
                    "username": event["user"],
                    "message": (
                        f"Login bem-sucedido de {ip} após {len(recent_failures)} falhas recentes "
                        f"— possível comprometimento de conta"
                    ),
                    "occurred_at": event["ts"],
                    "raw_line": event["raw"],
                })

            failed_by_ip[ip] = []

    alerts.sort(key=lambda a: a["occurred_at"])
    return alerts
