from psnap_api import authenticator
from psnap_api import client
from psnap_api import search
from psnap_api import user


# PlayStation Network API Python (PSNAP)
# original: https://github.com/games-directory/api-psn
# Retrieve User Information, Trophies, Game and Store data from the PlayStation Network
# Author: isFakeAccount

class PSNAP:
    def __init__(self, npsso):
        self.authenticator = authenticator.Authenticator(npsso_token=npsso)

    def client(self):
        """
        Creates a new client object

        :return: Client Object
        """
        return client.Client(self.authenticator)

    def user(self, account_id=None):
        """
        Creates a new user object

        :return: User Object
        """
        return user.User(self.authenticator, account_id)

    def search(self):
        """
        Creates a new search object

        :return: Search Object
        """
        return search.Search(self.authenticator)
