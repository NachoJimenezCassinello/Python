"""Handles OAuth 2.0 Client‑Credentials flow and token caching."""
from __future__ import annotations

import os
import time
from typing import Dict

import requests
from dotenv import load_dotenv

from src.utils.exceptions import SalesforceAuthError

__all__ = ["SalesforceAuth"]


class SalesforceAuth:
    """Obtain & refresh an access token via client‑credentials flow."""

    _SAFETY_MARGIN = 0.9  # refresh a bit before true expiry

    def __init__(self, *, domain: str | None = None):
        load_dotenv()
        self._client_id: str | None = os.getenv("SF_CLIENT_ID")
        self._client_secret: str | None = os.getenv("SF_CLIENT_SECRET")
        self._domain: str | None = domain or os.getenv("SF_DOMAIN")

        if not all([self._client_id, self._client_secret, self._domain]):
            raise SalesforceAuthError(
                "SF_CLIENT_ID, SF_CLIENT_SECRET and SF_DOMAIN must be set in env"
            )

        self._token_url = f"https://{self._domain}/services/oauth2/token"
        self._token: str | None = None
        self._instance_url: str | None = None
        self._expires_at: float = 0.0

    # ---------------------------------------------------------------------
    # public API
    # ---------------------------------------------------------------------
    @property
    def access_token(self) -> str:
        """Return a valid token, refreshing if needed."""
        if time.time() >= self._expires_at:
            self._refresh()
        return self._token  # type: ignore [return-value]

    @property
    def instance_url(self) -> str:
        if not self._instance_url:
            self._refresh()
        return self._instance_url  # type: ignore [return-value]

    # ------------------------------------------------------------------
    # internal helpers
    # ------------------------------------------------------------------
    def _refresh(self) -> None:
        payload = {
            "grant_type": "client_credentials",
            "client_id": self._client_id,
            "client_secret": self._client_secret
            # "scope": self._scope,
        }
        try:
            resp = requests.post(self._token_url, data=payload, timeout=15)
            resp.raise_for_status()
        except requests.RequestException as exc:
            raise SalesforceAuthError(f"Token request failed: {exc}") from exc

        js: Dict[str, str] = resp.json()
        print("js: "+str(js))
        self._token = js["access_token"]
        self._instance_url = js["instance_url"]
        ttl = int(js.get("expires_in", 900))  # default 15 min
        self._expires_at = time.time() + ttl * self._SAFETY_MARGIN