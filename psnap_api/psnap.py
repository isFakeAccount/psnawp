from psnap_api import authenticator
from psnap_api import client

# PlayStation Network API Python (PSNAP)
# original: https://github.com/games-directory/api-psn
# Retrieve User Information, Trophies, Game and Store data from the PlayStation Network
# Author: isFakeAccount

class PSNAP:
    def __init__(self, npsso):
        self.authenticator = authenticator.Authenticator(npsso_token=npsso)
        self.client = client.Client(self.authenticator)
