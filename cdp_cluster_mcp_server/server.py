from fastmcp import FastMCP
from .tools import (
    cluster_discovery_tool, federated_cluster_inventory_tool, cluster_health_tool, service_health_tool,
    impala_spike_analysis_tool, approval_status_tool, prepare_restart_service_tool,
    execute_restart_service_tool, write_incident_memory_tool, incident_memory_list_tool,
    impala_rca_tool, storage_rca_tool, cluster_rca_summary_tool, autonomous_remediation_plan_tool,
    execution_plan_tool, approval_package_tool, policy_decision_tool, zero_touch_decision_tool,
    zero_touch_execute_tool, watchdog_tick_tool, watchdog_status_tool, alert_payload_tool,
    slack_alert_tool, teams_alert_tool, chatops_message_tool, prometheus_alert_context_tool,
    autopilot_summary_tool,
)

mcp = FastMCP("CDP Cluster MCP Server v7 Enterprise Deployment")
for tool in [
    cluster_discovery_tool, federated_cluster_inventory_tool, cluster_health_tool, service_health_tool,
    impala_spike_analysis_tool, approval_status_tool, prepare_restart_service_tool,
    execute_restart_service_tool, write_incident_memory_tool, incident_memory_list_tool,
    impala_rca_tool, storage_rca_tool, cluster_rca_summary_tool, autonomous_remediation_plan_tool,
    execution_plan_tool, approval_package_tool, policy_decision_tool, zero_touch_decision_tool,
    zero_touch_execute_tool, watchdog_tick_tool, watchdog_status_tool, alert_payload_tool,
    slack_alert_tool, teams_alert_tool, chatops_message_tool, prometheus_alert_context_tool,
    autopilot_summary_tool,
]:
    mcp.tool()(tool)
