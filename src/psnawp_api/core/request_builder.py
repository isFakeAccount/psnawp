from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeAlias, TypedDict, cast

from requests import Response, request
from typing_extensions import NotRequired, Unpack

from psnawp_api.core.psnawp_exceptions import (
    PSNAWPBadRequest,
    PSNAWPClientError,
    PSNAWPForbidden,
    PSNAWPNotAllowed,
    PSNAWPNotFound,
    PSNAWPServerError,
    PSNAWPTooManyRequests,
    PSNAWPUnauthorized,
)

if TYPE_CHECKING:
    from requests.sessions import RequestsCookieJar, _Auth, _Cert, _Data, _Files, _HooksInput, _Params, _Timeout, _Verify


def response_checker(response: Response) -> None:
    """Checks the HTTP(S) response and raises corresponding PSNAWP exceptions.

    This function examines the status code of the HTTP response and raises PSNAWP exceptions based on error conditions.

    :param response: The HTTP response object.
    :type response: requests.Response

    :raises: If the status code is 400.

    :raises: If the status code is 401.

    :raises: If the status code is 403.

    :raises: If the status code is 404.

    :raises: If the status code is 405.

    :raises: If the status code is 429.

    :raises: If the status code is in the 4xx range (excluding the one listed above).

    :raises: If the status code is 500 or above.

    """
    if response.status_code == 400:
        raise PSNAWPBadRequest(response.text)
    elif response.status_code == 401:
        raise PSNAWPUnauthorized(response.text)
    elif response.status_code == 403:
        raise PSNAWPForbidden(response.text)
    elif response.status_code == 404:
        raise PSNAWPNotFound(response.text)
    elif response.status_code == 405:
        raise PSNAWPNotAllowed(response.text)
    elif response.status_code == 429:
        raise PSNAWPTooManyRequests(response.text)
    elif 400 <= response.status_code < 500:
        raise PSNAWPClientError(response.text)
    elif response.status_code >= 500:
        raise PSNAWPServerError(response.text)
    else:
        response.raise_for_status()


RequestBuilderHeaders = TypedDict(
    "RequestBuilderHeaders",
    {
        "User-Agent": str,
        "Content-Type": str,
        "Accept-Language": str,
        "Country": str,
    },
)

_TextMapping: TypeAlias = dict[str, str]


class RequestOptions(TypedDict):
    allow_redirects: NotRequired[bool]
    auth: NotRequired[_Auth]
    cert: NotRequired[_Cert]
    cookies: NotRequired[RequestsCookieJar | _TextMapping]
    data: NotRequired[_Data]
    files: NotRequired[_Files]
    headers: NotRequired[_TextMapping]
    hooks: NotRequired[_HooksInput]
    json: NotRequired[Any]
    params: NotRequired[_Params]
    proxies: NotRequired[_TextMapping]
    stream: NotRequired[bool]
    timeout: NotRequired[_Timeout]
    url: str | bytes
    verify: NotRequired[_Verify]


class RequestBuilder:
    """Handles all the HTTP Requests and provides a gateway to interacting with PSN API.

    :param default_headers: Default headers for the requests.
    :type default_headers: Unpack[RequestBuilderHeaders]

    """

    def __init__(self, **default_headers: Unpack[RequestBuilderHeaders]) -> None:
        """Initialize Request Handler with default headers."""
        self.default_headers = cast(dict[str, str], default_headers)

    def request(self, method: str | bytes, **kwargs: Unpack[RequestOptions]) -> Response:
        """Handles HTTP requests and returns the requests.Response object.

        :param method: The HTTP method to use for the request (e.g., GET, PATCH).
        :type method: str | bytes
        :param kwargs: The options for the HTTP request.
        :type kwargs: Unpack[RequestOptions]

        :returns: The Request Response Object.
        :rtype: requests.Response

        :

        """
        kwargs["headers"] = self.default_headers | kwargs.get("headers", {})
        response = request(method=method, **kwargs)
        response_checker(response)
        return response

    def get(self, **kwargs: Unpack[RequestOptions]) -> Response:
        """Handles the GET requests and returns the requests.Response object.

        :param kwargs: The options for the GET request.
        :type kwargs: Unpack[RequestOptions]

        :returns: The Request Response Object.
        :rtype: requests.Response

        """
        return self.request(method="get", **kwargs)

    def patch(self, **kwargs: Unpack[RequestOptions]) -> Response:
        """Handles the PATCH requests and returns the requests.Response object.

        :param kwargs: The options for the PATCH request.
        :type kwargs: Unpack[RequestOptions]

        :returns: The Request Response Object.
        :rtype: requests.Response

        """
        return self.request(method="patch", **kwargs)

    def post(self, **kwargs: Unpack[RequestOptions]) -> Response:
        """Handles the POST requests and returns the requests.Response object.

        :param kwargs: The options for the POST request.
        :type kwargs: Unpack[RequestOptions]

        :returns: The Request Response Object.
        :rtype: requests.Response

        """
        return self.request(method="post", **kwargs)

    def put(self, **kwargs: Unpack[RequestOptions]) -> Response:
        """Handles the PUT requests and returns the requests.Response object.

        :param kwargs: The options for the PUT request.
        :type kwargs: Unpack[RequestOptions]

        :returns: The Request Response Object.
        :rtype: requests.Response

        """
        return self.request(method="put", **kwargs)

    def delete(self, **kwargs: Unpack[RequestOptions]) -> Response:
        """Handles the DELETE requests and returns the requests.Response object.

        :param kwargs: The options for the DELETE request.
        :type kwargs: Unpack[RequestOptions]

        :returns: The Request Response Object.
        :rtype: requests.Response

        """
        return self.request(method="delete", **kwargs)

    def head(self, **kwargs: Unpack[RequestOptions]) -> Response:
        """Handles the HEAD requests and returns the requests.Response object.

        :param kwargs: The options for the HEAD request.
        :type kwargs: Unpack[RequestOptions]

        :returns: The Request Response Object.
        :rtype: requests.Response

        """
        return self.request(method="head", **kwargs)

    def options(self, **kwargs: Unpack[RequestOptions]) -> Response:
        """Handles the OPTIONS requests and returns the requests.Response object.

        :param kwargs: The options for the OPTIONS request.
        :type kwargs: Unpack[RequestOptions]

        :returns: The Request Response Object.
        :rtype: requests.Response

        """
        return self.request(method="options", **kwargs)
