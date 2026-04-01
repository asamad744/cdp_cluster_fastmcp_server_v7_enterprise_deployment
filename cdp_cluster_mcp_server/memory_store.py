import json
import os
import time
from .config import settings

def write_incident(payload):
    os.makedirs(settings.memory_store_path, exist_ok=True)
    incident_id = payload.get("incident_id") or f"incident_{int(time.time())}"
    path = os.path.join(settings.memory_store_path, f"{incident_id}.json")
    data = {"incident_id": incident_id, **payload}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return {"status": "ok", "incident_id": incident_id, "path": os.path.abspath(path)}

def list_incidents():
    os.makedirs(settings.memory_store_path, exist_ok=True)
    files = sorted([f for f in os.listdir(settings.memory_store_path) if f.endswith(".json")])
    return {"status": "ok", "count": len(files), "incidents": files}
