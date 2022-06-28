import json

import requests

from psnawp_api.authenticator import Authenticator


class RequestBuilder:
    """Handles all the HTTP Requests and provides a gateway to interacting with PSN API."""

    def __init__(self, authenticator: Authenticator):
        """Initialized Request Handler and saves the instance of authenticator for future use.

        :param authenticator: The instance of :class: `Authenticator`. Represents single
            authentication to PSN API.

        """
        self.authenticator = authenticator
        self.country = "US"
        self.language = "en"
        self.default_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
        }

    def get(self, **kwargs):
        """Handles the GET requests and returns the parsed objects.

        :param kwargs: The query parameters to add to the request.

        :returns: Formatted Objects from HTTP Response.

        """
        access_token = self.authenticator.obtain_fresh_access_token()
        headers = {**self.default_headers, "Authorization": f"Bearer {access_token}"}
        if "headers" in kwargs.keys():
            headers = {**headers, **kwargs["headers"]}

        params = None
        if "params" in kwargs.keys():
            params = kwargs["params"]

        data = None
        if "data" in kwargs.keys():
            data = kwargs["data"]

        response = requests.get(
            url=kwargs["url"], headers=headers, params=params, data=data
        )
        response.raise_for_status()
        return response.json()

    def multipart_post(self, **kwargs):
        """Handles the Multipart POST requests and returns the parsed objects.

        :param kwargs: The query parameters to add to the request.

        :returns: Formatted Objects from HTTP Response.

        """
        access_token = self.authenticator.obtain_fresh_access_token()
        headers = {**self.default_headers, "Authorization": f"Bearer {access_token}"}
        if "headers" in kwargs.keys():
            headers = {**headers, **kwargs["headers"]}

        data = None
        if "data" in kwargs.keys():
            data = kwargs["data"]

        response = requests.post(
            url=kwargs["url"],
            headers=headers,
            files={
                kwargs["name"]: (
                    None,
                    json.dumps(data),
                    "application/json; charset=utf-8",
                )
            },
        )
        response.raise_for_status()
        return response.json()

    def delete(self, **kwargs):
        """Handles the DELETE requests and returns the parsed objects.

        :param kwargs: The query parameters to add to the request.

        :returns: Formatted Objects from HTTP Response.

        """
        access_token = self.authenticator.obtain_fresh_access_token()
        headers = {**self.default_headers, "Authorization": f"Bearer {access_token}"}
        if "headers" in kwargs.keys():
            headers = {**headers, **kwargs["headers"]}

        params = None
        if "params" in kwargs.keys():
            params = kwargs["params"]

        data = None
        if "data" in kwargs.keys():
            data = kwargs["data"]

        response = requests.delete(
            url=kwargs["url"], headers=headers, params=params, data=data
        )
        response.raise_for_status()
        return response.json()
