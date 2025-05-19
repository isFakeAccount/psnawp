"""PlayStation Network API Wrapper Python (PSNAWP) Retrieve User Information, Trophies, Game and Store data from the PlayStation Network."""

from __future__ import annotations

from random import choice
from typing import TYPE_CHECKING, Any, Literal, overload

from pyrate_limiter import Duration, Rate

from psnawp_api.core import (
    Authenticator,
    PSNAWPIllegalArgumentError,
)
from psnawp_api.models import (
    Client,
    GameTitle,
    User,
)
from psnawp_api.models.group import Group
from psnawp_api.models.listing import PaginationArguments
from psnawp_api.models.search import SearchDomain, UniversalSearch
from psnawp_api.models.trophies import PlatformType

if TYPE_CHECKING:
    from collections.abc import Generator, Iterable

    from psnawp_api.core import RequestBuilderHeaders
    from psnawp_api.models.search import GameSearchResultItem, UserSearchResultItem


class PSNAWP:
    """The PSNAWP class provides convenient access to PlayStation's API.

    Instances of this class are the gateway to interacting with PSN API through PSNAWP.

    :var Authenticator authenticator: Instance of Authenticator class. Used to make authenticated HTTPs request to
        playstation server.

    """

    def __init__(
        self,
        npsso_cookie: str,
        headers: RequestBuilderHeaders | None = None,
        rate_limit: Rate | None = None,
    ) -> None:
        """Initializes the authentication handler with the provided NPSSO cookie.

        :param npsso_cookie: The NPSSO cookie obtained from the PlayStation Network website.
        :param dict[str, str] headers: Optional HTTP headers to include in all requests. Can be used to modify the API
            response language by setting ``Accept-Language`` or specify a region using ``Country``. Defaults to:

            - ``User-Agent``: Generic mobile browser user agent
            - ``Accept-Language``: ``en-US,en;q=0.9`` (English)
            - ``Country``: ``US`` (United States)
        :param rate_limit: Controls the request rate to the PSN API. By default, PSNAWP enforces a default rate limit of
            one request every three seconds—equivalent to up to 300 requests in a 15-minute window—to comply with
            PlayStation Network guidelines. Users may override this rate limit by providing a custom ``Rate`` instance,
            but doing so can lead to request throttling or temporary bans if set too aggressively.

        :raises PSNAWPAuthenticationError: If the NPSSO cookie is expired or invalid.

        """
        random_ua = [
            "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.6598.1817 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.5707.1741 Mobile Safari/537.36",
            "Mozilla/5.0 (Android 14; Mobile; rv:137.0) Gecko/137.0 Firefox/137.0",
            "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/55.0.9318.1385 Mobile Safari/537.36"
            "Mozilla/5.0 (iPhone; CPU iPhone OS 18_3_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/135.0.7049.83 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2469.1901 Mobile Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 18_3_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3.1 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 18_3_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3.1 Mobile/15E148 Safari/604.1",
        ]
        default_headers: RequestBuilderHeaders = {
            "User-Agent": choice(random_ua),
            "Accept-Language": "en-US,en;q=0.9",
            "Country": "US",
        }

        if rate_limit is None:
            rate_limit = Rate(1, Duration.SECOND * 3)

        _header = default_headers | headers if headers is not None else default_headers
        self.authenticator = Authenticator(
            npsso_cookie=npsso_cookie,
            common_headers=_header,
            rate_limit=rate_limit,
        )

    def me(self) -> Client:
        """Retrieve a Client instance for the authenticated user.

        The returned Client object represents the currently logged-in user and provides methods to perform user-centric
        operations, including (but not limited to):

        - Fetching the user's trophies.
        - Accepting or rejecting incoming friend requests.
        - Sending and receiving messages.
        - And more—see the Client class documentation for the full list of available methods.

        :returns: A Client object bound to your account, ready to manage the authenticated user's data and interactions.

        .. code-block:: python

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
        """Retrieve a User instance by Online ID or Account ID.

        The returned User object represents the specified PlayStation Network user and provides methods to inspect and
        interact with their account, including (but not limited to):

        - Fetching the user's trophies and trophy summaries.
        - Checking friendship status.
        - Determining whether the user has blocked you.
        - Retrieving basic profile information (avatar, bio, locale, etc.).
        - Querying presence data (online/offline status, current activity).
        - Sending friend requests or messages (subject to privacy settings).
        - And more—see the User class documentation for the complete list of available methods.

        .. note::

            The account_id takes higher precedence than online_id. If both arguments are passed, online_id will be
            ignored.

        :param online_id: Online ID (GamerTag) of the user.
        :param account_id: Account ID of the user.

        :returns: User Object

        :raises PSNAWPIllegalArgumentError: If None of the kwargs are passed.
        :raises PSNAWPNotFoundError: If the online_id or account_id is not valid/found.

        .. code-block:: Python

            user1 = psnawp.user(online_id="VaultTec_Trading")
            user2 = psnawp.user(account_id="1802043923080044300")

        """
        online_id: str | None = kwargs.get("online_id")
        account_id: str | None = kwargs.get("account_id")

        if account_id is not None:
            return User.from_account_id(self.authenticator, account_id)
        if online_id is not None:
            return User.from_online_id(self.authenticator, online_id)
        raise PSNAWPIllegalArgumentError(
            "You must provide at least online ID or account ID.",
        )

    def game_title(
        self,
        title_id: str,
        platform: PlatformType,
        account_id: str = "6515971742264256071",
        np_communication_id: str | None = None,
    ) -> GameTitle:
        """Creates a GameTitle class object from title_id which represents a PlayStation video game title.

        .. important::

            ``title_id`` can be obtained from https://andshrew.github.io/PlayStation-Titles/,
            https://serialstation.com/trophies/ or from
            :py:class:`~psnawp_api.models.search.universal_search.UniversalSearch`.

            PlayStation3 and PS Vita cannot be searched using
            :py:class:`~psnawp_api.models.search.universal_search.UniversalSearch`. Also their np communication id can't
            be fetched using
            :py:meth:`~psnawp_api.models.trophies.trophy_titles.TrophyTitleIterator.get_np_communication_id`. The user
            must provide the np communication id for PS3/PS VITA title themselves.

        .. tip::

            GameTitle lets you fetch trophies for the game you don't own. If you are trying to fetch your own trophies
            see the :py:class:`psnawp_api.models.client.Client` class. Use the :py:meth:`me` to create instance of the
            Client class.

        .. note::

            The PlayStation API requires NP Communication ID to fetch trophies for a title. The only way you can get NP
            Communication ID (``np_communication_id``) endpoint is through Trophy Titles endpoint that takes in NP Title
            ID (``title_id``) and fetches the corresponding NP Communication ID for it. However, that catch is that the
            endpoint only returns NP Communication ID if you own that game.

            To allow users to retrieve information without having to own that video game I picked a default user who has
            played the most number of games based on this website
            (https://www.truetrophies.com/leaderboard/gamer/gamesplayed). It is possible that the there are games this
            user has not played and in that case it is better to provide your own account id (``'me'``) or someone who
            has played that game.

        .. note::

            During the construction of the object, an additional call is made to get the ``np_communication_id``. This
            ID is important for getting trophy data. This call can be skipped by providing ``np_communication_id`` in as
            argument.

        :param title_id: unique ID of game title.
        :param platform: The platform this title belongs to.
        :param: account_id: The account whose trophy list is being accessed
        :param np_communication_id: Unique ID of a game title used to request trophy information.

        :returns: Title Object

        :raises PSNAWPNotFoundError: If the user does not have any trophies for that game or the game doesn't exist.
        :raises PSNAWPIllegalArgumentError: If ``np_communication_id`` is not provided for the following platforms:
            PlatformType.PS3, PlatformType.PS_VITA, PlatformType.PSPC.

        """
        if platform in (PlatformType.PS3, PlatformType.PS_VITA, PlatformType.PSPC) and np_communication_id is None:
            raise PSNAWPIllegalArgumentError(f"np_communication_id is required for the platform {platform}.")

        if np_communication_id is None:
            return GameTitle.from_title_id(authenticator=self.authenticator, title_id=title_id, platform=platform, account_id=account_id)

        return GameTitle.with_np_communication_id(
            authenticator=self.authenticator,
            title_id=title_id,
            platform=platform,
            np_communication_id=np_communication_id,
        )

    @overload
    def group(self, *, group_id: str) -> Group: ...

    @overload
    def group(self, *, users_list: Iterable[User]) -> Group: ...

    def group(self, **kwargs: Any) -> Group:
        """Creates a group object from a Group ID or from list of users.

        .. warning::

            Passing ``users_list`` will create a new group each time. If you want to continue from the same group. Use
            group id obtained from :py:meth:`psnawp_api.models.client.Client.get_groups()`

        :param group_id: The Group ID of a group usually retrieved with the ``get_groups()`` method.
        :param users_list: A list of users of the members in the group.

        :returns: Group Object

        :raises PSNAWPNotFoundError: If group id does not exist or is invalid.
        :raises PSNAWPForbiddenError: If you are sending message a user who has blocked you.

        """
        group_id: str | None = kwargs.get("group_id")
        users: Iterable[User] | None = kwargs.get("users_list")

        if group_id is not None:
            return Group.create_from_group_id(self.authenticator, group_id=group_id)
        if users is not None:
            return Group.create_from_users(self.authenticator, users=users)
        raise PSNAWPIllegalArgumentError("You provide at least Group Id or Users")

    @overload
    def search(
        self,
        search_query: str,
        search_domain: Literal[SearchDomain.USERS],
        limit: int | None = None,
        offset: int = 0,
        page_size: int = 20,
    ) -> Generator[UserSearchResultItem, None, None]: ...
    @overload
    def search(
        self,
        search_query: str,
        search_domain: Literal[SearchDomain.FULL_GAMES],
        limit: int | None = None,
        offset: int = 0,
        page_size: int = 20,
    ) -> Generator[GameSearchResultItem, None, None]: ...
    @overload
    def search(
        self,
        search_query: str,
        search_domain: Literal[SearchDomain.ADD_ONS],
        limit: int | None = None,
        offset: int = 0,
        page_size: int = 20,
    ) -> Generator[GameSearchResultItem, None, None]: ...
    def search(
        self,
        search_query: str,
        search_domain: SearchDomain,
        limit: int | None = None,
        offset: int = 0,
        page_size: int = 20,
    ) -> Generator[GameSearchResultItem, None, None] | Generator[UserSearchResultItem, None, None]:
        """Creates a new search object based on search_domain that can be used to search for games, games-addons, and users.

        :param search_query: The search query string, used to specify the terms or keywords to search for.
        :param search_domain: Specifies the domain to search within, such as games, add-ons, or users.
        :param limit: Total numbers of items to receive, None means no limit.
        :param page_size: The number of items to receive per api request.
        :param offset: Specifies the offset for paginator.

        :returns: Search Iterator object to iterate over search results.

        """
        pg_args = PaginationArguments(
            total_limit=limit,
            offset=offset,
            page_size=page_size,
        )

        if search_domain == SearchDomain.USERS:
            return UniversalSearch(
                authenticator=self.authenticator,
                pagination_args=pg_args,
                search_query=search_query,
            ).search_user()

        return UniversalSearch(
            authenticator=self.authenticator,
            pagination_args=pg_args,
            search_query=search_query,
        ).search_game(search_domain)
