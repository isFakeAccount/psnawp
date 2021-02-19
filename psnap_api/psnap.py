from psnap_api import authenticator
from psnap_api import client


class PSNAP:
    def __init__(self, npsso):
        self.authenticator = authenticator.Authenticator(npsso_token=npsso)
        self.client = client.Client(self.authenticator)
