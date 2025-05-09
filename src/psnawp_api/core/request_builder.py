"""Provides the HTTP request handling interface."""

from __future__ import annotations

from http import HTTPStatus
from logging import getLogger
from typing import TYPE_CHECKING, Any, TypeAlias, TypedDict, cast

from pyrate_limiter import Duration, Limiter, LimiterDelayException
from pyrate_limiter.buckets.sqlite_bucket import SQLiteBucket
from requests import Session
from typing_extensions import NotRequired, Unpack

from psnawp_api.core.psnawp_exceptions import (
    PSNAWPBadRequestError,
    PSNAWPClientError,
    PSNAWPForbiddenError,
    PSNAWPNotAllowedError,
    PSNAWPNotFoundError,
    PSNAWPServerError,
    PSNAWPTooManyRequestsError,
    PSNAWPUnauthorizedError,
)
from psnawp_api.utils import get_temp_db_path

if TYPE_CHECKING:
    from pyrate_limiter import Rate
    from requests import Response
    from requests.sessions import (
        RequestsCookieJar,
        _Auth,
        _Cert,
        _Data,
        _Files,
        _HooksInput,
        _Params,
        _Timeout,
        _Verify,
    )

request_builder_logger = getLogger("psnawp")


def response_checker(response: Response) -> None:
    """Checks the HTTP(S) response and raises corresponding PSNAWP exceptions.

    This function examines the status code of the HTTP response and raises PSNAWP exceptions based on error conditions.

    :param requests.Response response: The HTTP response object.

    :raises PSNAWPBadRequestError: If the HTTP response status code is 400.
    :raises PSNAWPUnauthorizedError: If the HTTP response status code is 401.
    :raises PSNAWPForbiddenError: If the HTTP response status code is 403.
    :raises PSNAWPNotFoundError: If the HTTP response status code is 404.
    :raises PSNAWPNotAllowedError: If the HTTP response status code is 405.
    :raises PSNAWPTooManyRequestsError: If the HTTP response status code is 429.
    :raises PSNAWPClientError: If the HTTP response status code is in the 4xx range (excluding those listed above).
    :raises PSNAWPServerError: If the HTTP response status code is 500 or above.

    """
    if response.status_code == HTTPStatus.BAD_REQUEST:
        raise PSNAWPBadRequestError(response.text)
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        raise PSNAWPUnauthorizedError(response.text)
    if response.status_code == HTTPStatus.FORBIDDEN:
        raise PSNAWPForbiddenError(response.text)
    if response.status_code == HTTPStatus.NOT_FOUND:
        raise PSNAWPNotFoundError(response.text)
    if response.status_code == HTTPStatus.METHOD_NOT_ALLOWED:
        raise PSNAWPNotAllowedError(response.text)
    if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
        raise PSNAWPTooManyRequestsError(response.text)
    if HTTPStatus.BAD_REQUEST <= response.status_code < HTTPStatus.INTERNAL_SERVER_ERROR:
        raise PSNAWPClientError(response.text)
    if response.status_code >= HTTPStatus.INTERNAL_SERVER_ERROR:
        raise PSNAWPServerError(response.text)
    response.raise_for_status()


RequestBuilderHeaders = TypedDict(
    "RequestBuilderHeaders",
    {
        "User-Agent": str,
        "Accept-Language": str,
        "Country": str,
    },
)

_TextMapping: TypeAlias = dict[str, str]


