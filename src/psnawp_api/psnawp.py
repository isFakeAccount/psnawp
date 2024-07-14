from __future__ import annotations

from typing import Any, Generator, Iterable, Optional, overload

from psnawp_api.core import Authenticator, PSNAWPIllegalArgumentError, RequestBuilderHeaders
from psnawp_api.models import Client, GameTitle, Group, SearchDomain, UniversalSearch, User
from psnawp_api.models.listing import PaginationArguments
from psnawp_api.models.search import SearchResult


class PSNAWP:
    """PlayStation Network API Wrapper Python (PSNAWP) Retrieve User Information, Trophies, Game and Store data from the PlayStation Network.

    Instances of this class are the gateway to interacting with PSN API through PSNAWP.

    .. code-block:: Python

        from psnawp_api import PSNAWP

        psnawp = PSNAWP("<64 character npsso code>")

    """

    def __init__(
        self,
        npsso_cookie: str,
        headers: Optional[RequestBuilderHeaders] = None,
    ) -> None:
        """Constructor Method. Takes the npsso_cookie and creates instance of ``request_builder.RequestBuilder`` which is used later in code for HTTPS requests.

        :param npsso_cookie: npsso cookie obtained from PSN website.
        :param headers: Common headers that will be added to all HTTP request such as ``Country`` and ``Accept-Language``.

        :raises PSNAWPAuthenticationError: If npsso code is expired or is incorrect.

        """

        default_headers: RequestBuilderHeaders = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 11; sdk_gphone_x86 Build/RSR1.201013.001; wv) \
            AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.106 Mobile Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Country": "US",
        }

        _header = default_headers | headers if headers is not None else default_headers
        self.authenticator = Authenticator(
            npsso_cookie=npsso_cookie,
            common_headers=_header,
        )

    def me(self) -> Client:
        """Creates a new client object (your account).

        :returns: Client Object

        .. code-block:: Python

            from psnawp_api import PSNAWP

            psnawp = PSNAWP("<64 character npsso code>")
            client = psnawp.me()

        """
        return Client(self.authenticator)

    @overload
    def user(self, *, online_id: str) -> User: ...

    @overload
    def user(self, *, account_id: str) -> User: ...

    def user(self, **kwargs: Any) -> User:
        """Creates a new user object using Online ID (GamerTag) or Account ID (PSN ID).

        .. note::

            The account_id takes higher precedence than online_id. If both arguments are passed, online_id will be ignored.

        :param online_id: Online ID (GamerTag) of the user.
        :param account_id: Account ID of the user.

        :returns: User Object

        :raises PSNAWPIllegalArgumentError: If None of the kwargs are passed.
        :raises PSNAWPNotFound: If the online_id or account_id is not valid/found.

        .. code-block:: Python

            user1 = psnawp.user(online_id="VaultTec_Trading")
            user2 = psnawp.user(account_id="1802043923080044300")

        """
        online_id: Optional[str] = kwargs.get("online_id")
        account_id: Optional[str] = kwargs.get("account_id")

        if account_id is not None:
            return User.from_account_id(self.authenticator, account_id)
        elif online_id is not None:
            return User.from_online_id(self.authenticator, online_id)
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

            ``title_id`` can be obtained from https://andshrew.github.io/PlayStation-Titles/ or from :py:class:`psnawp_api.models.search.Search`

        .. note::

            During the construction of the object, an additional call is made to get the np_communication_id. This ID is important for getting trophy data. This
            call can be skipped by providing np_communication_id in as argument.

        :param title_id: unique ID of game title.
        :param: account_id: The account whose trophy list is being accessed
        :param np_communication_id: Unique ID of a game title used to request trophy information.

        :returns: Title Object

        :raises PSNAWPNotFound: If the user does not have any trophies for that game or the game doesn't exist.

        """
        return GameTitle(self.authenticator, title_id=title_id, account_id=account_id, np_communication_id=np_communication_id)

    @overload
    def group(self, *, group_id: str) -> Group: ...

    @overload
    def group(self, *, users_list: Iterable[User]) -> Group: ...

    def group(self, **kwargs: Any) -> Group:
        """Creates a group object from a Group ID or from list of users.

        .. warning::

            Passing ``users_list`` will create a new group each time. If you want to continue from the same group. Use group id obtained from
            ``client.get_groups()``

        :param group_id: The Group ID of a group usually retrieved with the ``get_groups()`` method.
        :param users_list: A list of users of the members in the group.

        :returns: Group Object

        :raises PSNAWPNotFound: If group id does not exist or is invalid.
        :raises PSNAWPForbidden: If you are sending message a user who has blocked you.

        """

        group_id: Optional[str] = kwargs.get("group_id")
        users: Optional[Iterable[User]] = kwargs.get("users_list")

        if group_id is not None:
            return Group.create_from_group_id(self.authenticator, group_id=group_id)
        elif users is not None:
            return Group.create_from_users(self.authenticator, users=users)
        else:
            raise PSNAWPIllegalArgumentError("You provide at least Group Id or Users")

    def search(
        self,
        search_query: str,
        search_domain: SearchDomain,
        limit: Optional[int] = None,
        offset: int = 0,
        page_size: int = 20,
    ) -> Generator[SearchResult, None, None]:
        """Creates a new search object

        :param search_query: _description_
        :param search_domain: _description_
        :param limit: Total numbers of items to receive, None means no limit.
        :param page_size: The number of items to receive per api request.
        :param offset: Specifies the offset for paginator.

        :returns: Search Iterator object to iterate over search results.

        """
        pg_args = PaginationArguments(total_limit=limit, offset=offset, page_size=page_size)
        if search_domain == SearchDomain.FULL_GAMES:
            return UniversalSearch(authenticator=self.authenticator, pagination_args=pg_args, search_query=search_query).search_full_game()
        else:
            return UniversalSearch(authenticator=self.authenticator, pagination_args=pg_args, search_query=search_query).search_add_onns()
