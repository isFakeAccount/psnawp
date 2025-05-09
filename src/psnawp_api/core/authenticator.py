"""Provides Authentication and Authorization classes."""

from __future__ import annotations

import time
import uuid
from functools import wraps
from typing import TYPE_CHECKING, ClassVar, TypedDict, TypeVar, cast
from urllib.parse import parse_qs, urlparse

from typing_extensions import NotRequired, ParamSpec, Unpack

from psnawp_api.core.psnawp_exceptions import PSNAWPAuthenticationError
from psnawp_api.core.request_builder import RequestBuilder
from psnawp_api.utils import API_PATH, BASE_PATH

if TYPE_CHECKING:
    from collections.abc import Callable

    from pyrate_limiter import Rate
    from requests import Response

    from psnawp_api.core.request_builder import RequestBuilderHeaders, RequestOptions

PT = ParamSpec("PT")
RT = TypeVar("RT")


def pre_request_processing(method: Callable[PT, RT]) -> Callable[PT, RT]:
    """A decorator that ensures the authenticator has a valid access token before making an HTTP request.

    If the access token is missing or expired, it fetches a new token using the refresh token or npsso cookie.

    :param method: The decorated HTTP request method.

    :returns: The wrapped method with token validation logic applied.

    """

    @wraps(method)
    def _impl(*method_args: PT.args, **method_kwargs: PT.kwargs) -> RT:
        authenticator_obj = cast("Authenticator", method_args[0])
        if authenticator_obj.token_response is None:
            authorization_code = authenticator_obj.get_authorization_code()
            authenticator_obj.fetch_access_token_from_authorization(authorization_code)
        else:
            authenticator_obj.fetch_access_token_from_refresh()

        return method(*method_args, **method_kwargs)

    return _impl


class TokenResponse(TypedDict):
    """Represents the token response from Sony's authentication and token refresh APIs.

    This includes the access token, refresh token, their expiration times, and additional metadata related to the
    authorization process.

    """

    access_token_expires_at: NotRequired[float]
    access_token: str
    expires_in: int
    id_token: str
    refresh_token_expires_at: NotRequired[float]
    refresh_token_expires_in: int
    refresh_token: str
    scope: str
    token_type: str


