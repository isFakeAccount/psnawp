import platform

import requests

from psnawp_api import psnawp_exceptions


# Class RequestBuilder
# Builds the http requests from arguments that are passed to it
# Saves the clutter as less repeated code is needed
class RequestBuilder:
    def __init__(self, authenticator):
        self.authenticator = authenticator
        self.country = 'US'
        self.language = 'en'
        self.default_headers = {'Accept-Language': 'en-US',
                                'User-Agent': platform.platform()}

    def get(self, **kwargs):
        access_token = self.authenticator.obtain_fresh_access_token()
        headers = {
            **self.default_headers,
            'Authorization': 'Bearer {}'.format(access_token)
        }
        if 'headers' in kwargs.keys():
            headers = {**headers, **kwargs['headers']}

        params = None
        if 'params' in kwargs.keys():
            params = kwargs['params']

        data = None
        if 'data' in kwargs.keys():
            params = kwargs['data']

        response = requests.get(url=kwargs['url'], headers=headers, params=params, data=data)
        if 500 <= response.status_code <= 599:
            raise psnawp_exceptions.PSNAWPServerError(response.reason)
        return response.json()

    def post(self, **kwargs):
        # TODO: Implement this functions when needed
        pass
