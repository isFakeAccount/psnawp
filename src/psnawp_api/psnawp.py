import logging
from typing import overload

from psnawp_api.core import authenticator
from psnawp_api.utils import request_builder
from psnawp_api.models import client, search, user
from psnawp_api.core.psnawp_exceptions import PSNAWPIllegalArgumentError

logging_level = logging.INFO


class PSNAWP:
    """PlayStation Network API Wrapper Python (PSNAWP) Retrieve User Information, Trophies, Game and Store data from the PlayStation Network

    Instances of this class are the gateway to interacting with PSN API through PSNAWP.

    """

    def __init__(self, npsso_cookie):
        """Constructor Method. Takes the npsso_cookie and creates instance of `request_builder.RequestBuilder` which is used later in code for HTTPS requests.

        :param npsso_cookie: npsso cookie obtained from PSN website.
        :type npsso_cookie: str

        :raises: `PSNAWPIllegalArgumentError` If npsso code len is not 64 characters.

        """
        self.request_builder = request_builder.RequestBuilder(
            authenticator.Authenticator(npsso_cookie)
        )

    def me(self):
        """Creates a new client object (your account).

        :returns: Client Object
        :rtype: client.Client

        """
        return client.Client(self.request_builder)

    @overload
    def user(self, online_id: str):
        ...

    @overload
    def user(self, account_id: str):
        ...

    def user(self, **kwargs):
        """Creates a new user object using Online ID (GamerTag) or Account ID (PSN ID).

        Note: You may only provide Online ID or Account ID. But not both at once.

        :param kwargs: online_id (str): Online ID (GamerTag) of the user. account_id
            (str): Account ID of the user.
        :type kwargs: dict

        :returns: User Object
        :rtype: user.User

        :raises: `PSNAWPIllegalArgumentError` If None or Both kwargs are passed.

        """
        online_id = kwargs.get("online_id")
        account_id = kwargs.get("account_id")

        if (online_id and account_id) or not (online_id or account_id):
            raise PSNAWPIllegalArgumentError(
                "You provide at least online ID or account ID, and not both."
            )

        return user.User(self.request_builder, online_id, account_id)

    def search(self):
        """Creates a new search object

        :returns: Search Object

        """
        return search.Search(self.request_builder)
