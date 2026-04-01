import os
import re
import time
from collections import Counter, defaultdict
from .config import settings
from .cm_client import cm_client
from .policy import approval_status, can_execute, policy_decision, zero_touch_decision
from .memory_store import write_incident, list_incidents
from .cluster_router import get_cluster_config, federated_inventory
from .alerts import alert_payload, send_slack, send_teams, chatops_message, flush_alert_only
from .planner import autonomous_plan_from_rca, execution_plan, approval_package, select_zero_touch_action
from .prometheus_scaffold import prometheus_alert_context
from .watchdog import runtime

def cluster_discovery_tool(cluster_key: str = ""):
    key, cfg = get_cluster_config(cluster_key)
    if not cm_client.configured(key):
        return {"status": "not_configured", "message": f"Missing CM details for cluster key: {key}"}
    data = cm_client.request("GET", "clusters", cluster_key=key)
    items = data.get("items", []) if isinstance(data, dict) else []
    return {"status": "ok", "cluster_key": key, "clusters": [item.get("name") for item in items if isinstance(item, dict)], "raw": data}

def federated_cluster_inventory_tool():
    return federated_inventory()

def cluster_health_tool(cluster_key: str = ""):
    key, cfg = get_cluster_config(cluster_key)
    if not cm_client.configured(key):
        return {"status": "not_configured", "message": f"Missing CM details for cluster key: {key}"}
    cluster_name = cfg.get("cluster_name", "")
    services = cm_client.request("GET", f"clusters/{cluster_name}/services", cluster_key=key)
    hosts = cm_client.request("GET", "hosts", cluster_key=key)
    return {"status": "ok", "cluster_key": key, "cluster_name": cluster_name, "services": services, "hosts": hosts}

def service_health_tool(service_name: str, cluster_key: str = ""):
    key, cfg = get_cluster_config(cluster_key)
    if not cm_client.configured(key):
        return {"status": "not_configured", "message": f"Missing CM details for cluster key: {key}"}
    cluster_name = cfg.get("cluster_name", "")
    service = cm_client.request("GET", f"clusters/{cluster_name}/services/{service_name}", cluster_key=key)
    roles = cm_client.request("GET", f"clusters/{cluster_name}/services/{service_name}/roles", cluster_key=key)
    return {"status": "ok", "cluster_key": key, "service_name": service_name, "service": service, "roles": roles}

