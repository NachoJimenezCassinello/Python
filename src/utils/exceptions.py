"""Custom exceptions for the Salesforce toolkit."""

class SalesforceAuthError(Exception):
    """Raised when authentication fails (missing env vars, HTTP 4xx, etc.)."""


class SalesforceAPIError(Exception):
    """Raised for non‑successful API responses (HTTP 4xx/5xx)."""

    def __init__(self, status_code: int, message: str):
        super().__init__(f"{status_code}: {message}")
        self.status_code = status_code
        self.message = message
