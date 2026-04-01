import requests
from .config import settings

def alert_payload(channel: str, title: str, summary: str, severity: str = "info", cluster_key: str = ""):
    return {"status": "ok", "channel": channel, "payload": {"title": title, "summary": summary, "severity": severity, "cluster_key": cluster_key}}

def send_slack(title: str, summary: str, severity: str = "info", cluster_key: str = ""):
    payload = {"text": f"[{severity.upper()}] {title} | cluster={cluster_key or 'default'} | {summary}"}
    if not settings.slack_webhook_url:
        return {"status": "not_configured", "payload": payload}
    r = requests.post(settings.slack_webhook_url, json=payload, timeout=20)
    return {"status": "ok", "status_code": r.status_code, "payload": payload}

def send_teams(title: str, summary: str, severity: str = "info", cluster_key: str = ""):
    payload = {"text": f"[{severity.upper()}] {title} | cluster={cluster_key or 'default'} | {summary}"}
    if not settings.teams_webhook_url:
        return {"status": "not_configured", "payload": payload}
    r = requests.post(settings.teams_webhook_url, json=payload, timeout=20)
    return {"status": "ok", "status_code": r.status_code, "payload": payload}

def chatops_message(channel: str, title: str, summary: str, next_steps=None, cluster_key: str = ""):
    return {"status": "ok", "channel": channel, "message": {"title": title, "summary": summary, "cluster_key": cluster_key, "next_steps": next_steps or []}}

def flush_alert_only(title: str, summary: str, severity: str = "info", cluster_key: str = ""):
    return {"status": "ok", "action": "flush_alert_only", "title": title, "summary": summary, "severity": severity, "cluster_key": cluster_key}
