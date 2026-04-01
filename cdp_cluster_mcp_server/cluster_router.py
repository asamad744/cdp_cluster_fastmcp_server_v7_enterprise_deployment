from .config import settings

def get_cluster_config(cluster_key=None):
    key = cluster_key or settings.default_cluster_key
    return key, settings.cluster_map.get(key, {})

def federated_inventory():
    result = []
    for key, cfg in settings.cluster_map.items():
        result.append({
            "cluster_key": key,
            "cluster_name": cfg.get("cluster_name", ""),
            "cm_host": cfg.get("cm_host", ""),
            "configured": all(cfg.get(k) for k in ["cm_host", "cm_username", "cm_password", "cluster_name"]),
        })
    return {"status": "ok", "clusters": result, "default_cluster_key": settings.default_cluster_key}
