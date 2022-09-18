class PSNAWPException(Exception):
    """Base Exception for all PSNAWP Exceptions."""

    def __init__(self, message):
        super().__init__(message)


class PSNAWPIllegalArgumentError(PSNAWPException):
    """Exception raised if user gave wrong input to a function."""

    def __init__(self, message):
        super().__init__(message)


class PSNAWPNotFound(PSNAWPException):
    """Exception raised if resource not found."""

    def __init__(self, message):
        super().__init__(message)


class PSNAWPForbidden(PSNAWPException):
    """Exception for accessing an action is not allowed due to insufficient rights to a resource."""

    def __init__(self, message):
        super().__init__(message)


class PSNAWPAuthenticationError(PSNAWPException):
    """Exception for authentication related errors."""

    def __init__(self, message):
        super().__init__(message)
