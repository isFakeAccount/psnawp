from __future__ import annotations

import time
import uuid
from functools import wraps
from typing import TYPE_CHECKING, Callable, Optional, TypedDict, TypeVar, cast
from urllib.parse import parse_qs, urlparse

from requests import Response
from typing_extensions import NotRequired, ParamSpec, Unpack

from psnawp_api.core.psnawp_exceptions import PSNAWPAuthenticationError
from psnawp_api.core.request_builder import RequestBuilder
from psnawp_api.utils import API_PATH, BASE_PATH

if TYPE_CHECKING:
    from psnawp_api.core.request_builder import RequestBuilderHeaders, RequestOptions

PT = ParamSpec("PT")
RT = TypeVar("RT")


def pre_request_processing(method: Callable[PT, RT]) -> Callable[PT, RT]:
    @wraps(method)
    def _impl(*method_args: PT.args, **method_kwargs: PT.kwargs) -> RT:
        authenticator_obj = cast(Authenticator, method_args[0])
        if authenticator_obj.token_response is None:
            authorization_code = authenticator_obj.get_authorization_code()
            authenticator_obj.fetch_access_token_from_authorization(authorization_code)
        else:
            authenticator_obj.fetch_access_token_from_refresh()

        method_out = method(*method_args, **method_kwargs)
        return method_out

    return _impl


