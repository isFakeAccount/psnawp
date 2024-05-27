class PSNAWPException(Exception):
    """Base Exception for all PSNAWP Exceptions."""


class PSNAWPServerError(PSNAWPException):
    """Exception raised if there is a problem at the server."""


class PSNAWPClientError(PSNAWPException):
    """Exception raised if there is a problem at the client."""


class PSNAWPAuthenticationError(PSNAWPClientError):
    """Exception for authentication related errors."""


class PSNAWPBadRequest(PSNAWPClientError):
    """Exception raised if bad request is made to the endpoint."""


class PSNAWPIllegalArgumentError(PSNAWPClientError):
    """Exception raised if user gave wrong input to a function."""


class PSNAWPUnauthorized(PSNAWPClientError):
    """Exception for accessing an action is not allowed due to missing the right authorization."""


class PSNAWPForbidden(PSNAWPClientError):
    """Exception for accessing an action is not allowed due to insufficient rights to a resource."""


class PSNAWPNotFound(PSNAWPClientError):
    """Exception raised if resource not found."""


class PSNAWPNotAllowed(PSNAWPClientError):
    """Exception raised if resource doesn't support this method."""


class PSNAWPTooManyRequests(PSNAWPClientError):
    """Exception raised if client sends too many requests."""
