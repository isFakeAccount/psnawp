"""Core package for the PlayStation API wrapper.

This package contains the foundational modules responsible for handling core functionalities such as authentication,
request management, and exception handling.

Modules in this package include:

- Authentication setup and token refresh.
- HTTP session and request logic.
- Custom exception classes and error handling utilities.

"""

from psnawp_api.core.authenticator import Authenticator
from psnawp_api.core.psnawp_exceptions import (
    PSNAWPAuthenticationError,
    PSNAWPBadRequestError,
    PSNAWPClientError,
    PSNAWPError,
    PSNAWPForbiddenError,
    PSNAWPIllegalArgumentError,
    PSNAWPNotAllowedError,
    PSNAWPNotFoundError,
    PSNAWPServerError,
    PSNAWPTooManyRequestsError,
    PSNAWPUnauthorizedError,
)
from psnawp_api.core.request_builder import (
    RequestBuilder,
    RequestBuilderHeaders,
    RequestOptions,
)

__all__ = [
    "Authenticator",
    "PSNAWPAuthenticationError",
    "PSNAWPBadRequestError",
    "PSNAWPClientError",
    "PSNAWPError",
    "PSNAWPForbiddenError",
    "PSNAWPIllegalArgumentError",
    "PSNAWPNotAllowedError",
    "PSNAWPNotFoundError",
    "PSNAWPServerError",
    "PSNAWPTooManyRequestsError",
    "PSNAWPUnauthorizedError",
    "RequestBuilder",
    "RequestBuilderHeaders",
    "RequestOptions",
]