class TokenResponse(TypedDict):
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
    """Provides an interface for PSN Authentication and API"""

    __CONSTANTS = {
        "CLIENT_ID": "09515159-7237-4370-9b40-3806e67c0891",
        "SCOPE": "psn:mobile.v2.core psn:clientapp",
        "REDIRECT_URI": "com.scee.psxandroid.scecompcall://redirect",
    }
    __AUTH_HEADER = {"Authorization": "Basic MDk1MTUxNTktNzIzNy00MzcwLTliNDAtMzgwNmU2N2MwODkxOnVjUGprYTV0bnRCMktxc1A="}

    def __init__(
        self,
        npsso_cookie: str,
        common_headers: RequestBuilderHeaders,
    ):
        """Represents a single authentication to PSN API.

        :param npsso_cookie: npsso cookie obtained from PSN website.
        :param common_headers: Common headers that will be added to all HTTP request.

        """
        self.npsso_token = npsso_cookie
        self.common_headers = common_headers
        self.request_builder = RequestBuilder(common_headers)
        self.token_response: Optional[TokenResponse] = None

        self.cid = str(uuid.UUID(int=uuid.getnode()))

    @property
    def access_token_expiration_time(self) -> float:
        """Get the access token expiration time.

        If the ``token_response`` is not available or ``access_token_expires_at``, returns current time.

        :returns: The expiration time of the access token as a Unix timestamp.

        """
        if self.token_response is None:
            return time.time()
        return self.token_response.get("access_token_expires_at", time.time())

    @property
    def refresh_token_expiration_time(self) -> float:
        """Get the refresh token expiration time.

        If the ``token_response`` is not available or ``refresh_token_expires_at``, returns current time.

        :returns: The expiration time of the refresh token as a Unix timestamp.

        """
        if self.token_response is None:
            return time.time()
        return self.token_response.get("refresh_token_expires_at", time.time())

    @property
    def access_token_expiration_in(self) -> int:
        """Get the time until the access token expires.

        If the ``token_response`` is not available or ``expires_in``, returns 0.

        :returns: The number of seconds until the access token expires.

        """
        if self.token_response is None:
            return 0
        return self.token_response.get("expires_in", 0)

    @property
    def refresh_token_expiration_in(self) -> int:
        """Get the time until the refresh token expires.

        If the ``token_response`` is not available or ``refresh_token_expires_in``, returns 0.

        :returns: The number of seconds until the refresh token expires.

        """
        if self.token_response is None:
            return 0
        return self.token_response.get("refresh_token_expires_in", 0)

    def fetch_access_token_from_refresh(self) -> None:
        """Updates the access token using refresh token."""

        if self.token_response is None:
            raise PSNAWPAuthenticationError("Attempt to obtain access_token using refresh token when refresh token is missing.")

        if self.access_token_expiration_time > time.time():
            return None

        header = type(self).__AUTH_HEADER | {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "com.sony.snei.np.android.sso.share.oauth.versa.USER_AGENT",
        }
        data = {
            "refresh_token": self.token_response["refresh_token"],
            "grant_type": "refresh_token",
            "scope": type(self).__CONSTANTS["SCOPE"],
            "token_format": "jwt",
        }
        response = self.request_builder.post(
            url=f"{BASE_PATH['base_uri']}{API_PATH['access_token']}",
            headers=header,
            data=data,
        )
        self.token_response = cast(TokenResponse, response.json())
        self.token_response["access_token_expires_at"] = self.token_response["expires_in"] + time.time()
        self.token_response["refresh_token_expires_at"] = self.token_response["refresh_token_expires_in"] + time.time()

    def fetch_access_token_from_authorization(self, authorization_code: str) -> None:
        """Obtain the access token using authorization code for the first time, after this the access token is obtained via refresh token.

        :param code: Code obtained using npsso code.

        """

        header = type(self).__AUTH_HEADER | {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "com.sony.snei.np.android.sso.share.oauth.versa.USER_AGENT",
            "X-Psn-Correlation-Id": self.cid,
        }
        data = {
            "cid": self.cid,
            "code": authorization_code,
            "grant_type": "authorization_code",
            "redirect_uri": type(self).__CONSTANTS["REDIRECT_URI"],
            "scope": type(self).__CONSTANTS["SCOPE"],
            "token_format": "jwt",
        }
        response = self.request_builder.post(
            url=f"{BASE_PATH['base_uri']}{API_PATH['access_token']}",
            headers=header,
            data=data,
        )
        self.token_response = cast(TokenResponse, response.json())
        self.token_response["access_token_expires_at"] = self.token_response["expires_in"] + time.time()
        self.token_response["refresh_token_expires_at"] = self.token_response["refresh_token_expires_in"] + time.time()

    def get_authorization_code(self) -> str:
        """Obtains the authorization code for PSN authentication.

        Obtains the access code and the refresh code. Access code lasts about 1 hour. While the refresh code lasts about 2 months. After 2 months a new npsso
        code is needed.

        :raises PSNAWPAuthenticationError: If authorization is not successful.

        """
        headers = {
            "Cookie": f"npsso={self.npsso_token}",
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
            "client_id": type(self).__CONSTANTS["CLIENT_ID"],
            "device_base_font_size": "10",
            "device_profile": "mobile",
            "elements_visibility": "no_aclink",
            "enable_scheme_error_code": "true",
            "no_captcha": "true",
            "PlatformPrivacyWs1": "minimal",
            "redirect_uri": type(self).__CONSTANTS["REDIRECT_URI"],
            "response_type": "code",
            "scope": type(self).__CONSTANTS["SCOPE"],
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
        if "error" in parsed_query.keys():
            if "4165" in parsed_query["error_code"]:
                raise PSNAWPAuthenticationError("Your npsso code has expired or is incorrect. Please generate a new code!")
            else:
                raise PSNAWPAuthenticationError("Something went wrong while authenticating")

        return parsed_query["code"][0]

    @pre_request_processing
    def get(self, **kwargs: Unpack[RequestOptions]) -> Response:
        """Make a GET request with automatic Bearer token authorization.

        This method simplifies making GET requests by automatically adding the necessary Authorization header with a Bearer token. You can pass any additional
        arguments or keyword arguments, which will be forwarded to the underlying request builder's ``get`` method.

        :param kwargs: Additional arguments to be forwarded to the ``get`` method of the request builder.

        :returns: The response from the GET request.

        :raises PSNAWPAuthenticationError: If the ``token_response`` is ``None``, indicating that an attempt to make an HTTP request was made without an access
            token.
        :raises PSNAWPBadRequest: If the HTTP response status code is 400.
        :raises PSNAWPUnauthorized: If the HTTP response status code is 401.
        :raises PSNAWPForbidden: If the HTTP response status code is 403.
        :raises PSNAWPNotFound: If the HTTP response status code is 404.
        :raises PSNAWPNotAllowed: If the HTTP response status code is 405.
        :raises PSNAWPTooManyRequests: If the HTTP response status code is 429.
        :raises PSNAWPClientError: If the HTTP response status code is in the 4xx range (excluding those listed above).
        :raises PSNAWPServerError: If the HTTP response status code is 500 or above.

        .. note::

            The ``pre_request_processing`` decorator ensures that ``token_response`` is usually set correctly. The check for ``self.token_response is None`` is
            a safeguard in case of unexpected issues.

        """
        if self.token_response is None:
            raise PSNAWPAuthenticationError("Attempt to make HTTP Request without access_token.")

        if "headers" not in kwargs:
            kwargs["headers"] = {}
        kwargs["headers"]["Authorization"] = f"Bearer {self.token_response['access_token']}"

        return self.request_builder.get(**kwargs)

    @pre_request_processing
    def post(self, **kwargs: Unpack[RequestOptions]) -> Response:
        """Make a POST request with automatic Bearer token authorization.

        This method simplifies making POST requests by automatically adding the necessary Authorization header with a Bearer token. You can pass any additional
        arguments or keyword arguments, which will be forwarded to the underlying request builder's ``post`` method.

        :param kwargs: Additional arguments to be forwarded to the ``post`` method of the request builder.

        :returns: The response from the POST request.

        :raises PSNAWPAuthenticationError: If the ``token_response`` is ``None``, indicating that an attempt to make an HTTP request was made without an access
            token.
        :raises PSNAWPBadRequest: If the HTTP response status code is 400.
        :raises PSNAWPUnauthorized: If the HTTP response status code is 401.
        :raises PSNAWPForbidden: If the HTTP response status code is 403.
        :raises PSNAWPNotFound: If the HTTP response status code is 404.
        :raises PSNAWPNotAllowed: If the HTTP response status code is 405.
        :raises PSNAWPTooManyRequests: If the HTTP response status code is 429.
        :raises PSNAWPClientError: If the HTTP response status code is in the 4xx range (excluding those listed above).
        :raises PSNAWPServerError: If the HTTP response status code is 500 or above.

        .. note::

            The ``pre_request_processing`` decorator ensures that ``token_response`` is usually set correctly. The check for ``self.token_response is None`` is
            a safeguard in case of unexpected issues.

        """
        if self.token_response is None:
            raise PSNAWPAuthenticationError("Attempt to make HTTP Request without access_token.")

        if "headers" not in kwargs:
            kwargs["headers"] = {}
        kwargs["headers"]["Authorization"] = f"Bearer {self.token_response['access_token']}"

        return self.request_builder.post(**kwargs)

    @pre_request_processing
    def patch(self, **kwargs: Unpack[RequestOptions]) -> Response:
        """Make a PATCH request with automatic Bearer token authorization.

        This method simplifies making POST requests by automatically adding the necessary Authorization header with a Bearer token. You can pass any additional
        arguments or keyword arguments, which will be forwarded to the underlying request builder's ``patch`` method.

        :param kwargs: Additional arguments to be forwarded to the ``patch`` method of the request builder.

        :returns: The response from the POST request.

        :raises PSNAWPAuthenticationError: If the ``token_response`` is ``None``, indicating that an attempt to make an HTTP request was made without an access
            token.
        :raises PSNAWPBadRequest: If the HTTP response status code is 400.
        :raises PSNAWPUnauthorized: If the HTTP response status code is 401.
        :raises PSNAWPForbidden: If the HTTP response status code is 403.
        :raises PSNAWPNotFound: If the HTTP response status code is 404.
        :raises PSNAWPNotAllowed: If the HTTP response status code is 405.
        :raises PSNAWPTooManyRequests: If the HTTP response status code is 429.
        :raises PSNAWPClientError: If the HTTP response status code is in the 4xx range (excluding those listed above).
        :raises PSNAWPServerError: If the HTTP response status code is 500 or above.

        .. note::

            The ``pre_request_processing`` decorator ensures that ``token_response`` is usually set correctly. The check for ``self.token_response is None`` is
            a safeguard in case of unexpected issues.

        """
        if self.token_response is None:
            raise PSNAWPAuthenticationError("Attempt to make HTTP Request without access_token.")

        if "headers" not in kwargs:
            kwargs["headers"] = {}
        kwargs["headers"]["Authorization"] = f"Bearer {self.token_response['access_token']}"

        return self.request_builder.patch(**kwargs)

    @pre_request_processing
    def delete(self, **kwargs: Unpack[RequestOptions]) -> Response:
        """Make a DELETE request with automatic Bearer token authorization.

        This method simplifies making POST requests by automatically adding the necessary Authorization header with a Bearer token. You can pass any additional
        arguments or keyword arguments, which will be forwarded to the underlying request builder's ``delete`` method.

        :param kwargs: Additional arguments to be forwarded to the ``delete`` method of the request builder.

        :returns: The response from the POST request.

        :raises PSNAWPAuthenticationError: If the ``token_response`` is ``None``, indicating that an attempt to make an HTTP request was made without an access
            token.
        :raises PSNAWPBadRequest: If the HTTP response status code is 400.
        :raises PSNAWPUnauthorized: If the HTTP response status code is 401.
        :raises PSNAWPForbidden: If the HTTP response status code is 403.
        :raises PSNAWPNotFound: If the HTTP response status code is 404.
        :raises PSNAWPNotAllowed: If the HTTP response status code is 405.
        :raises PSNAWPTooManyRequests: If the HTTP response status code is 429.
        :raises PSNAWPClientError: If the HTTP response status code is in the 4xx range (excluding those listed above).
        :raises PSNAWPServerError: If the HTTP response status code is 500 or above.

        .. note::

            The ``pre_request_processing`` decorator ensures that ``token_response`` is usually set correctly. The check for ``self.token_response is None`` is
            a safeguard in case of unexpected issues.

        """
        if self.token_response is None:
            raise PSNAWPAuthenticationError("Attempt to make HTTP Request without access_token.")

        if "headers" not in kwargs:
            kwargs["headers"] = {}
        kwargs["headers"]["Authorization"] = f"Bearer {self.token_response['access_token']}"

        return self.request_builder.delete(**kwargs)

    @pre_request_processing
    def put(self, **kwargs: Unpack[RequestOptions]) -> Response:
        """Make a PUT request with automatic Bearer token authorization.

        This method simplifies making PUT requests by automatically adding the necessary Authorization header with a Bearer token. You can pass any additional
        arguments or keyword arguments, which will be forwarded to the underlying request builder's ``put`` method.

        :param kwargs: Additional arguments to be forwarded to the ``put`` method of the request builder.

        :returns: The response from the PUT request.

        :raises PSNAWPAuthenticationError: If the ``token_response`` is ``None``, indicating that an attempt to make an HTTP request was made without an access
            token.
        :raises PSNAWPBadRequest: If the HTTP response status code is 400.
        :raises PSNAWPUnauthorized: If the HTTP response status code is 401.
        :raises PSNAWPForbidden: If the HTTP response status code is 403.
        :raises PSNAWPNotFound: If the HTTP response status code is 404.
        :raises PSNAWPNotAllowed: If the HTTP response status code is 405.
        :raises PSNAWPTooManyRequests: If the HTTP response status code is 429.
        :raises PSNAWPClientError: If the HTTP response status code is in the 4xx range (excluding those listed above).
        :raises PSNAWPServerError: If the HTTP response status code is 500 or above.

        .. note::

            The ``pre_request_processing`` decorator ensures that ``token_response`` is usually set correctly. The check for ``self.token_response is None`` is
            a safeguard in case of unexpected issues.

        """
        if self.token_response is None:
            raise PSNAWPAuthenticationError("Attempt to make HTTP Request without access_token.")

        if "headers" not in kwargs:
            kwargs["headers"] = {}
        kwargs["headers"]["Authorization"] = f"Bearer {self.token_response['access_token']}"

        return self.request_builder.put(**kwargs)
