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
        """
        Gets the account ID of the client logged in the api

        :return: str: accountID
        """
        access_token = self.authenticator.obtain_fresh_access_token()
        headers = {
            **self.default_headers,
            'Authorization': 'Bearer {}'.format(access_token)
        }
        response = requests.get(url='{}/v1/devices/accounts/me'.format(Client.base_uri), headers=headers).json()
        return response['accountId']

    def get_account_devices(self):
        """
        Gets the devices the client is logged into

        :return: dict: accountDevices
        """
        access_token = self.authenticator.obtain_fresh_access_token()
        headers = {
            **self.default_headers,
            'Authorization': 'Bearer {}'.format(access_token),
        }
        response = requests.get(url='{}/v1/devices/accounts/me'.format(Client.base_uri), headers=headers).json()
        return response['accountDevices']

    def get_friends(self, limit=None):
        """
        Gets the friends list and return their account ids

        :param limit: The number of items from input max is 1000
        :return: dict: account ids of all friends in your friends list
        """
        if limit is None:
            limit = 1000
        else:
            limit = min(1000, limit)
        access_token = self.authenticator.obtain_fresh_access_token()
        headers = {
            **self.default_headers,
            'Authorization': 'Bearer {}'.format(access_token)
        }
        param = {'limit': limit}
        base_uri = 'https://m.np.playstation.net/api/userProfile/v1/internal/users'
        response = requests.get(url='{}/me/friends'.format(base_uri), headers=headers, params=param)
        return response.json()