def impala_spike_analysis_tool(cluster_key: str = ""):
    pattern = re.compile(r"Query submitted", re.IGNORECASE)
    table_pattern = re.compile(r"from\s+([a-zA-Z0-9_\.]+)", re.IGNORECASE)
    counts = defaultdict(int)
    tables = Counter()
    if os.path.exists(settings.impala_log_path):
        with open(settings.impala_log_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if pattern.search(line):
                    counts[line[:16].strip() if len(line) >= 16 else "unknown"] += 1
                m = table_pattern.search(line)
                if m:
                    tables[m.group(1)] += 1
    top_windows = dict(sorted(counts.items(), key=lambda x: x[1], reverse=True)[:20])
    top_tables = dict(tables.most_common(20))
    max_qpm = max(top_windows.values()) if top_windows else 0
    severity = "high" if max_qpm > 100 else "medium" if max_qpm > 20 else "low"
    return {"status": "ok", "cluster_key": cluster_key or settings.default_cluster_key, "severity": severity, "max_query_window_count": max_qpm, "top_windows": top_windows, "top_tables": top_tables, "log_path": settings.impala_log_path}

def impala_rca_tool(cluster_key: str = ""):
    spike = impala_spike_analysis_tool(cluster_key=cluster_key)
    severity = spike.get("severity", "low")
    probable_cause = "burst query workload" if severity in {"high", "medium"} else "no significant spike detected"
    recommendations = ["review coordinator admission control", "review top scanned tables", "review upstream BI or API burst sources"] if severity in {"high", "medium"} else []
    return {"status": "ok", "cluster_key": cluster_key or settings.default_cluster_key, "issue_type": "impala_pressure", "severity": severity, "probable_cause": probable_cause, "recommendations": recommendations, "evidence": spike}

def storage_rca_tool(cluster_key: str = ""):
    evidence = {"note": "storage RCA placeholder; extend with HDFS and YARN collectors in your environment"}
    return {"status": "ok", "cluster_key": cluster_key or settings.default_cluster_key, "issue_type": "storage_pressure", "severity": "unknown", "probable_cause": "requires HDFS and YARN collectors", "recommendations": ["check HDFS free space", "check small files", "check YARN queue pressure"], "evidence": evidence}

def cluster_rca_summary_tool(cluster_key: str = ""):
    impala = impala_rca_tool(cluster_key=cluster_key)
    storage = storage_rca_tool(cluster_key=cluster_key)
    overall_issue = "impala_pressure" if impala.get("severity") in {"high", "medium"} else "storage_or_general"
    return {"status": "ok", "cluster_key": cluster_key or settings.default_cluster_key, "overall_issue": overall_issue, "impala_rca": impala, "storage_rca": storage}

def autonomous_remediation_plan_tool(cluster_key: str = ""):
    rca = cluster_rca_summary_tool(cluster_key=cluster_key)
    return autonomous_plan_from_rca(rca, cluster_key=cluster_key or settings.default_cluster_key)

def execution_plan_tool(cluster_key: str = ""):
    plan = autonomous_remediation_plan_tool(cluster_key=cluster_key)
    return execution_plan(plan)

def approval_package_tool(cluster_key: str = ""):
    plan = autonomous_remediation_plan_tool(cluster_key=cluster_key)
    return approval_package(cluster_key=cluster_key or settings.default_cluster_key, remediation_plan=plan)

def policy_decision_tool(action_type: str, risk: str = "medium", approved: bool = False):
    return policy_decision(action_type=action_type, risk=risk, approved=approved)

def zero_touch_decision_tool(cluster_key: str = ""):
    plan = autonomous_remediation_plan_tool(cluster_key=cluster_key)
    selected = select_zero_touch_action(plan)
    action = selected.get("action", "none")
    risk = selected.get("risk", "unknown")
    decision = zero_touch_decision(action, risk=risk) if action != "none" else {"status": "ok", "action_type": "none", "zero_touch_allowed": False, "decision_reason": "no eligible low-risk action"}
    return {"status": "ok", "cluster_key": cluster_key or settings.default_cluster_key, "selected_action": selected, "decision": decision}

def approval_status_tool():
    return approval_status()

def prepare_restart_service_tool(service_name: str, cluster_key: str = ""):
    key, cfg = get_cluster_config(cluster_key)
    return {"status": "prepared", "action_type": "restart_service_guarded", "cluster_key": key, "cluster_name": cfg.get("cluster_name",""), "service_name": service_name, "approval_required": settings.require_human_approval}

def execute_restart_service_tool(service_name: str, approved: bool = False, cluster_key: str = ""):
    key, cfg = get_cluster_config(cluster_key)
    allowed, reason = can_execute("restart_service_guarded", approved)
    if not allowed:
        return {"status": "blocked", "reason": reason, "service_name": service_name, "cluster_key": key}
    if not cm_client.configured(key):
        return {"status": "not_configured", "message": f"Missing CM details for cluster key: {key}"}
    cluster_name = cfg.get("cluster_name", "")
    result = cm_client.request("POST", f"clusters/{cluster_name}/services/{service_name}/commands/restart", cluster_key=key)
    return {"status": "ok", "cluster_key": key, "service_name": service_name, "result": result}

def write_incident_memory_tool(incident_id: str = "", summary: str = "", details=None, cluster_key: str = ""):
    payload = {"incident_id": incident_id, "summary": summary, "details": details or {}, "cluster_key": cluster_key or settings.default_cluster_key}
    return write_incident(payload)

def incident_memory_list_tool():
    return list_incidents()

def alert_payload_tool(title: str, summary: str, severity: str = "info", channel: str = "generic", cluster_key: str = ""):
    return alert_payload(channel=channel, title=title, summary=summary, severity=severity, cluster_key=cluster_key or settings.default_cluster_key)

def slack_alert_tool(title: str, summary: str, severity: str = "info", cluster_key: str = ""):
    return send_slack(title=title, summary=summary, severity=severity, cluster_key=cluster_key or settings.default_cluster_key)

def teams_alert_tool(title: str, summary: str, severity: str = "info", cluster_key: str = ""):
    return send_teams(title=title, summary=summary, severity=severity, cluster_key=cluster_key or settings.default_cluster_key)

def chatops_message_tool(channel: str, title: str, summary: str, next_steps=None, cluster_key: str = ""):
    return chatops_message(channel=channel, title=title, summary=summary, next_steps=next_steps or [], cluster_key=cluster_key or settings.default_cluster_key)

def prometheus_alert_context_tool(cluster_key: str = "", query: str = ""):
    return prometheus_alert_context(cluster_key=cluster_key or settings.default_cluster_key, query=query)

def autopilot_summary_tool(cluster_key: str = ""):
    return {
        "status": "ok",
        "cluster_key": cluster_key or settings.default_cluster_key,
        "rca": cluster_rca_summary_tool(cluster_key=cluster_key),
        "remediation_plan": autonomous_remediation_plan_tool(cluster_key=cluster_key),
        "execution_plan": execution_plan_tool(cluster_key=cluster_key),
        "approval_package": approval_package_tool(cluster_key=cluster_key),
        "zero_touch": zero_touch_decision_tool(cluster_key=cluster_key),
    }

def zero_touch_execute_tool(cluster_key: str = ""):
    decision_bundle = zero_touch_decision_tool(cluster_key=cluster_key)
    selected = decision_bundle.get("selected_action", {})
    decision = decision_bundle.get("decision", {})
    action = selected.get("action", "none")
    if not decision.get("zero_touch_allowed", False):
        return {"status": "blocked", "cluster_key": cluster_key or settings.default_cluster_key, "reason": decision.get("decision_reason", "not allowed"), "selected_action": selected}
    if action == "flush_alert_only":
        result = flush_alert_only(title="CDP Autopilot Alert", summary="Zero-touch low-risk action selected", severity="info", cluster_key=cluster_key or settings.default_cluster_key)
        memory = write_incident({"summary": "Zero-touch action executed", "details": {"action": action, "result": result}, "cluster_key": cluster_key or settings.default_cluster_key})
        return {"status": "ok", "cluster_key": cluster_key or settings.default_cluster_key, "executed_action": action, "result": result, "memory": memory}
    if action == "write_incident_memory":
        memory = write_incident({"summary": "Zero-touch memory write action", "details": {"action": action}, "cluster_key": cluster_key or settings.default_cluster_key})
        return {"status": "ok", "cluster_key": cluster_key or settings.default_cluster_key, "executed_action": action, "memory": memory}
    return {"status": "blocked", "cluster_key": cluster_key or settings.default_cluster_key, "reason": f"no executor implemented for action: {action}", "selected_action": selected}

def watchdog_tick_tool(cluster_key: str = ""):
    result = zero_touch_execute_tool(cluster_key=cluster_key)
    runtime.last_result = result
    runtime.last_tick = time.time()
    return {"status": "ok", "cluster_key": cluster_key or settings.default_cluster_key, "watchdog_result": result}

def watchdog_status_tool():
    return {"status": "ok", "last_tick": runtime.last_tick, "last_result": runtime.last_result}
