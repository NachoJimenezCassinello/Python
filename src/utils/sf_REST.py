"""High‑level helpers for SOQL, Composite API and Platform Events."""
from __future__ import annotations

from typing import Any, Dict, List

import requests

from src.utils.exceptions import SalesforceAPIError
from src.utils.sf_auth import SalesforceAuth

__all__ = ["SalesforceREST"]


class SalesforceREST:
    """Wraps common REST calls, reusing the token from SalesforceAuth."""

    def __init__(self, auth: SalesforceAuth, *, version: str = "v60.0"):
        self._auth = auth
        self._v = version

    # ------------------------------- helpers ----------------------------- #
    def _headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self._auth.access_token}"}

    def _request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:  # noqa: ANN001
        url = f"{self._auth.instance_url}{path}"
        hdrs = {**self._headers(), **kwargs.pop("headers", {})}
        try:
            resp = requests.request(method, url, headers=hdrs, timeout=15, **kwargs)
            resp.raise_for_status()
        except requests.HTTPError as exc:
            raise SalesforceAPIError(resp.status_code, resp.text) from exc  # type: ignore[arg-type]
        except requests.RequestException as exc:
            raise SalesforceAPIError(-1, str(exc)) from exc
        return resp.json()

    # ------------------------------- SOQL ------------------------------- #
    def query(self, soql: str) -> List[Dict[str, Any]]:
        data = self._request(
            "GET",
            f"/services/data/{self._v}/query",
            params={"q": soql},
        )
        return data.get("records", [])

    # ---------------------------- Composite ----------------------------- #
    def composite(self, requests_batch: List[Dict[str, Any]], *, all_or_none: bool = True, bulk: bool = False):
        body = {"allOrNone": all_or_none, "collateSubrequests": bulk, "compositeRequest": requests_batch}
        return self._request("POST", f"/services/data/{self._v}/composite", json=body)

    def composite_query(self, soql: str):
        return self._request(
            "GET", f"/services/data/{self._v}/composite/query", params={"q": soql}
        )

    # ------------------------- Platform Events -------------------------- #
    def publish_event(self, api_name: str, payload: Dict[str, Any]):
        return self._request("POST", f"/services/data/{self._v}/sobjects/{api_name}", json=payload)