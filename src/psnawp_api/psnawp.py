from psnawp_api import request_builder
from psnawp_api import search, psnawp_exceptions, client
from psnawp_api import user
from psnawp_api import authenticator


class PSNAWP:
    """PlayStation Network API Wrapper Python (PSNAWP) Retrieve User Information, Trophies, Game and Store data from the PlayStation Network

    Instances of this class are the gateway to interacting with PSN API through PSNAWP.

    """

    def __init__(self, npsso_cookie):
        self.authenticator = authenticator.Authenticator(npsso_cookie)
        self.request_builder = request_builder.RequestBuilder(self.authenticator)

    def me(self):
        """Creates a new client object (your account). Reuses the

        :returns: Client Object

        """
        return client.Client(self)

    def user(self, **kwargs):
        """Creates a new user object

        :param kwargs: online_id: PSN ID of the user or account_id: Account ID of the
            user
        :type kwargs: str

        :returns: User Object

        :raises: If the user is not valid/found

        """
        online_id = None
        if "online_id" in kwargs.keys():
            online_id = kwargs["online_id"]

        account_id = None
        if "account_id" in kwargs.keys():
            account_id = kwargs["account_id"]

        if online_id is None and account_id is None:
            raise psnawp_exceptions.PSNAWPIllegalArgumentError(
                "You must provide either online ID or account ID"
            )

        return user.User(self.request_builder, self.me(), online_id, account_id)

    def search(self):
        """Creates a new search object

        :returns: Search Object

        """
        return search.Search(self.request_builder)
