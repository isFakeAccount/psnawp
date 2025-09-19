"""Provide exception classes for the psnawp package."""

import json
from typing import Any


class PSNAWPError(Exception):
    """Base Exception for all PSNAWP Exceptions."""

    def __init__(
        self,
        response: str,
    ) -> None:
        """Initialize the exception."""
        self.code: int | None = None
        self.message: str | None = None
        self.reference_id: str | None = None
        try:
            error: dict[str, dict[str, Any]] = json.loads(response)
        except json.JSONDecodeError:
            pass
        else:
            err = error.get("error", {})
            self.reference_id = err.get("referenceId")
            self.code = err.get("code")
            self.message = err.get("message")

        super().__init__(self.message or response)


class PSNAWPServerError(PSNAWPError):
    """Exception raised if there is a problem at the server."""


class PSNAWPClientError(PSNAWPError):
    """Exception raised if there is a problem at the client."""


class PSNAWPAuthenticationError(PSNAWPClientError):
    """Exception for authentication related errors."""


class PSNAWPBadRequestError(PSNAWPClientError):
    """Exception raised if bad request is made to the endpoint."""


class PSNAWPIllegalArgumentError(PSNAWPClientError):
    """Exception raised if user gave wrong input to a function."""


class PSNAWPUnauthorizedError(PSNAWPClientError):
    """Exception for accessing an action is not allowed due to missing the right authorization."""


class PSNAWPInvalidTokenError(PSNAWPClientError):
    """Exception raised if user gave unparsable npsso token string."""


class PSNAWPForbiddenError(PSNAWPClientError):
    """Exception for accessing an action is not allowed due to insufficient rights to a resource."""


class PSNAWPNotFoundError(PSNAWPClientError):
    """Exception raised if resource not found."""


class PSNAWPNotAllowedError(PSNAWPClientError):
    """Exception raised if resource doesn't support this method."""


class PSNAWPTooManyRequestsError(PSNAWPClientError):
    """Exception raised if client sends too many requests."""
