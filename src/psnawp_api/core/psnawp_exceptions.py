"""Provide exception classes for the psnawp package."""


class PSNAWPError(Exception):
    """Base Exception for all PSNAWP Exceptions."""


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
