import json
import platform

import requests


# Class RequestBuilder
# Builds the http requests from arguments that are passed to it
# Saves the clutter as less repeated code is needed
# For internal use only do not call directly
class RequestBuilder:
    def __init__(self, authenticator):
        self.authenticator = authenticator
        self.country = 'US'
        self.language = 'en'
        self.default_headers = {'User-Agent': platform.platform()}

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
            data = kwargs['data']

        response = requests.get(url=kwargs['url'], headers=headers, params=params, data=data)
        response.raise_for_status()
        return response.json()

    def multipart_post(self, **kwargs):
        access_token = self.authenticator.obtain_fresh_access_token()
        headers = {
            **self.default_headers,
            'Authorization': 'Bearer {}'.format(access_token)
        }
        if 'headers' in kwargs.keys():
            headers = {**headers, **kwargs['headers']}

        name = None
        if 'name' in kwargs.keys():
            name = kwargs['name']

        data = None
        if 'data' in kwargs.keys():
            data = kwargs['data']

        response = requests.post(url=kwargs['url'], headers=headers, files={name: (None, json.dumps(data),
                                                                                   'application/json; charset=utf-8')})
        response.raise_for_status()
        return response.json()

    def delete(self, **kwargs):
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
            data = kwargs['data']

        response = requests.delete(url=kwargs['url'], headers=headers, params=params, data=data)
        response.raise_for_status()
        return response.json()
