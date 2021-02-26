from psnawp_api import user


# Class Client
# This class will contain the information about the logged in user
class Client:
    base_uri = 'https://dms.api.playstation.com/api'

    def __init__(self, request_builder):
        self.request_builder = request_builder
        self.account_id = 'me'

    def get_account_id(self):
        """
        Gets the account ID of the client logged in the api

        :return: str: accountID
        """
        response = self.request_builder.get(url='{}/v1/devices/accounts/me'.format(Client.base_uri))
        return response['accountId']

    def get_account_devices(self):
        """
        Gets the devices the client is logged into

        :return: dict: accountDevices
        """
        response = self.request_builder.get(url='{}/v1/devices/accounts/me'.format(Client.base_uri))
        return response['accountDevices']

    def get_friends(self, limit=None):
        """
        Gets the friends list and return their account ids

        :param limit: The number of items from input max is 1000
        :return: List: Users list of all friends in your friends list
        """
        if limit is None:
            limit = 1000
        else:
            limit = min(1000, limit)
        params = {'limit': limit}
        base_uri = 'https://m.np.playstation.net/api/userProfile/v1/internal/users'
        response = self.request_builder.get(url='{}/me/friends'.format(base_uri), params=params)
        friends_list = []
        for account_id in response['friends']:
            friends_list.append(user.User(self.request_builder, account_id=account_id))
        return friends_list
