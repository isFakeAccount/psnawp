import platform

import requests


class Client:
    base_uri = 'https://dms.api.playstation.com/api'

    def __init__(self, authenticator):
        self.authenticator = authenticator
        self.account_id = 'me'
        self.country = 'US'
        self.language = 'en'
        self.default_headers = {'Accept-Language': 'en-US',
                                'User-Agent': platform.platform()}

    def get_account_id(self):
        access_token = self.authenticator.obtain_fresh_access_token()
        headers = {
            **self.default_headers,
            'Authorization': 'Bearer {}'.format(access_token),
        }
        response = requests.get(url='{}/v1/devices/accounts/me'.format(Client.base_uri), headers=headers).json()
        return response['accountId']

    def get_account_devices(self):
        access_token = self.authenticator.obtain_fresh_access_token()
        headers = {
            **self.default_headers,
            'Authorization': 'Bearer {}'.format(access_token),
        }
        response = requests.get(url='{}/v1/devices/accounts/me'.format(Client.base_uri), headers=headers).json()
        return response['accountDevices']
