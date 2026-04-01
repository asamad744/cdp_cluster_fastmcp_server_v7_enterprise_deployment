# Cloudera AI Application Setup

Use this package as a Cloudera AI Application.

Application settings:
- Script: `serve_http.py`
- Arguments: leave empty

Install step:
```bash
pip install -r requirements.txt
```

Keep `CDP_CLUSTER_MAP_JSON` on a single line in `.env`.
Recommended first rollout:
- `CDP_ENABLE_WRITE_ACTIONS=false`
- `CDP_REQUIRE_HUMAN_APPROVAL=true`
- `CDP_ZERO_TOUCH_ENABLED=true`
- `CDP_ZERO_TOUCH_ALLOWED_ACTIONS=write_incident_memory,flush_alert_only`
