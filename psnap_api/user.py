from psnap_api import search


# Class User
# This class will contain the information about the PSN ID you passed in when creating object
class User:
    base_uri = 'https://m.np.playstation.net/api/userProfile/v1/internal/users'

    def __init__(self, request_builder, online_id):
        self.request_builder = request_builder
        self.online_id = online_id
        search_obj = search.Search(request_builder)
        profile = search_obj.search_user(online_id)
        self.account_id = profile['profile']['accountId']

    def profile(self):
        """
        Gets the profile of the user

        :return: Information about profile such as about me, avatars, languages etc...
        """
        response = self.request_builder.get(url='{}/{}/profiles'.format(User.base_uri, self.account_id))
        return response

    def get_presence(self):
        """
        Gets the presences of a user

        :return: dict availability, lastAvailableDate, and primaryPlatformInfo
        """
        params = {'type': 'primary'}
        response = self.request_builder.get(url='{}/{}/basicPresences'.format(User.base_uri, self.account_id),
                                            params=params)
        return response['basicPresence']

    def friendship(self):
        """
        Gets the friendship status and stats of the user

        :return: dict: friendship stats
        """
        response = self.request_builder.get(url='{}/me/friends/{}/summary'.format(User.base_uri, self.account_id))
        return response

    def is_available_to_play(self):
        """
        TODO I am not sure what this endpoint returns I'll update the documentation later
        :return:
        """
        response = self.request_builder.get(url='{}/me/friends/subscribing/availableToPlay'.format(User.base_uri))
        return response

    def is_blocked(self):
        """
        Checks if the user is blocked by you

        :return: boolean: True if the user is blocked otherwise False
        """
        response = self.request_builder.get(url='{}/me/blocks'.format(User.base_uri))
        if self.account_id in response['blockList']:
            return True
        else:
            return False
