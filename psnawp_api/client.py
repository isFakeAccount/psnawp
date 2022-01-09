from psnawp_api import user


# Class Client
# This class will contain the information about the logged in user
class Client:
    base_uri = 'https://dms.api.playstation.com/api'

    def __init__(self, request_builder):
        self.request_builder = request_builder
        self.online_id = self.get_online_id()
        self.account_id = self.get_account_id()

    def get_online_id(self):
        """
        Gets the online ID of the client logged in the api

        :returns: str: onlineID
        """
        response = self.request_builder.get(url='{}/{}/profiles'.format(user.User.base_uri, self.get_account_id()))
        return response['onlineId']

    def get_account_id(self):
        """
        Gets the account ID of the client logged in the api

        :returns: str: accountID
        """
        response = self.request_builder.get(url='{}/v1/devices/accounts/me'.format(Client.base_uri))
        return response['accountId']

    def get_account_devices(self):
        """
        Gets the devices the client is logged into

        :returns: dict: accountDevices
        """
        response = self.request_builder.get(url='{}/v1/devices/accounts/me'.format(Client.base_uri))
        return response['accountDevices']

    def get_friends(self, limit=1000):
        """
        Gets the friends list and return their account ids

        :param limit: The number of items from input max is 1000
        :type limit: int
        :returns: List: Account ID of all friends in your friends list
        """
        limit = min(1000, limit)

        params = {'limit': limit}
        base_uri = 'https://m.np.playstation.net/api/userProfile/v1/internal/users'
        response = self.request_builder.get(url='{}/me/friends'.format(base_uri), params=params)
        return response['friends']
    
    def get_gamelist(self, limit=1000, offset=0):	
        """ 
        Get the game list and return their progress and trophies

        :param limit: The number of items from input max is 1000
        :type limit: int
        :param offset: Index where start the listing
        :type offset: int
        :returns: List: Game list and respective progress
        """

        limit = min(1000,limit)
        offset = min(1000,offset)
        response = self.request_builder.get(url='https://m.np.playstation.net/api/trophy/v1/users/me/trophyTitles?limit={}&offset={}'.format(limit, offset))

        return response

    def blocked_list(self):
        """
        Gets the blocked list and return their account ids

        :returns: List: Account ID of all blocked users on your block list
        """
        base_uri = 'https://m.np.playstation.net/api/userProfile/v1/internal/users'
        response = self.request_builder.get(url='{}/me/blocks'.format(base_uri))
        return response['blockList']

    def __repr__(self):
        return "<User online_id:{} account_id:{}>".format('me', self.account_id)

    def __str__(self):
        return "Online ID: {} Account ID: {}".format('me', self.account_id)
