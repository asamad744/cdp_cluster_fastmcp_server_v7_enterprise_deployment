# Agent Studio HTTP Tool Setup

Use the CML Application URL as the MCP HTTP base.

Headers:
- `Authorization: Bearer <MCP_HTTP_BEARER_TOKEN>`
- `Content-Type: application/json`

Example tools:
- `POST /mcp/invoke/autopilot_summary_tool` with `{"cluster_key":"prod"}`
- `POST /mcp/invoke/zero_touch_decision_tool` with `{"cluster_key":"prod"}`
- `POST /mcp/invoke/watchdog_status_tool` with `{}`
- `POST /mcp/invoke/approval_package_tool` with `{"cluster_key":"prod"}`
