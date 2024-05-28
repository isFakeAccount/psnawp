from __future__ import annotations

import time
import uuid
from functools import wraps
from logging import getLogger
from typing import Callable, NotRequired, Optional, TypedDict, TypeVar, cast
from urllib.parse import parse_qs, urlparse

from requests import Response
from typing_extensions import ParamSpec, Unpack

from psnawp_api.core.psnawp_exceptions import PSNAWPAuthenticationError
from psnawp_api.core.request_builder import RequestBuilder, RequestBuilderHeaders, RequestOptions
from psnawp_api.utils import API_PATH, BASE_PATH

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


authenticator_logger = getLogger("psnawp")


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

        :raises: ``PSNAWPAuthenticationError`` If npsso code is expired or is incorrect.

        """
        self.npsso_token = npsso_cookie
        self.common_headers = common_headers
        self.request_builder = RequestBuilder(common_headers)
        self.token_response: Optional[TokenResponse] = None

        self.cid = str(uuid.uuid4())

    @property
    def access_token_expiration_time(self) -> float:
        if self.token_response is None:
            return time.time()
        return self.token_response.get("access_token_expires_at", time.time())

    @property
    def refresh_token_expiration_time(self) -> float:
        if self.token_response is None:
            return time.time()
        return self.token_response.get("refresh_token_expires_at", time.time())

    @property
    def access_token_expiration_in(self) -> int:
        if self.token_response is None:
            return 0
        return self.token_response.get("expires_in", 0)

    @property
    def refresh_token_expiration_in(self) -> int:
        if self.token_response is None:
            return 0
        return self.token_response.get("refresh_token_expires_in", 0)

    def fetch_access_token_from_refresh(self) -> None:
        """Obtain the access token using refresh token."""

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

        :raises: ``PSNAWPAuthenticationError`` If authorization is not successful.

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
        if self.token_response is None:
            raise PSNAWPAuthenticationError("Attempt to make HTTP Request without access_token.")

        if "headers" in kwargs:
            kwargs["headers"]["Authorization"] = f"Bearer {self.token_response['access_token']}"
        return self.request_builder.get(**kwargs)

    @pre_request_processing
    def post(self, **kwargs: Unpack[RequestOptions]) -> Response:
        if self.token_response is None:
            raise PSNAWPAuthenticationError("Attempt to make HTTP Request without access_token.")

        if "headers" in kwargs:
            kwargs["headers"]["Authorization"] = f"Bearer {self.token_response['access_token']}"
        return self.request_builder.post(**kwargs)
