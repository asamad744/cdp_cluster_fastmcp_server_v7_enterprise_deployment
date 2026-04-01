<<<<<<< HEAD
# cdp_cluster_fastmcp_server_v7_enterprise_deployment
=======
# CDP Cluster FastMCP Server v7 — Enterprise Deployment

Enterprise deployment pack for a CDP / Cloudera Manager FastMCP server with:
- multi-cluster routing
- RCA tools
- autonomous remediation planning
- alerting tools
- policy decisions
- approval packages
- incident memory
- zero-touch watchdog loop
- CML-ready single-port HTTP deployment
- bearer-token auth for HTTP mode
- health and metrics endpoints
- Docker and Kubernetes examples

## Deploy in CML
- Script: `serve_http.py`
- Arguments: leave empty

## Local HTTP run
```bash
pip install -r requirements.txt
cp .env.example .env
python serve_http.py
```

## Local STDIO run
```bash
pip install -r requirements.txt
python -m cdp_cluster_mcp_server.stdio_server
```
>>>>>>> 19682ef (Initial v7 enterprise deployment)
