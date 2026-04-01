from typing import Any, Dict, Optional
import requests
from .cluster_router import get_cluster_config

class CMClient:
    def configured(self, cluster_key=None) -> bool:
        _, cfg = get_cluster_config(cluster_key)
        return bool(cfg.get("cm_host") and cfg.get("cm_username") and cfg.get("cm_password") and cfg.get("cluster_name"))

    def base_url(self, cluster_key=None) -> str:
        _, cfg = get_cluster_config(cluster_key)
        scheme = "https" if bool(cfg.get("cm_use_tls", False)) else "http"
        return f"{scheme}://{cfg.get('cm_host','')}:{cfg.get('cm_port',7180)}/api/{cfg.get('cm_api_version','v40')}"

    def request(self, method: str, path: str, cluster_key=None, params: Optional[Dict[str, Any]] = None, body: Optional[Dict[str, Any]] = None) -> Any:
        key, cfg = get_cluster_config(cluster_key)
        url = f"{self.base_url(key)}/{path.lstrip('/')}"
        response = requests.request(
            method=method,
            url=url,
            auth=(cfg.get("cm_username",""), cfg.get("cm_password","")),
            params=params,
            json=body,
            timeout=45,
            verify=bool(cfg.get("cm_verify_tls", True)),
        )
        response.raise_for_status()
        if "application/json" in response.headers.get("content-type", ""):
            return response.json()
        return {"raw": response.text}

cm_client = CMClient()
