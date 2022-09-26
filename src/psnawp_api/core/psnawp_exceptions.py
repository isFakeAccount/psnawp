class PSNAWPException(Exception):
    """Base Exception for all PSNAWP Exceptions."""


class PSNAWPAuthenticationError(PSNAWPException):
    """Exception for authentication related errors."""


class PSNAWPBadRequest(PSNAWPException):
    """Exception raised if bad request is made to the endpoint."""


class PSNAWPIllegalArgumentError(PSNAWPException):
    """Exception raised if user gave wrong input to a function."""


class PSNAWPUnauthorized(PSNAWPException):
    """Exception for accessing an action is not allowed due to missing the right authorization."""


class PSNAWPForbidden(PSNAWPException):
    """Exception for accessing an action is not allowed due to insufficient rights to a resource."""


class PSNAWPNotFound(PSNAWPException):
    """Exception raised if resource not found."""


class PSNAWPNotAllowed(PSNAWPException):
    """Exception raised if resource doesn't support this method."""


class PSNAWPServerError(PSNAWPException):
    """Exception raised if there is a problem at the server."""
