from psnap_api import psnap_exceptions


# Class Search
# Used to search for users from their PSN ID and get their Online ID
class Search:
    def __init__(self, request_builder):
        self.request_builder = request_builder

    def search_user(self, search_query=""):
        """
        Searches a user online ID and returns their account id

        :param search_query: online id of user you want to search
        :return: dict: PSN ID and Account ID of the user in search query
        :raises PSNAPIllegalArgumentError: If the search query is empty
        :raises PSNAPInvalidRequestError: If the user is invalid
        """
        # If user tries to do empty search
        if len(search_query) <= 0:
            raise psnap_exceptions.PSNAPIllegalArgumentError('Search_query must contain a value.')
        base_uri = "https://us-prof.np.community.playstation.net/userProfile/v1/users"
        param = {'fields': 'accountId,onlineId'}
        response = self.request_builder.get(url="{}/{}/profile2".format(base_uri, search_query), params=param)
        if 'error' in response.keys():
            raise psnap_exceptions.PSNAPInvalidRequestError("Invalid user {}".format(search_query))
        return response
