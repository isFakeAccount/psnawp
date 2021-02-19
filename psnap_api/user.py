import platform

import requests

from psnap_api import psnap


class User:
    base_uri = 'https://m.np.playstation.net/api/userProfile/v1/internal/users'

    def __init__(self, authenticator, account_id):
        self.authenticator = authenticator
        self.account_id = account_id
        self.country = 'US'
        self.language = 'en'
        self.default_headers = {'Accept-Language': 'en-US',
                                'User-Agent': platform.platform()}

    def get_presence(self, account_id=None):
        if account_id is None:
            if self.account_id is None:
                raise AttributeError('account_id is of NoneType')
            else:
                account_id = self.account_id
        """
        Gets the presences of a user

        :param account_id: account ID of user
        :return: dict availability, lastAvailableDate, and primaryPlatformInfo
        """
        access_token = self.authenticator.obtain_fresh_access_token()
        headers = {
            **self.default_headers,
            'Authorization': 'Bearer {}'.format(access_token)
        }
        param = {'type': 'primary'}
        response = requests.get(url='{}/{}/basicPresences'.format(User.base_uri, account_id), headers=headers,
                                params=param).json()
        return response['basicPresence']