class Authenticator:
    """Provides an interface for PSN Authentication and API.

    :var str npsso_cookie: The NPSSO cookie, which is required for obtaining an access token from the PSN API.
    :var RequestBuilderHeaders common_headers: Headers that will be passed in each HTTPs request.
    :var RequestBuilder request_builder: A :py:class:`~psnawp_api.core.request_builder.RequestBuilder` object that helps
        in constructing and sending HTTP requests.
    :var TokenResponse | None token_response: Stores the token response from PlayStation API to keep track of access
        token, refresh token, their expiration times.
    :var str cid: The client ID, a unique identifier for the client, generated using the device's MAC address.

    .. note::

        This class is intended to be used via PSNAWP. See :py:meth:`psnawp_api.psnawp.PSNAWP.__init__`

    """

    AUTH_METADATA: ClassVar[dict[str, str]] = {
        "CLIENT_ID": "09515159-7237-4370-9b40-3806e67c0891",
        "SCOPE": "psn:mobile.v2.core psn:clientapp",
        "REDIRECT_URI": "com.scee.psxandroid.scecompcall://redirect",
    }
    AUTH_HEADER: ClassVar[dict[str, str]] = {
        "Authorization": "Basic MDk1MTUxNTktNzIzNy00MzcwLTliNDAtMzgwNmU2N2MwODkxOnVjUGprYTV0bnRCMktxc1A=",
    }

    def __init__(
        self,
        npsso_cookie: str,
        common_headers: RequestBuilderHeaders,
        rate_limit: Rate,
    ) -> None:
        """Represents a single authentication to PSN API.

        :param npsso_cookie: The Network Platform Single Sign-On (NPSSO) cookie, obtained after signing into PlayStation
            Network.
        :param common_headers: Common headers that will be added to all HTTP request.
        :param rate_limit: Controls pacing of HTTP requests to avoid service throttling.

        """
        self.npsso_cookie = npsso_cookie
        self.common_headers = common_headers
        self.request_builder = RequestBuilder(common_headers, rate_limit)
        self.token_response: TokenResponse | None = None
        self.cid = str(uuid.UUID(int=uuid.getnode()))

    @property
    def access_token_expiration_time(self) -> float:
        """Get the access token expiration time.

        If the :py:attr:`Authenticator.token_response` is not available or ``access_token_expires_at``, returns current
        time.

        :returns: The expiration time of the access token as a Unix timestamp.

        """
        if self.token_response is None:
            return time.time()
        return self.token_response.get("access_token_expires_at", time.time())

    @property
    def refresh_token_expiration_time(self) -> float:
        """Get the refresh token expiration time.

        If the :py:attr:`Authenticator.token_response` is not available or ``refresh_token_expires_at``, returns current
        time.

        :returns: The expiration time of the refresh token as a Unix timestamp.

        """
        if self.token_response is None:
            return time.time()
        return self.token_response.get("refresh_token_expires_at", time.time())

    @property
    def access_token_expiration_in(self) -> int:
        """Get the time until the access token expires.

        If the :py:attr:`Authenticator.token_response` is not available or ``expires_in``, returns 0.

        :returns: The number of seconds until the access token expires.

        """
        if self.token_response is None:
            return 0
        return self.token_response.get("expires_in", 0)

    @property
    def refresh_token_expiration_in(self) -> int:
        """Get the time until the refresh token expires.

        If the :py:attr:`Authenticator.token_response` is not available or ``refresh_token_expires_in``, returns 0.

        :returns: The number of seconds until the refresh token expires.

        """
        if self.token_response is None:
            return 0
        return self.token_response.get("refresh_token_expires_in", 0)

    def fetch_access_token_from_refresh(self) -> None:
        """Updates the access token using refresh token."""
        if self.token_response is None:
            raise PSNAWPAuthenticationError(
                "Attempt to obtain access_token using refresh token when refresh token is missing.",
            )

        if self.access_token_expiration_time > time.time():
            return

        header = type(self).AUTH_HEADER | {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "com.sony.snei.np.android.sso.share.oauth.versa.USER_AGENT",
        }
        data = {
            "refresh_token": self.token_response["refresh_token"],
            "grant_type": "refresh_token",
            "scope": type(self).AUTH_METADATA["SCOPE"],
            "token_format": "jwt",
        }
        response = self.request_builder.post(
            url=f"{BASE_PATH['base_uri']}{API_PATH['access_token']}",
            headers=header,
            data=data,
        )
        self.token_response = cast("TokenResponse", response.json())
        self.token_response["access_token_expires_at"] = self.token_response["expires_in"] + time.time()
        self.token_response["refresh_token_expires_at"] = self.token_response["refresh_token_expires_in"] + time.time()

    def fetch_access_token_from_authorization(self, authorization_code: str) -> None:
        """Obtain the access token using authorization code for the first time, after this the access token is obtained via refresh token.

        :param authorization_code: Code obtained using npsso code.

        """
        header = type(self).AUTH_HEADER | {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "com.sony.snei.np.android.sso.share.oauth.versa.USER_AGENT",
            "X-Psn-Correlation-Id": self.cid,
        }
        data = {
            "cid": self.cid,
            "code": authorization_code,
            "grant_type": "authorization_code",
            "redirect_uri": type(self).AUTH_METADATA["REDIRECT_URI"],
            "scope": type(self).AUTH_METADATA["SCOPE"],
            "token_format": "jwt",
        }
        response = self.request_builder.post(
            url=f"{BASE_PATH['base_uri']}{API_PATH['access_token']}",
            headers=header,
            data=data,
        )
        self.token_response = cast("TokenResponse", response.json())
        self.token_response["access_token_expires_at"] = self.token_response["expires_in"] + time.time()
        self.token_response["refresh_token_expires_at"] = self.token_response["refresh_token_expires_in"] + time.time()

    def get_authorization_code(self) -> str:
        """Obtains the authorization code for PSN authentication.

        Obtains the access code and the refresh code. Access code lasts about 1 hour. While the refresh code lasts about
        2 months. After 2 months a new npsso code is needed.

        :raises PSNAWPAuthenticationError: If authorization is not successful.

        """
        headers = {
            "Cookie": f"npsso={self.npsso_cookie}",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Requested-With": "com.scee.psxandroid",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-User": "?1",
        }
        params = {
            "access_type": "offline",
            "cid": self.cid,
            "client_id": type(self).AUTH_METADATA["CLIENT_ID"],
            "device_base_font_size": "10",
            "device_profile": "mobile",
            "elements_visibility": "no_aclink",
            "enable_scheme_error_code": "true",
            "no_captcha": "true",
            "PlatformPrivacyWs1": "minimal",
            "redirect_uri": type(self).AUTH_METADATA["REDIRECT_URI"],
            "response_type": "code",
            "scope": type(self).AUTH_METADATA["SCOPE"],
            "service_entity": "urn:service-entity:psn",
            "service_logo": "ps",
            "smcid": "psapp:signin",
            "support_scheme": "sneiprls",
            "turnOnTrustedBrowser": "true",
            "ui": "pr",
        }
        response = self.request_builder.get(
            url=f"{BASE_PATH['base_uri']}{API_PATH['oauth_code']}",
            headers=headers,
            params=params,
            allow_redirects=False,
        )

        location_url = response.headers["location"]
        parsed_url = urlparse(location_url)
        parsed_query = parse_qs(parsed_url.query)
        if "error" in parsed_query:
            if "4165" in parsed_query["error_code"]:
                raise PSNAWPAuthenticationError(
                    "Your npsso code has expired or is incorrect. Please generate a new code!",
                )
            raise PSNAWPAuthenticationError(
                "Something went wrong while authenticating",
            )

        return parsed_query["code"][0]

    @pre_request_processing
    def get(self, **kwargs: Unpack[RequestOptions]) -> Response:
        """Make a GET request with automatic Bearer token authorization.

        This method simplifies making GET requests by automatically adding the necessary Authorization header with a
        Bearer token. You can pass any additional arguments or keyword arguments, which will be forwarded to the
        underlying request builder's ``get`` method.

        :param kwargs: Additional arguments to be forwarded to the ``get`` method of the request builder.

        :returns: The response from the GET request.

        :raises PSNAWPAuthenticationError: If the :py:attr:`Authenticator.token_response` is ``None``, indicating that
            an attempt to make an HTTP request was made without an access token.
        :raises PSNAWPBadRequestError: If the HTTP response status code is 400.
        :raises PSNAWPUnauthorizedError: If the HTTP response status code is 401.
        :raises PSNAWPForbiddenError: If the HTTP response status code is 403.
        :raises PSNAWPNotFoundError: If the HTTP response status code is 404.
        :raises PSNAWPNotAllowedError: If the HTTP response status code is 405.
        :raises PSNAWPTooManyRequestsError: If the HTTP response status code is 429.
        :raises PSNAWPClientError: If the HTTP response status code is in the 4xx range (excluding those listed above).
        :raises PSNAWPServerError: If the HTTP response status code is 500 or above.

        .. note::

            The :py:func:`~psnawp_api.core.authenticator.pre_request_processing` decorator ensures that
            :py:attr:`Authenticator.token_response` is usually set correctly. The check for ``self.token_response is
            None`` is a safeguard in case of unexpected issues.

        """
        if self.token_response is None:
            raise PSNAWPAuthenticationError(
                "Attempt to make HTTP Request without access_token.",
            )

        if "headers" not in kwargs:
            kwargs["headers"] = {}
        kwargs["headers"]["Authorization"] = f"Bearer {self.token_response['access_token']}"

        return self.request_builder.get(**kwargs)

    @pre_request_processing
    def post(self, **kwargs: Unpack[RequestOptions]) -> Response:
        """Make a POST request with automatic Bearer token authorization.

        This method simplifies making POST requests by automatically adding the necessary Authorization header with a
        Bearer token. You can pass any additional arguments or keyword arguments, which will be forwarded to the
        underlying request builder's ``post`` method.

        :param kwargs: Additional arguments to be forwarded to the ``post`` method of the request builder.

        :returns: The response from the POST request.

        :raises PSNAWPAuthenticationError: If the :py:attr:`Authenticator.token_response` is ``None``, indicating that
            an attempt to make an HTTP request was made without an access token.
        :raises PSNAWPBadRequestError: If the HTTP response status code is 400.
        :raises PSNAWPUnauthorizedError: If the HTTP response status code is 401.
        :raises PSNAWPForbiddenError: If the HTTP response status code is 403.
        :raises PSNAWPNotFoundError: If the HTTP response status code is 404.
        :raises PSNAWPNotAllowedError: If the HTTP response status code is 405.
        :raises PSNAWPTooManyRequestsError: If the HTTP response status code is 429.
        :raises PSNAWPClientError: If the HTTP response status code is in the 4xx range (excluding those listed above).
        :raises PSNAWPServerError: If the HTTP response status code is 500 or above.

        .. note::

            The :py:func:`~psnawp_api.core.authenticator.pre_request_processing` decorator ensures that
            :py:attr:`Authenticator.token_response` is usually set correctly. The check for ``self.token_response is
            None`` is a safeguard in case of unexpected issues.

        """
        if self.token_response is None:
            raise PSNAWPAuthenticationError(
                "Attempt to make HTTP Request without access_token.",
            )

        if "headers" not in kwargs:
            kwargs["headers"] = {}
        kwargs["headers"]["Authorization"] = f"Bearer {self.token_response['access_token']}"

        return self.request_builder.post(**kwargs)

    @pre_request_processing
    def patch(self, **kwargs: Unpack[RequestOptions]) -> Response:
        """Make a PATCH request with automatic Bearer token authorization.

        This method simplifies making POST requests by automatically adding the necessary Authorization header with a
        Bearer token. You can pass any additional arguments or keyword arguments, which will be forwarded to the
        underlying request builder's ``patch`` method.

        :param kwargs: Additional arguments to be forwarded to the ``patch`` method of the request builder.

        :returns: The response from the POST request.

        :raises PSNAWPAuthenticationError: If the :py:attr:`Authenticator.token_response` is ``None``, indicating that
            an attempt to make an HTTP request was made without an access token.
        :raises PSNAWPBadRequestError: If the HTTP response status code is 400.
        :raises PSNAWPUnauthorizedError: If the HTTP response status code is 401.
        :raises PSNAWPForbiddenError: If the HTTP response status code is 403.
        :raises PSNAWPNotFoundError: If the HTTP response status code is 404.
        :raises PSNAWPNotAllowedError: If the HTTP response status code is 405.
        :raises PSNAWPTooManyRequestsError: If the HTTP response status code is 429.
        :raises PSNAWPClientError: If the HTTP response status code is in the 4xx range (excluding those listed above).
        :raises PSNAWPServerError: If the HTTP response status code is 500 or above.

        .. note::

            The :py:func:`~psnawp_api.core.authenticator.pre_request_processing` decorator ensures that
            :py:attr:`Authenticator.token_response` is usually set correctly. The check for ``self.token_response is
            None`` is a safeguard in case of unexpected issues.

        """
        if self.token_response is None:
            raise PSNAWPAuthenticationError(
                "Attempt to make HTTP Request without access_token.",
            )

        if "headers" not in kwargs:
            kwargs["headers"] = {}
        kwargs["headers"]["Authorization"] = f"Bearer {self.token_response['access_token']}"

        return self.request_builder.patch(**kwargs)

    @pre_request_processing
    def delete(self, **kwargs: Unpack[RequestOptions]) -> Response:
        """Make a DELETE request with automatic Bearer token authorization.

        This method simplifies making POST requests by automatically adding the necessary Authorization header with a
        Bearer token. You can pass any additional arguments or keyword arguments, which will be forwarded to the
        underlying request builder's ``delete`` method.

        :param kwargs: Additional arguments to be forwarded to the ``delete`` method of the request builder.

        :returns: The response from the POST request.

        :raises PSNAWPAuthenticationError: If the :py:attr:`Authenticator.token_response` is ``None``, indicating that
            an attempt to make an HTTP request was made without an access token.
        :raises PSNAWPBadRequestError: If the HTTP response status code is 400.
        :raises PSNAWPUnauthorizedError: If the HTTP response status code is 401.
        :raises PSNAWPForbiddenError: If the HTTP response status code is 403.
        :raises PSNAWPNotFoundError: If the HTTP response status code is 404.
        :raises PSNAWPNotAllowedError: If the HTTP response status code is 405.
        :raises PSNAWPTooManyRequestsError: If the HTTP response status code is 429.
        :raises PSNAWPClientError: If the HTTP response status code is in the 4xx range (excluding those listed above).
        :raises PSNAWPServerError: If the HTTP response status code is 500 or above.

        .. note::

            The :py:func:`~psnawp_api.core.authenticator.pre_request_processing` decorator ensures that
            :py:attr:`Authenticator.token_response` is usually set correctly. The check for ``self.token_response is
            None`` is a safeguard in case of unexpected issues.

        """
        if self.token_response is None:
            raise PSNAWPAuthenticationError(
                "Attempt to make HTTP Request without access_token.",
            )

        if "headers" not in kwargs:
            kwargs["headers"] = {}
        kwargs["headers"]["Authorization"] = f"Bearer {self.token_response['access_token']}"

        return self.request_builder.delete(**kwargs)

    @pre_request_processing
    def put(self, **kwargs: Unpack[RequestOptions]) -> Response:
        """Make a PUT request with automatic Bearer token authorization.

        This method simplifies making PUT requests by automatically adding the necessary Authorization header with a
        Bearer token. You can pass any additional arguments or keyword arguments, which will be forwarded to the
        underlying request builder's ``put`` method.

        :param kwargs: Additional arguments to be forwarded to the ``put`` method of the request builder.

        :returns: The response from the PUT request.

        :raises PSNAWPAuthenticationError: If the :py:attr:`Authenticator.token_response` is ``None``, indicating that
            an attempt to make an HTTP request was made without an access token.
        :raises PSNAWPBadRequestError: If the HTTP response status code is 400.
        :raises PSNAWPUnauthorizedError: If the HTTP response status code is 401.
        :raises PSNAWPForbiddenError: If the HTTP response status code is 403.
        :raises PSNAWPNotFoundError: If the HTTP response status code is 404.
        :raises PSNAWPNotAllowedError: If the HTTP response status code is 405.
        :raises PSNAWPTooManyRequestsError: If the HTTP response status code is 429.
        :raises PSNAWPClientError: If the HTTP response status code is in the 4xx range (excluding those listed above).
        :raises PSNAWPServerError: If the HTTP response status code is 500 or above.

        .. note::

            The :py:func:`~psnawp_api.core.authenticator.pre_request_processing` decorator ensures that
            :py:attr:`Authenticator.token_response` is usually set correctly. The check for ``self.token_response is
            None`` is a safeguard in case of unexpected issues.

        """
        if self.token_response is None:
            raise PSNAWPAuthenticationError(
                "Attempt to make HTTP Request without access_token.",
            )

        if "headers" not in kwargs:
            kwargs["headers"] = {}
        kwargs["headers"]["Authorization"] = f"Bearer {self.token_response['access_token']}"

        return self.request_builder.put(**kwargs)
