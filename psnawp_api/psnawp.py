from psnawp_api import authenticator
from psnawp_api import client
from psnawp_api import request_builder
from psnawp_api import search
from psnawp_api import user


# PlayStation Network API Wrapper Python (PSNAWP)
# original: https://github.com/games-directory/api-psn
# Retrieve User Information, Trophies, Game and Store data from the PlayStation Network
# Author: isFakeAccount

class PSNAWP:
    def __init__(self, npsso):
        self.authenticator = authenticator.Authenticator(npsso_token=npsso)
        self.request_builder = request_builder.RequestBuilder(self.authenticator)

    def client(self):
        """
        Creates a new client object (your account)

        :return: Client Object
        """
        return client.Client(self.request_builder)

    def user(self, online_id=None, account_id=None):
        """
        Creates a new user object

        :param online_id: PSN ID of the user
        :param account_id: Account ID of the user
        :return: User Object
        :raises PSNAWPIllegalArgumentError: If the argument is empty
        :raises PSNAWPUserNotFound: If the user is invalid
        """
        return user.User(self.request_builder, online_id, account_id)

    def search(self):
        """
        Creates a new search object

        :return: Search Object
        """
        return search.Search(self.request_builder)
