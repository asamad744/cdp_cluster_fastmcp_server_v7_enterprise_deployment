from .config import settings

def prometheus_alert_context(cluster_key: str = "", query: str = ""):
    if not settings.prometheus_base_url:
        return {"status": "not_configured", "message": "PROMETHEUS_BASE_URL is not configured", "cluster_key": cluster_key, "query": query}
    return {"status": "ok", "cluster_key": cluster_key, "query": query, "note": "Prometheus integration scaffold only; extend with your alert query logic."}
