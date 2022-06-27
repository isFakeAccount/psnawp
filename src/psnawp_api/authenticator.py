from typing import Any
from urllib.parse import urlparse, parse_qs

import requests

from psnawp_api import psnawp_exceptions
from psnawp_api.endpoints import BASE_PATH, API_PATH


class Authenticator:
    """Provides an interface for PSN Authentication."""

    PARAMS = {
        "CLIENT_ID": "ac8d161a-d966-4728-b0ea-ffec22f69edc",
        "SCOPE": "psn:clientapp psn:mobile.v1",
        "REDIRECT_URI": "com.playstation.PlayStationApp://redirect",
    }
    AUTH_HEADER = {
        "Authorization": "Basic YWM4ZDE2MWEtZDk2Ni00NzI4LWIwZWEtZmZlYzIyZjY5ZWRjOkRFaXhFcVhYQ2RYZHdqMHY="
    }

    def __init__(self, npsso_cookie: str):
        """Represents a single authentication to PSN API.

        :param npsso_cookie: npsso cookie obtained from PSN website.

        :raises: If npsso code len is not 64 characters.

        """
        if len(npsso_cookie) != 64:
            raise psnawp_exceptions.PSNAWPIllegalArgumentError(
                "Your npsso code is incorrect!"
            )
        self.npsso_token = npsso_cookie
        self.auth_properties: dict[str, Any] = {}
        self.authenticate()

    def obtain_fresh_access_token(self) -> Any:
        """Gets a new access token from refresh token.

        :returns: access token

        """
        data = {
            "refresh_token": self.auth_properties["refresh_token"],
            "grant_type": "refresh_token",
            "scope": Authenticator.PARAMS["SCOPE"],
            "token_format": "jwt",
        }
        response = requests.post(
            f"{BASE_PATH['base_uri']}{API_PATH['access_token']}",
            headers=Authenticator.AUTH_HEADER,
            data=data,
        )
        self.auth_properties = response.json()
        if self.auth_properties["refresh_token_expires_in"] <= 60 * 60 * 24 * 3:
            print(
                "Warning: Your refresh token is going to expire in less than 3 days. Please renew you npsso token!"
            )
        return self.auth_properties["access_token"]

    def oauth_token(self, code: str) -> None:
        """Obtain the access token using oauth code for the first time, after this the access token is obtained via refresh token.

        :param code: Code obtained using npsso code.

        """

        data = {
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": Authenticator.PARAMS["REDIRECT_URI"],
            "scope": Authenticator.PARAMS["SCOPE"],
            "token_format": "jwt",
        }

        response = requests.post(
            f"{BASE_PATH['base_uri']}{API_PATH['access_token']}",
            headers=Authenticator.AUTH_HEADER,
            data=data,
        )
        self.auth_properties = response.json()
        if self.auth_properties["refresh_token_expires_in"] <= 60 * 60 * 24 * 3:
            print(
                "Warning: Your refresh token is going to expire in less than 3 days. Please renew you npsso token!"
            )

    def authenticate(self) -> None:
        """Authenticate using the npsso code provided in the constructor.

        Obtains the access code and the refresh code. Access code lasts about 1 hour.
        While the refresh code lasts about 2 months. After 2 months a new npsso code is
        needed.

        :raises: If authentication is not successful.

        """
        cookies = {"Cookie": f"npsso={self.npsso_token}"}
        params = {
            "access_type": "offline",
            "client_id": Authenticator.PARAMS["CLIENT_ID"],
            "scope": Authenticator.PARAMS["SCOPE"],
            "redirect_uri": Authenticator.PARAMS["REDIRECT_URI"],
            "response_type": "code",
        }
        response = requests.get(
            f"{BASE_PATH['base_uri']}{API_PATH['oauth_code']}",
            headers=cookies,
            params=params,
            allow_redirects=False,
        )
        response.raise_for_status()
        location_url = response.headers["location"]
        parsed_url = urlparse(location_url)
        parsed_query = parse_qs(parsed_url.query)
        if "error" in parsed_query.keys():
            if "4165" in parsed_query["error_code"]:
                raise psnawp_exceptions.PSNAWPAuthenticationError(
                    "Your npsso code has expired or is incorrect. Please generate a new code!"
                )
            else:
                raise psnawp_exceptions.PSNAWPAuthenticationError(
                    "Something went wrong while authenticating"
                )
        self.oauth_token(parsed_query["code"][0])
