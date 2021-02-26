from psnawp_api import psnawp_exceptions


# Class Search
# Used to search for users from their PSN ID and get their Online ID
class Search:
    def __init__(self, request_builder):
        self.request_builder = request_builder

    def online_id_to_account_id(self, online_id=""):
        """
        Converts user online ID and returns their account id

        :param online_id: online id of user you want to search
        :return: dict: PSN ID and Account ID of the user in search query
        :raises PSNAWPIllegalArgumentError: If the search query is empty
        :raises PSNAWPUserNotFound: If the user is invalid
        """
        # If user tries to do empty search
        if len(online_id) <= 0:
            raise psnawp_exceptions.PSNAWPIllegalArgumentError('online_id must contain a value.')
        base_uri = "https://us-prof.np.community.playstation.net/userProfile/v1/users"
        param = {'fields': 'accountId,onlineId,currentOnlineId'}
        response = self.request_builder.get(url="{}/{}/profile2".format(base_uri, online_id), params=param)
        if 'error' in response.keys():
            raise psnawp_exceptions.PSNAWPUserNotFound("Invalid user {}".format(online_id))
        return response
