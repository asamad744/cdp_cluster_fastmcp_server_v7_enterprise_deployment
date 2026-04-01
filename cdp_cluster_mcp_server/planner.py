def autonomous_plan_from_rca(rca_summary: dict, cluster_key: str = ""):
    overall_issue = rca_summary.get("overall_issue", "unknown")
    impala_rca = rca_summary.get("impala_rca", {})
    storage_rca = rca_summary.get("storage_rca", {})
    if overall_issue == "impala_pressure":
        plan = {
            "plan_type": "guarded_impala_response",
            "recommended_actions": [
                {"action": "review_admission_control", "risk": "low"},
                {"action": "review_hot_tables", "risk": "low"},
                {"action": "flush_alert_only", "risk": "low", "approval_required": False},
                {"action": "prepare_restart_service", "service_name": "impala", "risk": "medium", "approval_required": True},
            ],
            "probable_cause": impala_rca.get("probable_cause", "unknown"),
        }
    else:
        plan = {
            "plan_type": "storage_or_general_response",
            "recommended_actions": [
                {"action": "check_hdfs_capacity", "risk": "low"},
                {"action": "check_small_files", "risk": "low"},
                {"action": "check_yarn_pressure", "risk": "low"},
                {"action": "flush_alert_only", "risk": "low", "approval_required": False},
            ],
            "probable_cause": storage_rca.get("probable_cause", "unknown"),
        }
    return {"status": "ok", "cluster_key": cluster_key, "plan": plan}

def execution_plan(remediation_plan: dict):
    actions = remediation_plan.get("plan", {}).get("recommended_actions", [])
    steps = []
    for idx, action in enumerate(actions, start=1):
        steps.append({"step": idx, "action": action.get("action"), "risk": action.get("risk", "unknown"), "approval_required": action.get("approval_required", False), "service_name": action.get("service_name", "")})
    return {"status": "ok", "execution_steps": steps}

def approval_package(cluster_key: str, remediation_plan: dict):
    actions = remediation_plan.get("plan", {}).get("recommended_actions", [])
    return {"status": "ok", "cluster_key": cluster_key, "approval_package": {"summary": remediation_plan.get("plan", {}).get("probable_cause", "unknown"), "recommended_actions": actions, "requires_human_review": any(x.get("approval_required", False) for x in actions)}}

def select_zero_touch_action(remediation_plan: dict):
    for action in remediation_plan.get("plan", {}).get("recommended_actions", []):
        if action.get("risk") == "low" and not action.get("approval_required", False):
            return action
    return {}
