import logging
import re
from typing import overload, Optional, Iterable

from psnawp_api.core import authenticator
from psnawp_api.core.psnawp_exceptions import PSNAWPIllegalArgumentError
from psnawp_api.models.client import Client
from psnawp_api.models.group import Group
from psnawp_api.models.search import Search
from psnawp_api.models.user import User
from psnawp_api.utils import request_builder

logging_level = logging.INFO


class PSNAWP:
    """PlayStation Network API Wrapper Python (PSNAWP) Retrieve User Information, Trophies, Game and Store data from the PlayStation Network.

    Instances of this class are the gateway to interacting with PSN API through PSNAWP.

    .. code-block:: Python

        from psnawp_api import PSNAWP
        psnawp = PSNAWP('<64 character npsso code>')

    """

    def __init__(self, npsso_cookie):
        """Constructor Method. Takes the npsso_cookie and creates instance of ``request_builder.RequestBuilder`` which is used later in code for HTTPS requests.

        :param npsso_cookie: npsso cookie obtained from PSN website.
        :type npsso_cookie: str

        :raises: ``PSNAWPIllegalArgumentError`` If npsso code len is not 64 characters.

        """
        self._request_builder = request_builder.RequestBuilder(
            authenticator.Authenticator(npsso_cookie)
        )

    def me(self):
        """Creates a new client object (your account).

        :returns: Client Object
        :rtype: Client

        .. code-block:: Python

            from psnawp_api import PSNAWP
            psnawp = PSNAWP('<64 character npsso code>')
            client = psnawp.me()

        """
        return Client(self._request_builder)

    @overload
    def user(self, *, online_id: str):
        ...

    @overload
    def user(self, *, account_id: str):
        ...

    def user(self, **kwargs):
        """Creates a new user object using Online ID (GamerTag) or Account ID (PSN ID).

        .. note::

            You may only provide Online ID or Account ID. But not both at once.

        :param kwargs: online_id (str): Online ID (GamerTag) of the user. account_id
            (str): Account ID of the user.
        :type kwargs: dict

        :returns: User Object
        :rtype: User

        :raises: `PSNAWPIllegalArgumentError` If None or Both kwargs are passed.

        .. code-block:: Python

            user1 = psnawp.user(online_id="VaultTec_Trading")
            user2 = psnawp.user(account_id='1802043923080044300')

        """
        online_id: Optional[str] = kwargs.get("online_id")
        account_id: Optional[str] = kwargs.get("account_id")

        if (online_id and account_id) or not (online_id or account_id):
            raise PSNAWPIllegalArgumentError(
                "You provide at least online ID or account ID, and not both."
            )

        if account_id is not None and not re.match(r"\d{19}", account_id):
            raise PSNAWPIllegalArgumentError(
                "The account id is not correct. Perhaps you meant online_id?"
            )
        return User(self._request_builder, online_id, account_id)

    @overload
    def group(self, *, group_id: str) -> Group:
        ...

    @overload
    def group(self, *, users_list: Iterable[User]) -> Group:
        ...

    def group(self, **kwargs) -> Group:
        """Creates a group object from a Group ID or from list of users.

        .. warning::

            Passing ``users_list`` will create a new group each time. If you want to
            continue from the same group. Use group id obtained from
            ``client.get_groups()``

        :param kwargs: group_id (str): The Group ID of a group usually retrieved with
            the get_groups() method. users_list(Iterable[User]): A list of users of the
            members in the group.

        :returns: Group Object
        :rtype: Group

        :raises: ``PSNAWPIllegalArgumentError`` If None or Both kwargs are passed.

        """

        group_id: Optional[str] = kwargs.get("group_id")
        users: Optional[Iterable[User]] = kwargs.get("users_list")

        if (group_id and users) or not (group_id or users):
            raise PSNAWPIllegalArgumentError(
                "You provide at least Group Id or Users, and not both."
            )
        return Group(self._request_builder, group_id=group_id, users=users)

    def search(self):
        """Creates a new search object

        :returns: Search Object

        """
        return Search(self._request_builder)
