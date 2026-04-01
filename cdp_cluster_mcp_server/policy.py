from .config import settings

def approval_status():
    return {
        "status": "ok",
        "enable_write_actions": settings.enable_write_actions,
        "require_human_approval": settings.require_human_approval,
        "zero_touch_enabled": settings.zero_touch_enabled,
        "allowed_actions": sorted(settings.allowed_actions),
        "zero_touch_allowed_actions": sorted(settings.zero_touch_allowed_actions),
    }

def can_execute(action_type: str, approved: bool):
    if action_type not in settings.allowed_actions:
        return False, "action not allowlisted"
    if action_type == "write_incident_memory":
        return True, "allowed"
    if not settings.enable_write_actions:
        return False, "write actions disabled"
    if settings.require_human_approval and not approved:
        return False, "approval required"
    return True, "allowed"

def zero_touch_can_execute(action_type: str):
    if not settings.zero_touch_enabled:
        return False, "zero touch disabled"
    if action_type not in settings.zero_touch_allowed_actions:
        return False, "zero touch action not allowlisted"
    return True, "allowed"

def policy_decision(action_type: str, risk: str = "medium", approved: bool = False):
    allowed, reason = can_execute(action_type, approved)
    return {
        "status": "ok",
        "action_type": action_type,
        "risk": risk,
        "approved": approved,
        "execution_allowed": allowed,
        "decision_reason": reason,
        "human_approval_required": settings.require_human_approval and not approved,
    }

def zero_touch_decision(action_type: str, risk: str = "low"):
    allowed, reason = zero_touch_can_execute(action_type)
    return {
        "status": "ok",
        "action_type": action_type,
        "risk": risk,
        "zero_touch_allowed": allowed,
        "decision_reason": reason,
    }
