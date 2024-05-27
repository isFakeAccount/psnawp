from __future__ import annotations

import time
from datetime import timedelta
from functools import wraps
from logging import getLogger
from typing import Any, Callable, TypeVar, cast
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
        method_out = method(*method_args, **method_kwargs)

        authenticator_obj = cast(Authenticator, method_args[0])
        if authenticator_obj.refresh_token_expiration_in < authenticator_obj.refresh_token_warn_time.total_seconds():
            authenticator_obj.refresh_token_warn_callback(authenticator_obj.refresh_token_warn_time)
        return method_out

    return _impl


authenticator_logger = getLogger("psnawp")


class Authenticator:
    """Provides an interface for PSN Authentication and API"""

    __PARAMS = {
        "CLIENT_ID": "09515159-7237-4370-9b40-3806e67c0891",
        "SCOPE": "psn:mobile.v2.core psn:clientapp",
        "REDIRECT_URI": "com.scee.psxandroid.scecompcall://redirect",
    }
    __AUTH_HEADER = {"Authorization": "Basic MDk1MTUxNTktNzIzNy00MzcwLTliNDAtMzgwNmU2N2MwODkxOnVjUGprYTV0bnRCMktxc1A="}

    def __init__(
        self,
        npsso_cookie: str,
        refresh_token_warn_time: timedelta,
        refresh_token_warn_callback: Callable[[timedelta], None],
        **default_headers: Unpack[RequestBuilderHeaders],
    ):
        """Represents a single authentication to PSN API.

        :param npsso_cookie: npsso cookie obtained from PSN website.

        :raises: ``PSNAWPAuthenticationError`` If npsso code is expired or is incorrect.

        """
        self.npsso_token = npsso_cookie
        self.default_headers = default_headers
        self.request_builder = RequestBuilder(**default_headers)
        self.auth_properties: dict[str, Any] = {}

        self.refresh_token_warn_time = refresh_token_warn_time
        self.refresh_token_warn_callback = refresh_token_warn_callback

    @property
    def access_token_expiration_time(self) -> float:
        return self.auth_properties.get("access_token_expires_at", time.time())

    @property
    def refresh_token_expiration_time(self) -> float:
        return self.auth_properties.get("refresh_token_expires_at", time.time())

    @property
    def access_token_expiration_in(self) -> float:
        return self.auth_properties.get("expire_in", 0)

    @property
    def refresh_token_expiration_in(self) -> float:
        return self.auth_properties.get("refresh_token_expires_in", 0)

    def fetch_access_token_from_refresh(self, refresh_token: str) -> None:
        """Obtain the access token using refresh token."""

        data = {
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
            "scope": type(self).__PARAMS["SCOPE"],
            "token_format": "jwt",
        }
        response = self.request_builder.post(
            url=f"{BASE_PATH['base_uri']}{API_PATH['access_token']}",
            headers=type(self).__AUTH_HEADER,
            data=data,
        )
        self.auth_properties = response.json()
        self.auth_properties["access_token_expires_at"] = self.auth_properties["expires_in"] + time.time()
        self.auth_properties["refresh_token_expires_at"] = self.auth_properties["refresh_token_expires_in"] + time.time()

    def fetch_access_token_from_authorization(self, authorization_code: str) -> None:
        """Obtain the access token using authorization code for the first time, after this the access token is obtained via refresh token.

        :param code: Code obtained using npsso code.

        """

        data = {
            "code": authorization_code,
            "grant_type": "authorization_code",
            "redirect_uri": type(self).__PARAMS["REDIRECT_URI"],
            "scope": type(self).__PARAMS["SCOPE"],
            "token_format": "jwt",
        }

        response = self.request_builder.post(
            url=f"{BASE_PATH['base_uri']}{API_PATH['access_token']}",
            headers=type(self).__AUTH_HEADER,
            data=data,
        )
        self.auth_properties = response.json()
        self.auth_properties["access_token_expires_at"] = self.auth_properties["expires_in"] + time.time()
        self.auth_properties["refresh_token_expires_at"] = self.auth_properties["refresh_token_expires_in"] + time.time()

    def get_authorization_code(self) -> None:
        """Obtains the authorization code for PSN authentication.

        Obtains the access code and the refresh code. Access code lasts about 1 hour. While the refresh code lasts about 2 months. After 2 months a new npsso
        code is needed.

        :raises: ``PSNAWPAuthenticationError`` If authorization is not successful.

        """
        headers = {"Cookie": f"npsso={self.npsso_token}"}
        params = {
            "access_type": "offline",
            "client_id": type(self).__PARAMS["CLIENT_ID"],
            "scope": type(self).__PARAMS["SCOPE"],
            "redirect_uri": type(self).__PARAMS["REDIRECT_URI"],
            "response_type": "code",
        }
        response = self.request_builder.get(
            url=f"{BASE_PATH['base_uri']}{API_PATH['oauth_code']}",
            headers=headers,
            params=params,
            allow_redirects=False,
        )
        response.raise_for_status()
        location_url = response.headers["location"]
        parsed_url = urlparse(location_url)
        parsed_query = parse_qs(parsed_url.query)
        if "error" in parsed_query.keys():
            if "4165" in parsed_query["error_code"]:
                raise PSNAWPAuthenticationError("Your npsso code has expired or is incorrect. Please generate a new code!")
            else:
                raise PSNAWPAuthenticationError("Something went wrong while authenticating")

        self.fetch_access_token_from_authorization(parsed_query["code"][0])

    @pre_request_processing
    def get(self, **kwargs: Unpack[RequestOptions]) -> Response:
        return self.request_builder.get(**kwargs)

    @pre_request_processing
    def post(self, **kwargs: Unpack[RequestOptions]) -> Response:
        return self.request_builder.post(**kwargs)
