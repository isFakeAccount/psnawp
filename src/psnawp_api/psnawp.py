from __future__ import annotations

import logging
from typing import overload, Optional, Iterator, Any

from psnawp_api.core import authenticator
from psnawp_api.core.psnawp_exceptions import PSNAWPIllegalArgumentError
from psnawp_api.models.client import Client
from psnawp_api.models.game_title import GameTitle
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

    def __init__(self, npsso_cookie: str, *, accept_language: str = "en-US", country: str = "US"):
        """Constructor Method. Takes the npsso_cookie and creates instance of ``request_builder.RequestBuilder`` which is used later in code for HTTPS requests.

        :param str npsso_cookie: npsso cookie obtained from PSN website.
        :param str accept_language: The preferred language(s) for content negotiation in HTTP headers.
        :param str country: The client's country for HTTP headers.

        :raises: ``PSNAWPAuthenticationError`` If npsso code is expired or is incorrect.

        """
        self._request_builder = request_builder.RequestBuilder(authenticator.Authenticator(npsso_cookie), accept_language, country)

    def me(self) -> Client:
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
    def user(self, *, online_id: str) -> User:
        ...

    @overload
    def user(self, *, account_id: str) -> User:
        ...

    def user(self, **kwargs: Any) -> User:
        """Creates a new user object using Online ID (GamerTag) or Account ID (PSN ID).

        .. note::

            The account_id takes higher precedence than online_id. If both arguments are passed, online_id will be ignored.

        :param kwargs: online_id (str): Online ID (GamerTag) of the user. account_id (str): Account ID of the user.
        :type kwargs: dict

        :returns: User Object
        :rtype: User

        :raises: `PSNAWPIllegalArgumentError` If None of the kwargs are passed.

        :raises: ``PSNAWPNotFound`` If the online_id or account_id is not valid/found.

        .. code-block:: Python

            user1 = psnawp.user(online_id="VaultTec_Trading")
            user2 = psnawp.user(account_id='1802043923080044300')

        """
        online_id: Optional[str] = kwargs.get("online_id")
        account_id: Optional[str] = kwargs.get("account_id")

        if account_id is not None:
            return User.from_account_id(self._request_builder, account_id)
        elif online_id is not None:
            return User.from_online_id(self._request_builder, online_id)
        else:
            raise PSNAWPIllegalArgumentError("You must provide at least online ID or account ID.")

    def game_title(self, title_id: str, account_id: str = "6515971742264256071", np_communication_id: Optional[str] = None) -> GameTitle:
        """Creates a GameTitle class object from title_id which represents a PlayStation video game title.

        .. note::

            The GameTitle class is only useful if the user has played that video game. To allow users to retrieve information without having to play that video
            game I picked a default user who has played the most number of games based on this website
            (https://www.truetrophies.com/leaderboard/gamer/gamesplayed). It is possible that the there are games this user has not played and in that case it
            is better to provide your own account id (``'me'``) or someone who has played that game.

        .. note::

            ``title_id`` can be obtained from https://andshrew.github.io/PlayStation-Titles/ or from :py:meth:`psnawp_api.models.search.Search.get_title_id`

        .. note::

            During the construction of the object, an additional call is made to get the np_communication_id. This ID is important for getting trophy data. This
            call can be skipped by providing np_communication_id in as argument.

        :param title_id: unique ID of game title.
        :type title_id: str
        :param: account_id: The account whose trophy list is being accessed
        :type account_id: str
        :param np_communication_id: Unique ID of a game title used to request trophy information.
        :type np_communication_id: Optional[str]

        :returns: Title Object
        :rtype: GameTitle

        :raises: ``PSNAWPNotFound`` If the user does not have any trophies for that game or the game doesn't exist.

        """
        return GameTitle(self._request_builder, title_id=title_id, account_id=account_id, np_communication_id=np_communication_id)

    @overload
    def group(self, *, group_id: str) -> Group:
        ...

    @overload
    def group(self, *, users_list: Iterator[User]) -> Group:
        ...

    def group(self, **kwargs: Any) -> Group:
        """Creates a group object from a Group ID or from list of users.

        .. warning::

            Passing ``users_list`` will create a new group each time. If you want to continue from the same group. Use group id obtained from
            ``client.get_groups()``

        :param kwargs: group_id (str): The Group ID of a group usually retrieved with the get_groups() method. users_list(Iterator[User]): A list of users of
            the members in the group.

        :returns: Group Object
        :rtype: Group

        :raises: ``PSNAWPIllegalArgumentError`` If None or Both kwargs are passed.

        :raises: ``PSNAWPForbidden`` If you are Dming a user who has blocked you.

        """

        group_id: Optional[str] = kwargs.get("group_id")
        users: Optional[Iterator[User]] = kwargs.get("users_list")

        if (group_id and users) or not (group_id or users):
            raise PSNAWPIllegalArgumentError("You provide at least Group Id or Users, and not both.")
        return Group(self._request_builder, group_id=group_id, users=users)

    def search(self) -> Search:
        """Creates a new search object

        :returns: Search Object

        """
        return Search(self._request_builder)
