import json

import requests

from psnawp_api.core.authenticator import Authenticator
from psnawp_api.core.psnawp_exceptions import (
    PSNAWPNotFound,
    PSNAWPForbidden,
    PSNAWPBadRequest,
    PSNAWPNotAllowed,
    PSNAWPServerError,
    PSNAWPUnauthorized,
)


def response_checker(response):
    """Checks the HTTP(S) response and re-raises them as PSNAWP Exceptions

    :param response: :class:`Response <Response>` object
    :type response: requests.Response

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
    elif response.status_code >= 500:
        raise PSNAWPServerError(response.text)
    else:
        response.raise_for_status()


class RequestBuilder:
    """Handles all the HTTP Requests and provides a gateway to interacting with PSN API."""

    def __init__(self, authenticator: Authenticator):
        """Initialized Request Handler and saves the instance of authenticator for future use.

        :param authenticator: The instance of :class: `Authenticator`. Represents single
            authentication to PSN API.

        """
        self.authenticator = authenticator
        self.default_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
            "Content-Type": "application/json",
            "Accept-Language": "en-US",
            "Country": "US",
        }

    def get(self, **kwargs) -> requests.Response:
        """Handles the GET requests and returns the requests.Response object.

        :param kwargs: The query parameters to add to the request.

        :returns: The Request Response Object.
        :rtype: requests.Response

        """
        access_token = self.authenticator.obtain_fresh_access_token()
        headers = {**self.default_headers, "Authorization": f"Bearer {access_token}"}
        if "headers" in kwargs.keys():
            headers = {**headers, **kwargs["headers"]}

        params = kwargs.get("params")
        data = kwargs.get("data")

        response = requests.get(
            url=kwargs["url"], headers=headers, params=params, data=data
        )
        response_checker(response)
        return response

    def patch(self, **kwargs) -> requests.Response:
        """Handles the POST requests and returns the requests.Response object.

        :param kwargs: The query parameters to add to the request.

        :returns: The Request Response Object.
        :rtype: requests.Response

        """
        access_token = self.authenticator.obtain_fresh_access_token()
        headers = {**self.default_headers, "Authorization": f"Bearer {access_token}"}
        if "headers" in kwargs.keys():
            headers = {**headers, **kwargs["headers"]}

        params = kwargs.get("params")
        data = kwargs.get("data")

        response = requests.patch(
            url=kwargs["url"], headers=headers, data=data, params=params
        )

        response_checker(response)
        return response

    def post(self, **kwargs) -> requests.Response:
        """Handles the POST requests and returns the requests.Response object.

        :param kwargs: The query parameters to add to the request.

        :returns: The Request Response Object.
        :rtype: requests.Response

        """
        access_token = self.authenticator.obtain_fresh_access_token()
        headers = {**self.default_headers, "Authorization": f"Bearer {access_token}"}
        if "headers" in kwargs.keys():
            headers = {**headers, **kwargs["headers"]}

        params = kwargs.get("params")
        data = kwargs.get("data")

        response = requests.post(
            url=kwargs["url"], headers=headers, data=data, params=params
        )

        response_checker(response)
        return response

    def multipart_post(self, **kwargs) -> requests.Response:
        """Handles the Multipart POST requests and returns the requests.Response object.

        :param kwargs: The query parameters to add to the request.

        :returns: The Request Response Object.
        :rtype: requests.Response

        """
        access_token = self.authenticator.obtain_fresh_access_token()
        headers = {**self.default_headers, "Authorization": f"Bearer {access_token}"}
        if "headers" in kwargs.keys():
            headers = {**headers, **kwargs["headers"]}

        data = kwargs.get("data")

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
        response_checker(response)
        return response

    def delete(self, **kwargs) -> requests.Response:
        """Handles the DELETE requests and returns the requests.Response object.

        :param kwargs: The query parameters to add to the request.

        :returns: The Request Response Object.
        :rtype: requests.Response

        """
        access_token = self.authenticator.obtain_fresh_access_token()
        headers = {**self.default_headers, "Authorization": f"Bearer {access_token}"}
        if "headers" in kwargs.keys():
            headers = {**headers, **kwargs["headers"]}

        params = kwargs.get("params")
        data = kwargs.get("data")

        response = requests.delete(
            url=kwargs["url"], headers=headers, params=params, data=data
        )
        response_checker(response)
        return response
