from __future__ import annotations

from typing import Optional, Any, Iterator, Literal

from psnawp_api.core.psnawp_exceptions import (
    PSNAWPNotFound,
    PSNAWPForbidden,
    PSNAWPBadRequest,
)
from psnawp_api.models.listing.pagination_arguments import PaginationArguments
from psnawp_api.models.title_stats import TitleStatsListing
from psnawp_api.models.trophies.trophy import TrophyBuilder, Trophy
from psnawp_api.models.trophies.trophy_group import (
    TrophyGroupsSummary,
    TrophyGroupsSummaryBuilder,
)
from psnawp_api.models.trophies.trophy_summary import TrophySummary
from psnawp_api.models.trophies.trophy_titles import TrophyTitles, TrophyTitle
from psnawp_api.utils.endpoints import BASE_PATH, API_PATH
from psnawp_api.utils.request_builder import RequestBuilder


class User:
    """This class will contain the information about the PSN ID you passed in when creating object"""

    @classmethod
    def from_online_id(cls, request_builder: RequestBuilder, online_id: str) -> User:
        """Creates the User instance from online ID and returns the instance.

        :param request_builder: Used to call http requests.
        :type request_builder: RequestBuilder
        :param online_id: Online ID (GamerTag) of the user.
        :type online_id: str

        :returns: User Class object which represents a PlayStation account
        :rtype: User

        :raises: ``PSNAWPNotFound`` If the user is not valid/found.

        """
        try:
            query = {"fields": "accountId,onlineId,currentOnlineId"}
            response: dict[str, Any] = request_builder.get(
                url=f"{BASE_PATH['legacy_profile_uri']}{API_PATH['legacy_profile'].format(online_id=online_id)}",
                params=query,
            ).json()
            account_id = response["profile"]["accountId"]
            online_id = response["profile"].get("currentOnlineId") or response["profile"].get("onlineId")
            return cls(request_builder, online_id, account_id)
        except PSNAWPNotFound as not_found:
            raise PSNAWPNotFound(f"Online ID {online_id} does not exist.") from not_found

    @classmethod
    def from_account_id(cls, request_builder: RequestBuilder, account_id: str) -> User:
        """Creates the User instance from account ID and returns the instance.

        :param request_builder: Used to call http requests.
        :type request_builder: RequestBuilder
        :param account_id: Account ID of the user.
        :type account_id: str

        :returns: User Class object which represents a PlayStation account
        :rtype: User

        :raises: ``PSNAWPNotFound`` If the user is not valid/found.

        """
        try:
            response: dict[str, Any] = request_builder.get(url=f"{BASE_PATH['profile_uri']}{API_PATH['profiles'].format(account_id=account_id)}").json()
            return cls(request_builder, response["onlineId"], account_id)
        except PSNAWPBadRequest as bad_request:
            raise PSNAWPNotFound(f"Account ID {account_id} does not exist.") from bad_request

    def __init__(
        self,
        request_builder: RequestBuilder,
        online_id: str,
        account_id: str,
    ):
        """Constructor of Class User.

        .. note::

            This class is intended to be interfaced with through PSNAWP.

        :param request_builder: Used to call http requests.
        :type request_builder: RequestBuilder
        :param online_id: Online ID (GamerTag) of the user.
        :type online_id: str
        :param account_id: Account ID of the user.
        :type account_id: str

        :raises: ``PSNAWPIllegalArgumentError`` If both online_id and account_id are not provided.

        :raises: ``PSNAWPNotFound`` If the online id or account id is not valid/found.

        """
        self._request_builder = request_builder
        self.online_id = online_id
        self.account_id = account_id
        self.prev_online_id = online_id

    def profile(self) -> dict[str, Any]:
        """Gets the profile of the user such as about me, avatars, languages etc...

        :returns: A dict containing info similar to what is shown below:
        :rtype: dict[str, Any]

            .. literalinclude:: examples/user/profile.json
                :language: json


        .. code-block:: Python

            user_example = psnawp.user(online_id='VaultTec_Trading')
            print(user_example.profile())

        """

        response: dict[str, Any] = self._request_builder.get(url=f"{BASE_PATH['profile_uri']}{API_PATH['profiles'].format(account_id=self.account_id)}").json()
        return response

    def get_presence(self) -> dict[str, Any]:
        """Gets the presences of a user. If the profile is private

        :returns: A dict containing info similar to what is shown below:
        :rtype: dict[str, Any]

            .. literalinclude:: examples/user/get_presence.json
                :language: json


        :raises: ``PSNAWPForbidden`` When the user's profile is private, and you don't have permission to view their online status.

        .. code-block:: Python

            user_example = psnawp.user(online_id='VaultTec_Trading')
            print(user_example.get_presence())

        """
        try:
            params = {"type": "primary"}
            response: dict[str, Any] = self._request_builder.get(
                url=f"{BASE_PATH['profile_uri']}/{self.account_id}{API_PATH['basic_presences']}",
                params=params,
            ).json()
            return response
        except PSNAWPForbidden as forbidden:
            raise PSNAWPForbidden(f"You are not allowed to check the presence of user {self.online_id}") from forbidden

    def friendship(self) -> dict[str, Any]:
        """Gets the friendship status and stats of the user

        :returns: A dict containing info similar to what is shown below
        :rtype: dict[str, Any]

            .. literalinclude:: examples/user/friendship.json
                :language: json


        .. code-block:: Python

            user_example = psnawp.user(online_id='VaultTec_Trading')
            print(user_example.friendship())

        """
        response: dict[Any, Any] = self._request_builder.get(
            url=f"{BASE_PATH['profile_uri']}{API_PATH['friends_summary'].format(account_id=self.account_id)}"
        ).json()
        return response

    def is_blocked(self) -> bool:
        """Checks if the user is blocked by you

        :returns: True if the user is blocked otherwise False
        :rtype: bool

        .. code-block:: Python

            user_example = psnawp.user(online_id='VaultTec_Trading')
            print(user_example.is_blocked())

        """
        response = self._request_builder.get(url=f"{BASE_PATH['profile_uri']}{API_PATH['blocked_users']}").json()
        return self.account_id in response["blockList"]

    def trophy_summary(self) -> TrophySummary:
        """Retrieve an overall summary of the number of trophies earned for a user broken down by

        - type
        - overall trophy level
        - progress towards the next level
        - current tier

        :returns: Trophy Summary Object containing all information
        :rtype: TrophySummary

        :raises: ``PSNAWPForbidden`` If the user's profile is private

        .. code-block:: Python

            user_example = psnawp.user(online_id="VaultTec_Trading")
            print(user_example.trophy_summary())

        """
        return TrophySummary.from_endpoint(request_builder=self._request_builder, account_id=self.account_id)

    def trophy_titles(self, limit: Optional[int] = None) -> Iterator[TrophyTitle]:
        """Retrieve all game titles associated with an account, and a summary of trophies earned from them.

        :param limit: Limit of titles returned, None means to return all trophy titles.
        :type limit: Optional[int]

        :returns: Generator object with TitleTrophySummary objects
        :rtype: Iterator[TrophyTitle]

        :raises: ``PSNAWPForbidden`` If the user's profile is private

        .. code-block:: Python

            user_example = psnawp.user(online_id="VaultTec_Trading")
            for trophy_title in user_example.trophy_titles(limit=None):
                print(trophy_title)

        """
        return TrophyTitles(request_builder=self._request_builder, account_id=self.account_id).get_trophy_titles(limit=limit)

    def trophy_titles_for_title(self, title_ids: list[str]) -> Iterator[TrophyTitle]:
        """Retrieve a summary of the trophies earned by a user for specific titles.

        .. note::

            ``title_id`` can be obtained from https://andshrew.github.io/PlayStation-Titles/ or from :py:meth:`psnawp_api.models.search.Search.get_title_id`

        :param title_ids: Unique ID of the title
        :type title_ids: list[str]

        :returns: Generator object with TitleTrophySummary objects
        :rtype: Iterator[TrophyTitle]

        :raises: ``PSNAWPForbidden`` If the user's profile is private

        .. code-block:: Python

            user_example = psnawp.user(online_id="VaultTec_Trading")
            for trophy_title in user_example.trophy_titles_for_title(title_id='CUSA00265_00'):
                print(trophy_title)

        """
        return TrophyTitles(request_builder=self._request_builder, account_id=self.account_id).get_trophy_summary_for_title(title_ids=title_ids)

    def trophies(
        self,
        np_communication_id: str,
        platform: Literal["PS Vita", "PS3", "PS4", "PS5"],
        trophy_group_id: str = "default",
        limit: Optional[int] = None,
        include_metadata: bool = False,
    ) -> Iterator[Trophy]:
        """Retrieves the earned status individual trophy detail of a single - or all - trophy groups for a title.

        :param np_communication_id: Unique ID of the title used to request trophy information
        :type np_communication_id: str
        :param platform: The platform this title belongs to.
        :type platform: Literal
        :param trophy_group_id: ID for the trophy group. Each game expansion is represented by a separate ID. all to return all trophies for the title, default
            for the game itself, and additional groups starting from 001 and so on return expansions trophies.
        :type trophy_group_id: str
        :param limit: Limit of trophies returned, None means to return all trophy titles.
        :type limit: Optional[int]
        :param include_metadata: If True, will fetch metadata for trophy such as name and detail
        :type include_metadata: bool

        .. warning::

            Setting ``include_metadata`` to ``True`` will use twice the amount of rate limit since the API wrapper has to obtain metadata from a separate
            endpoint.

        :returns: Returns the Trophy Generator object with all the information
        :rtype: Iterator[Trophy]

        :raises: ``PSNAWPNotFound`` if you don't have any trophies for that game.

        :raises: ``PSNAWPForbidden`` If the user's profile is private

        """

        if not include_metadata:
            return TrophyBuilder(
                request_builder=self._request_builder,
                np_communication_id=np_communication_id,
            ).earned_game_trophies(
                account_id=self.account_id,
                platform=platform,
                trophy_group_id=trophy_group_id,
                limit=limit,
            )
        else:
            return TrophyBuilder(
                request_builder=self._request_builder,
                np_communication_id=np_communication_id,
            ).earned_game_trophies_with_metadata(
                account_id=self.account_id,
                platform=platform,
                trophy_group_id=trophy_group_id,
                limit=limit,
            )

    def trophy_groups_summary(
        self,
        np_communication_id: str,
        platform: Literal["PS Vita", "PS3", "PS4", "PS5"],
        include_metadata: bool = False,
    ) -> TrophyGroupsSummary:
        """Retrieves the trophy groups for a title and their respective trophy count.

        This is most commonly seen in games which have expansions where additional trophies are added.

        :param np_communication_id: Unique ID of the title used to request trophy information
        :type np_communication_id: str
        :param platform: The platform this title belongs to.
        :param platform: The platform this title belongs to.
        :type platform: Literal
        :param include_metadata: If True, will fetch results from another endpoint and include metadata for trophy group such as name and detail
        :type include_metadata: bool

        .. warning::

            Setting ``include_metadata`` to ``True`` will use twice the amount of rate limit since the API wrapper has to obtain metadata from a separate
            endpoint.

        :returns: TrophyGroupSummary object containing title and title groups trophy information.
        :rtype: TrophyGroupsSummary

        :raises: ``PSNAWPNotFound`` if you don't have any trophies for that game.

        :raises: ``PSNAWPForbidden`` If the user's profile is private

        """
        if not include_metadata:
            return TrophyGroupsSummaryBuilder(
                request_builder=self._request_builder,
                np_communication_id=np_communication_id,
            ).user_trophy_groups_summary(account_id=self.account_id, platform=platform)
        else:
            return TrophyGroupsSummaryBuilder(
                request_builder=self._request_builder,
                np_communication_id=np_communication_id,
            ).user_trophy_groups_summary_with_metadata(account_id=self.account_id, platform=platform)

    def title_stats(self, *, limit: Optional[int] = None, offset: int = 0, page_size: int = 200) -> TitleStatsListing:
        """Retrieve a list of titles with their stats and basic meta-data

        :param limit: Limit of titles returned.
        :type limit: Optional[int]
        :param page_size: The number of items to receive per api request.
        :type page_size: int
        :param offset: Specifies the offset for paginator
        :type offset: int

        .. warning::

            Only returns data for PS4 games and above.

        :returns: Iterator class for TitleStats
        :rtype: Iterator[TitleStatsListing]

        .. code-block:: Python

            user_example = psnawp.user(online_id='jeranther')
            for title in user_example.title_stats():
                ...

        """
        pg_args = PaginationArguments(total_limit=limit, offset=offset, page_size=page_size)
        return TitleStatsListing(request_builder=self._request_builder, account_id=self.account_id, pagination_arguments=pg_args)

    def __repr__(self) -> str:
        return f"<User online_id:{self.online_id} account_id:{self.account_id}>"

    def __str__(self) -> str:
        return f"Online ID: {self.online_id} Account ID: {self.account_id}"
