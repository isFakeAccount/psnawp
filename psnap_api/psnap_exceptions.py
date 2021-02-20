# Class PSNAPException
# Used to generate custom exceptions for the API


class PSNAPException(Exception):
    """
    Generic Exception
    """

    def __init__(self, message):
        super().__init__(message)


class PSNAPIllegalArgumentError(Exception):
    """
    Exception raised if user gave wrong input to a function
    """

    def __init__(self, message):
        super().__init__(message)


class PSNAPInvalidRequestError(Exception):
    """
    Exception raised if user request was invalid
    """

    def __init__(self, message):
        super().__init__(message)


class PSNAPAuthenticationError(Exception):
    """
    Exception for authentication related errors
    """

    def __init__(self, message):
        super().__init__(message)


class PSNAPServerError(Exception):
    """
    Exception if the PSN server starts giving server errors
    """

    def __init__(self, message):
        super().__init__(message)
