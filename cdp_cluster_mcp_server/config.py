import json
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

def _as_bool(value, default):
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}

@dataclass
class Settings:
    cluster_map_json_raw: str = os.getenv("CDP_CLUSTER_MAP_JSON", "{}")
    default_cluster_key: str = os.getenv("CDP_DEFAULT_CLUSTER_KEY", "prod")
    impala_log_path: str = os.getenv("CDP_IMPALA_LOG_PATH", "/var/log/impala/impalad.INFO")

    enable_write_actions: bool = _as_bool(os.getenv("CDP_ENABLE_WRITE_ACTIONS"), False)
    require_human_approval: bool = _as_bool(os.getenv("CDP_REQUIRE_HUMAN_APPROVAL"), True)
    allowed_actions_raw: str = os.getenv("CDP_ALLOWED_ACTIONS", "restart_service_guarded,write_incident_memory,flush_alert_only")
    zero_touch_enabled: bool = _as_bool(os.getenv("CDP_ZERO_TOUCH_ENABLED"), True)
    zero_touch_allowed_actions_raw: str = os.getenv("CDP_ZERO_TOUCH_ALLOWED_ACTIONS", "write_incident_memory,flush_alert_only")
    memory_store_path: str = os.getenv("CDP_MEMORY_STORE_PATH", "memory/incidents")
    watchdog_interval_seconds: int = int(os.getenv("CDP_WATCHDOG_INTERVAL_SECONDS", "60"))

    slack_webhook_url: str = os.getenv("CDP_SLACK_WEBHOOK_URL", "")
    teams_webhook_url: str = os.getenv("CDP_TEAMS_WEBHOOK_URL", "")
    prometheus_base_url: str = os.getenv("PROMETHEUS_BASE_URL", "")
    prometheus_bearer_token: str = os.getenv("PROMETHEUS_BEARER_TOKEN", "")

    http_host: str = os.getenv("MCP_HTTP_HOST", "0.0.0.0")
    http_port: int = int(os.getenv("MCP_HTTP_PORT", "8000"))
    http_bearer_token: str = os.getenv("MCP_HTTP_BEARER_TOKEN", "")
    log_level: str = os.getenv("MCP_LOG_LEVEL", "INFO")

    @property
    def cluster_map(self):
        try:
            value = json.loads(self.cluster_map_json_raw)
            return value if isinstance(value, dict) else {}
        except Exception:
            return {}

    @property
    def allowed_actions(self):
        return {x.strip() for x in self.allowed_actions_raw.split(",") if x.strip()}

    @property
    def zero_touch_allowed_actions(self):
        return {x.strip() for x in self.zero_touch_allowed_actions_raw.split(",") if x.strip()}

settings = Settings()