class RequestOptions(TypedDict):
    """A typing stub for the options that can be passed to a `requests` request."""

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
    """Handles all the HTTP requests to PSN API and manages ratelimit.

    :var RequestBuilderHeaders common_headers: Headers that will be passed in each HTTPs request.
    :var ~requests_ratelimiter.LimiterSession session: :py:class:`~requests_ratelimiter.LimiterSession` object with
        built-in rate limit capabilities. Limit is hardcoded to 300 requests per 15 minutes.

    .. note::

        This class is intended to be used via :py:class:`~psnawp_api.core.authenticator.Authenticator`. If you want to
        override default headers for language and region, you may do so via
        :py:meth:`psnawp_api.psnawp.PSNAWP.__init__`.

    """

    def __init__(self, common_headers: RequestBuilderHeaders, rate_limit: Rate) -> None:
        """Initialize Request Handler with default headers.

        :param common_headers: Default headers for the requests.
        :param rate_limit: Controls pacing of HTTP requests to avoid service throttling.

        """
        self.common_headers = cast("dict[str, str]", common_headers)
        psn_api_rates = [rate_limit]

        db_path = get_temp_db_path()

        sqlite_bucket = SQLiteBucket.init_from_file(psn_api_rates, db_path=str(db_path))
        self.limiter = Limiter(sqlite_bucket, raise_when_fail=False, max_delay=Duration.SECOND * 3)

        self.session = Session()
        self.session.headers.update(self.common_headers)

    def request(
        self,
        method: str | bytes,
        **kwargs: Unpack[RequestOptions],
    ) -> Response:
        """Handles HTTP requests and returns the requests.Response object.

        :param method: The HTTP method to use for the request (e.g., GET, PATCH).
        :param kwargs: The options for the HTTP request.

        :returns: The Request Response Object.

        :raises PSNAWPBadRequestError: If the HTTP response status code is 400.
        :raises PSNAWPUnauthorizedError: If the HTTP response status code is 401.
        :raises PSNAWPForbiddenError: If the HTTP response status code is 403.
        :raises PSNAWPNotFoundError: If the HTTP response status code is 404.
        :raises PSNAWPNotAllowedError: If the HTTP response status code is 405.
        :raises PSNAWPTooManyRequestsError: If the HTTP response status code is 429.
        :raises PSNAWPClientError: If the HTTP response status code is in the 4xx range (excluding those listed above).
        :raises PSNAWPServerError: If the HTTP response status code is 500 or above.

        """
        request_builder_logger.debug(
            "Sending request: method=%s, url=%s, headers=%s, body=%s",
            method,
            kwargs.get("url"),
            kwargs.get("headers"),
            kwargs.get("data"),
        )
        try:
            self.limiter.try_acquire("psnawp-limiter")
        except LimiterDelayException as err:
            raise PSNAWPTooManyRequestsError("Rate limit exceeded: too many requests. Please retry again shortly.") from err

        response = self.session.request(method=method, **kwargs)
        request_builder_logger.debug(
            "Received response: status_code=%d, headers=%s, body=%s",
            response.status_code,
            response.headers,
            response.text,
        )
        response_checker(response)
        return response

    def get(self, **kwargs: Unpack[RequestOptions]) -> Response:
        """Handles the GET requests and returns the requests.Response object.

        :param kwargs: The options for the GET request.

        :returns: The Request Response Object.

        :raises PSNAWPBadRequestError: If the HTTP response status code is 400.
        :raises PSNAWPUnauthorizedError: If the HTTP response status code is 401.
        :raises PSNAWPForbiddenError: If the HTTP response status code is 403.
        :raises PSNAWPNotFoundError: If the HTTP response status code is 404.
        :raises PSNAWPNotAllowedError: If the HTTP response status code is 405.
        :raises PSNAWPTooManyRequestsError: If the HTTP response status code is 429.
        :raises PSNAWPClientError: If the HTTP response status code is in the 4xx range (excluding those listed above).
        :raises PSNAWPServerError: If the HTTP response status code is 500 or above.

        """
        return self.request(method="get", **kwargs)

    def patch(self, **kwargs: Unpack[RequestOptions]) -> Response:
        """Handles the PATCH requests and returns the requests.Response object.

        :param kwargs: The options for the PATCH request.

        :returns: The Request Response Object.

        :raises PSNAWPBadRequestError: If the HTTP response status code is 400.
        :raises PSNAWPUnauthorizedError: If the HTTP response status code is 401.
        :raises PSNAWPForbiddenError: If the HTTP response status code is 403.
        :raises PSNAWPNotFoundError: If the HTTP response status code is 404.
        :raises PSNAWPNotAllowedError: If the HTTP response status code is 405.
        :raises PSNAWPTooManyRequestsError: If the HTTP response status code is 429.
        :raises PSNAWPClientError: If the HTTP response status code is in the 4xx range (excluding those listed above).
        :raises PSNAWPServerError: If the HTTP response status code is 500 or above.

        """
        return self.request(method="patch", **kwargs)

    def post(self, **kwargs: Unpack[RequestOptions]) -> Response:
        """Handles the POST requests and returns the requests.Response object.

        :param kwargs: The options for the POST request.

        :returns: The Request Response Object.

        :raises PSNAWPBadRequestError: If the HTTP response status code is 400.
        :raises PSNAWPUnauthorizedError: If the HTTP response status code is 401.
        :raises PSNAWPForbiddenError: If the HTTP response status code is 403.
        :raises PSNAWPNotFoundError: If the HTTP response status code is 404.
        :raises PSNAWPNotAllowedError: If the HTTP response status code is 405.
        :raises PSNAWPTooManyRequestsError: If the HTTP response status code is 429.
        :raises PSNAWPClientError: If the HTTP response status code is in the 4xx range (excluding those listed above).
        :raises PSNAWPServerError: If the HTTP response status code is 500 or above.

        """
        return self.request(method="post", **kwargs)

    def put(self, **kwargs: Unpack[RequestOptions]) -> Response:
        """Handles the PUT requests and returns the requests.Response object.

        :param kwargs: The options for the PUT request.

        :returns: The Request Response Object.

        :raises PSNAWPBadRequestError: If the HTTP response status code is 400.
        :raises PSNAWPUnauthorizedError: If the HTTP response status code is 401.
        :raises PSNAWPForbiddenError: If the HTTP response status code is 403.
        :raises PSNAWPNotFoundError: If the HTTP response status code is 404.
        :raises PSNAWPNotAllowedError: If the HTTP response status code is 405.
        :raises PSNAWPTooManyRequestsError: If the HTTP response status code is 429.
        :raises PSNAWPClientError: If the HTTP response status code is in the 4xx range (excluding those listed above).
        :raises PSNAWPServerError: If the HTTP response status code is 500 or above.

        """
        return self.request(method="put", **kwargs)

    def delete(self, **kwargs: Unpack[RequestOptions]) -> Response:
        """Handles the DELETE requests and returns the requests.Response object.

        :param kwargs: The options for the DELETE request.

        :returns: The Request Response Object.

        :raises PSNAWPBadRequestError: If the HTTP response status code is 400.
        :raises PSNAWPUnauthorizedError: If the HTTP response status code is 401.
        :raises PSNAWPForbiddenError: If the HTTP response status code is 403.
        :raises PSNAWPNotFoundError: If the HTTP response status code is 404.
        :raises PSNAWPNotAllowedError: If the HTTP response status code is 405.
        :raises PSNAWPTooManyRequestsError: If the HTTP response status code is 429.
        :raises PSNAWPClientError: If the HTTP response status code is in the 4xx range (excluding those listed above).
        :raises PSNAWPServerError: If the HTTP response status code is 500 or above.

        """
        return self.request(method="delete", **kwargs)

    def head(self, **kwargs: Unpack[RequestOptions]) -> Response:
        """Handles the HEAD requests and returns the requests.Response object.

        :param kwargs: The options for the HEAD request.

        :returns: The Request Response Object.

        :raises PSNAWPBadRequestError: If the HTTP response status code is 400.
        :raises PSNAWPUnauthorizedError: If the HTTP response status code is 401.
        :raises PSNAWPForbiddenError: If the HTTP response status code is 403.
        :raises PSNAWPNotFoundError: If the HTTP response status code is 404.
        :raises PSNAWPNotAllowedError: If the HTTP response status code is 405.
        :raises PSNAWPTooManyRequestsError: If the HTTP response status code is 429.
        :raises PSNAWPClientError: If the HTTP response status code is in the 4xx range (excluding those listed above).
        :raises PSNAWPServerError: If the HTTP response status code is 500 or above.

        """
        return self.request(method="head", **kwargs)

    def options(self, **kwargs: Unpack[RequestOptions]) -> Response:
        """Handles the OPTIONS requests and returns the requests.Response object.

        :param kwargs: The options for the OPTIONS request.

        :returns: The Request Response Object.

        :raises PSNAWPBadRequestError: If the HTTP response status code is 400.
        :raises PSNAWPUnauthorizedError: If the HTTP response status code is 401.
        :raises PSNAWPForbiddenError: If the HTTP response status code is 403.
        :raises PSNAWPNotFoundError: If the HTTP response status code is 404.
        :raises PSNAWPNotAllowedError: If the HTTP response status code is 405.
        :raises PSNAWPTooManyRequestsError: If the HTTP response status code is 429.
        :raises PSNAWPClientError: If the HTTP response status code is in the 4xx range (excluding those listed above).
        :raises PSNAWPServerError: If the HTTP response status code is 500 or above.

        """
        return self.request(method="options", **kwargs)
