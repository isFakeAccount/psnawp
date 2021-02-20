from psnap_api import authenticator
from psnap_api import client
from psnap_api import request_builder
from psnap_api import search
from psnap_api import user


# PlayStation Network API Python (PSNAP)
# original: https://github.com/games-directory/api-psn
# Retrieve User Information, Trophies, Game and Store data from the PlayStation Network
# Author: isFakeAccount

class PSNAP:
    def __init__(self, npsso):
        self.authenticator = authenticator.Authenticator(npsso_token=npsso)
        self.request_builder = request_builder.RequestBuilder(self.authenticator)

    def client(self):
        """
        Creates a new client object (your account)

        :return: Client Object
        """
        return client.Client(self.request_builder)

    def user(self, online_id):
        """
        Creates a new user object

        :param online_id: PSN ID of the user
        :return: User Object
        """
        return user.User(self.request_builder, online_id)

    def search(self):
        """
        Creates a new search object

        :return: Search Object
        """
        return search.Search(self.request_builder)
