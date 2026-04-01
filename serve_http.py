import os
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
import uvicorn

from cdp_cluster_mcp_server.config import settings
from cdp_cluster_mcp_server.watchdog import runtime
from cdp_cluster_mcp_server.tools import (
    federated_cluster_inventory_tool, cluster_discovery_tool, cluster_health_tool, service_health_tool,
    impala_spike_analysis_tool, impala_rca_tool, storage_rca_tool, cluster_rca_summary_tool,
    autonomous_remediation_plan_tool, execution_plan_tool, approval_package_tool, policy_decision_tool,
    approval_status_tool, prepare_restart_service_tool, execute_restart_service_tool,
    write_incident_memory_tool, incident_memory_list_tool, alert_payload_tool, slack_alert_tool,
    teams_alert_tool, chatops_message_tool, prometheus_alert_context_tool, autopilot_summary_tool,
    zero_touch_decision_tool, zero_touch_execute_tool, watchdog_tick_tool, watchdog_status_tool,
)

app = FastAPI(title="CDP Cluster FastMCP Server v7 Enterprise Deployment", version="0.7.0")
TOOL_MAP = {
    "federated_cluster_inventory_tool": federated_cluster_inventory_tool,
    "cluster_discovery_tool": cluster_discovery_tool,
    "cluster_health_tool": cluster_health_tool,
    "service_health_tool": service_health_tool,
    "impala_spike_analysis_tool": impala_spike_analysis_tool,
    "impala_rca_tool": impala_rca_tool,
    "storage_rca_tool": storage_rca_tool,
    "cluster_rca_summary_tool": cluster_rca_summary_tool,
    "autonomous_remediation_plan_tool": autonomous_remediation_plan_tool,
    "execution_plan_tool": execution_plan_tool,
    "approval_package_tool": approval_package_tool,
    "policy_decision_tool": policy_decision_tool,
    "approval_status_tool": approval_status_tool,
    "prepare_restart_service_tool": prepare_restart_service_tool,
    "execute_restart_service_tool": execute_restart_service_tool,
    "write_incident_memory_tool": write_incident_memory_tool,
    "incident_memory_list_tool": incident_memory_list_tool,
    "alert_payload_tool": alert_payload_tool,
    "slack_alert_tool": slack_alert_tool,
    "teams_alert_tool": teams_alert_tool,
    "chatops_message_tool": chatops_message_tool,
    "prometheus_alert_context_tool": prometheus_alert_context_tool,
    "autopilot_summary_tool": autopilot_summary_tool,
    "zero_touch_decision_tool": zero_touch_decision_tool,
    "zero_touch_execute_tool": zero_touch_execute_tool,
    "watchdog_tick_tool": watchdog_tick_tool,
    "watchdog_status_tool": watchdog_status_tool,
}

def require_token(authorization: str | None):
    expected = settings.http_bearer_token
    if not expected:
        return
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")
    token = authorization.split(" ", 1)[1].strip()
    if token != expected:
        raise HTTPException(status_code=401, detail="invalid bearer token")

@app.on_event("startup")
def startup():
    if settings.zero_touch_enabled:
        runtime.start(lambda: watchdog_tick_tool(cluster_key=settings.default_cluster_key))

@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": "cdp-cluster-fastmcp-server-v7"}

@app.get("/readyz")
def readyz():
    return {"status": "ready", "tool_count": len(TOOL_MAP), "default_cluster_key": settings.default_cluster_key}

@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    return "cdp_cluster_fastmcp_server_up 1\n"

@app.get("/mcp/tools")
def mcp_tools(authorization: str | None = Header(default=None)):
    require_token(authorization)
    return {"status": "ok", "tools": sorted(TOOL_MAP.keys())}

@app.post("/mcp/invoke/{tool_name}")
async def invoke(tool_name: str, payload: dict | None = None, authorization: str | None = Header(default=None)):
    require_token(authorization)
    if tool_name not in TOOL_MAP:
        raise HTTPException(status_code=404, detail="unknown tool")
    payload = payload or {}
    result = TOOL_MAP[tool_name](**payload)
    return JSONResponse({"status": "ok", "tool": tool_name, "result": result})

def main():
    port = int(os.getenv("CDSW_APP_PORT", os.getenv("MCP_HTTP_PORT", "8000")))
    uvicorn.run(app, host=os.getenv("MCP_HTTP_HOST", "0.0.0.0"), port=port, reload=False)

if __name__ == "__main__":
    main()
