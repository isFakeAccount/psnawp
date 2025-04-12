"""Provides Class User representing a PlayStation User account."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, overload

from typing_extensions import Self

from psnawp_api.core import (
    PSNAWPBadRequestError,
    PSNAWPForbiddenError,
    PSNAWPNotFoundError,
)
from psnawp_api.models.listing import PaginationArguments
from psnawp_api.models.title_stats import TitleStatsIterator
from psnawp_api.models.trophies import (
    TrophyGroupsSummaryBuilder,
    TrophyIterator,
    TrophySummary,
    TrophyTitleIterator,
    TrophyWithProgressIterator,
)
from psnawp_api.utils import API_PATH, BASE_PATH, extract_region_from_npid

if TYPE_CHECKING:
    from collections.abc import Generator

    from pycountry.db import Country

    from psnawp_api.core import Authenticator
    from psnawp_api.models.trophies import (
        PlatformType,
        TrophyGroupsSummary,
        TrophyGroupSummary,
        TrophyGroupSummaryWithProgress,
    )


class User:
    """Class containing the information about the PSN ID you passed in when creating object.

    .. note::

        This class is intended to be used via PSNAWP. See :py:meth:`psnawp_api.psnawp.PSNAWP.user`

    """

    @classmethod
    def from_online_id(cls, authenticator: Authenticator, online_id: str) -> Self:
        """Creates the User instance from online ID and returns the instance.

        :param authenticator: The Authenticator instance used for making authenticated requests to the API.
        :param online_id: Online ID (GamerTag) of the user.

        :returns: User Class object which represents a PlayStation account

        :raises PSNAWPNotFoundError: If the user is not valid/found.

        """
        try:
            query = {"fields": "accountId,onlineId,currentOnlineId"}
            response: dict[str, Any] = authenticator.get(
                url=f"{BASE_PATH['legacy_profile_uri']}{API_PATH['legacy_profile'].format(online_id=online_id)}",
                params=query,
            ).json()
            account_id = response["profile"]["accountId"]
            online_id = response["profile"].get("currentOnlineId") or response["profile"].get("onlineId")
            return cls(authenticator, online_id, account_id)
        except PSNAWPNotFoundError as not_found:
            raise PSNAWPNotFoundError(
                f"Online ID {online_id} does not exist.",
            ) from not_found

    @classmethod
    def from_account_id(cls, authenticator: Authenticator, account_id: str) -> Self:
        """Creates the User instance from account ID and returns the instance.

        :param request_builder: Used to call http requests.
        :param account_id: Account ID of the user.

        :returns: User Class object which represents a PlayStation account

        :raises PSNAWPNotFoundError: If the user is not valid/found.

        """
        try:
            response: dict[str, Any] = authenticator.get(
                url=f"{BASE_PATH['profile_uri']}{API_PATH['profiles'].format(account_id=account_id)}",
            ).json()
            return cls(authenticator, response["onlineId"], account_id)
        except PSNAWPBadRequestError as bad_request:
            raise PSNAWPNotFoundError(
                f"Account ID {account_id} does not exist.",
            ) from bad_request

    def __init__(
        self,
        authenticator: Authenticator,
        online_id: str,
        account_id: str,
    ) -> None:
        """Constructor of Class User.

        :param authenticator: The Authenticator instance used for making authenticated requests to the API.
        :param online_id: Online ID (GamerTag) of the user.
        :param account_id: Account ID of the user.

        """
        self.authenticator = authenticator
        self.online_id = online_id
        self.account_id = account_id
        self.prev_online_id = online_id

    def profile(self) -> dict[str, Any]:
        """Gets the profile of the user such as about me, avatars, languages etc...

        :returns: A dict containing info similar to what is shown below:

            .. literalinclude:: ../examples/user/profile.json
                :language: json


        .. code-block:: Python

            user_example = psnawp.user(online_id="VaultTec_Trading")
            print(user_example.profile())

        """
        response: dict[str, Any] = self.authenticator.get(
            url=f"{BASE_PATH['profile_uri']}{API_PATH['profiles'].format(account_id=self.account_id)}",
        ).json()
        return response

    def get_region(self) -> Country | None:
        """Gets the region of the user.

        :returns: Returns Country object from Pycountry of the User or None if not found.

        .. code-block:: Python

            user_example = psnawp.user(online_id="VaultTec_Trading")
            print(user_example.get_region())

        .. note::

            See https://github.com/pycountry/pycountry for more info on Country object.

        """
        response = self.get_profile_legacy()
        npid = response.get("profile", {}).get("npId", "")
        return extract_region_from_npid(npid)

    def get_profile_legacy(self) -> dict[str, Any]:
        """Gets the user profile info from legacy api endpoint. Useful for legacy console (PS3, PS4) presence.

        :returns: A dict containing info similar to what is shown below:

            .. literalinclude:: ../examples/client/get_profile_legacy.json
                :language: json


        .. code-block:: Python

            user_example = psnawp.user(online_id="VaultTec_Trading")
            print(user_example.get_profile_legacy())

        """
        params = {
            "fields": "npId,onlineId,accountId,avatarUrls,plus,aboutMe,languagesUsed,trophySummary(@default,level,progress,earnedTrophies),"
            "isOfficiallyVerified,personalDetail(@default,profilePictureUrls),personalDetailSharing,personalDetailSharingRequestMessageFlag,"
            "primaryOnlineStatus,presences(@default,@titleInfo,platform,lastOnlineDate,hasBroadcastData),requestMessageFlag,blocking,friendRelation,"
            "following,consoleAvailability",
        }

        response: dict[str, Any] = self.authenticator.get(
            url=f"{BASE_PATH['legacy_profile_uri']}{API_PATH['legacy_profile'].format(online_id=self.online_id)}",
            params=params,
        ).json()

        return response

    def get_presence(self) -> dict[str, Any]:
        """Gets the presences of a user.

        :returns: A dict containing info similar to what is shown below:

            .. literalinclude:: ../examples/user/get_presence.json
                :language: json


        :raises PSNAWPForbiddenError: When the user's profile is private, and you don't have permission to view their
            online status.

        .. code-block:: Python

            user_example = psnawp.user(online_id="VaultTec_Trading")
            print(user_example.get_presence())

        """
        try:
            params = {
                "type": "primary",
                "platforms": "PS4,PS5,MOBILE_APP,PSPC",
                "withOwnGameTitleInfo": "true",
            }
            response: dict[str, Any] = self.authenticator.get(
                url=f"{BASE_PATH['profile_uri_v2']}/{self.account_id}{API_PATH['basic_presences']}",
                params=params,
            ).json()
        except PSNAWPForbiddenError as forbidden:
            raise PSNAWPForbiddenError(
                f"You are not allowed to check the presence of user {self.online_id}",
            ) from forbidden
        else:
            return response

    def friendship(self) -> dict[str, Any]:
        """Gets the friendship status and stats of the user.

        :returns: A dict containing info similar to what is shown below

            .. literalinclude:: ../examples/user/friendship.json
                :language: json


        .. code-block:: Python

            user_example = psnawp.user(online_id="VaultTec_Trading")
            print(user_example.friendship())

        """
        response: dict[Any, Any] = self.authenticator.get(
            url=f"{BASE_PATH['profile_uri']}{API_PATH['friends_summary'].format(account_id=self.account_id)}",
        ).json()
        return response

    def accept_friend_request(self) -> None:
        """Accept the friend request by the User.

        :returns: None

        """
        self.authenticator.put(
            url=f"{BASE_PATH['profile_uri']}{API_PATH['manage_friendship'].format(account_id=self.account_id)}",
        )

    def remove_friend(self) -> None:
        """Decline the friend request or unfriend the User.

        :returns: None

        """
        self.authenticator.delete(
            url=f"{BASE_PATH['profile_uri']}{API_PATH['manage_friendship'].format(account_id=self.account_id)}",
        )

    def friends_list(self, limit: int = 1000) -> Generator[User, None, None]:
        """Gets the friends list and returns an iterator of User objects.

        :param limit: The number of items from input max is 1000.

        :returns: All friends in your friends list.

        :raises PSNAWPForbiddenError: When the user's when you don't have permission to view their friends list.

        .. code-block:: Python

            user_example = psnawp.user(online_id="VaultTec_Trading")
            friends_list = user_example.friends_list()

            for friend in friends_list:
                ...

        """
        limit = min(1000, limit)

        params = {"limit": limit}
        response = self.authenticator.get(
            url=f"{BASE_PATH['profile_uri']}{API_PATH['friends_list'].format(account_id=self.account_id)}",
            params=params,
        ).json()
        return (
            User.from_account_id(
                authenticator=self.authenticator,
                account_id=account_id,
            )
            for account_id in response["friends"]
        )

    def is_blocked(self) -> bool:
        """Checks if the user is blocked by you.

        :returns: True if the user is blocked otherwise False

        .. code-block:: Python

            user_example = psnawp.user(online_id="VaultTec_Trading")
            print(user_example.is_blocked())

        """
        response = self.authenticator.get(
            url=f"{BASE_PATH['profile_uri']}{API_PATH['blocked_users']}",
        ).json()
        return self.account_id in response["blockList"]

    def get_shareable_profile_link(self) -> dict[str, str]:
        """Gets the shareable link and QR code for the PlayStation profile.

        This method fetches the URL that can be used to easily share the user's PlayStation profile. Additionally, it
        provides a QR code image URL that corresponds to the shareable URL.

        :returns: A dict containing info similar to what is shown below:

            .. literalinclude:: ../examples/client/shareable_profile.json
                :language: json


        .. code-block:: Python

            user_example = psnawp.user(online_id="VaultTec_Trading")
            print(user_example.get_shareable_profile_link())

        """
        response: dict[str, str] = self.authenticator.get(
            url=f"{BASE_PATH['cpss']}{API_PATH['share_profile'].format(account_id=self.account_id)}",
        ).json()
        return response

    def trophy_summary(self) -> TrophySummary:
        """Retrieve an overall summary of the number of trophies earned for a user broken down by.

        - type
        - overall trophy level
        - progress towards the next level
        - current tier

        :returns: Trophy Summary Object containing all information

        :raises PSNAWPForbiddenError: If the user's profile is private

        .. code-block:: Python

            user_example = psnawp.user(online_id="VaultTec_Trading")
            print(user_example.trophy_summary())

        """
        return TrophySummary.from_endpoint(
            authenticator=self.authenticator,
            account_id=self.account_id,
        )

    def trophy_titles(
        self,
        limit: int | None = None,
        offset: int = 0,
        page_size: int = 50,
    ) -> TrophyTitleIterator:
        """Retrieve all game titles associated with an account, and a summary of trophies earned from them.

        :param limit: Limit of titles returned, None means to return all trophy titles.
        :param page_size: The number of items to receive per api request.
        :param offset: Specifies the offset for paginator.

        :returns: Generator object with TrophyTitle objects.

        :raises PSNAWPForbiddenError: If the user's profile is private.

        .. code-block:: Python

            user_example = psnawp.user(online_id="VaultTec_Trading")
            for trophy_title in user_example.trophy_titles(limit=None):
                print(trophy_title)

        """
        pg_args = PaginationArguments(
            total_limit=limit,
            offset=offset,
            page_size=page_size,
        )
        return TrophyTitleIterator.from_endpoint(
            authenticator=self.authenticator,
            pagination_args=pg_args,
            account_id=self.account_id,
            title_ids=None,
        )

    def trophy_titles_for_title(self, title_ids: list[str]) -> TrophyTitleIterator:
        """Retrieve a summary of the trophies earned by a user for specific titles.

        :param list[str] title_ids: Unique ID of the title.

        :returns: Generator object with TrophyTitle objects.

        :raises PSNAWPForbiddenError: If the user's profile is private.

        .. note::

            ``title_id`` can be obtained from https://andshrew.github.io/PlayStation-Titles/ or from
            :py:class:`~psnawp_api.models.search.universal_search.UniversalSearch`

        .. code-block:: Python

            user_example = psnawp.user(online_id="VaultTec_Trading")
            for trophy_title in user_example.trophy_titles_for_title(title_ids=["CUSA00265_00"]):
                print(trophy_title)

        """
        pg_args = PaginationArguments(
            total_limit=None,
            offset=0,
            page_size=0,
        )  # Not used
        return TrophyTitleIterator.from_endpoint(
            authenticator=self.authenticator,
            pagination_args=pg_args,
            account_id=self.account_id,
            title_ids=title_ids,
        )

    @overload
    def trophies(
        self,
        np_communication_id: str,
        platform: PlatformType,
        include_progress: Literal[False] = False,
        trophy_group_id: str = "default",
        limit: int | None = None,
        offset: int = 0,
        page_size: int = 200,
    ) -> TrophyIterator: ...
    @overload
    def trophies(
        self,
        np_communication_id: str,
        platform: PlatformType,
        include_progress: Literal[True],
        trophy_group_id: str = "default",
        limit: int | None = None,
        offset: int = 0,
        page_size: int = 200,
    ) -> TrophyWithProgressIterator: ...
    def trophies(
        self,
        np_communication_id: str,
        platform: PlatformType,
        include_progress: bool = False,
        trophy_group_id: str = "default",
        limit: int | None = None,
        offset: int = 0,
        page_size: int = 200,
    ) -> TrophyIterator | TrophyWithProgressIterator:
        """Retrieves all trophies for a specified group within a game title, optionally including user progress.

        :param np_communication_id: Unique ID of a game title used to request trophy information. This can be obtained
            from ``GameTitle`` class.
        :param platform: The platform this title belongs to.
        :param trophy_group_id: ID for the trophy group. Each game expansion is represented by a separate ID. all to
            return all trophies for the title, default for the game itself, and additional groups starting from 001 and
            so on return expansions trophies.
        :param limit: Maximum number of trophies to return. None means all available trophies will be returned.
        :param include_progress: If True, includes progress information for each trophy.
        :param offset: The starting point within the collection of trophies.
        :param page_size: The number of trophies to return per page.

        :returns: Returns the Trophy Generator object with all the information

        :raises PSNAWPNotFoundError: If you don't have any trophies for that game.
        :raises PSNAWPForbiddenError: If the user's profile is private

        .. warning::

            Setting ``include_progress`` to ``True`` will consume more rate limits as progress information is fetched
            from a separate endpoint.

        """
        pg_args = PaginationArguments(
            total_limit=limit,
            offset=offset,
            page_size=page_size,
        )
        if not include_progress:
            return TrophyIterator.from_endpoint(
                authenticator=self.authenticator,
                pagination_args=pg_args,
                np_communication_id=np_communication_id,
                platform=platform,
                trophy_group_id=trophy_group_id,
            )
        return TrophyWithProgressIterator.from_endpoint(
            authenticator=self.authenticator,
            pagination_args=pg_args,
            np_communication_id=np_communication_id,
            platform=platform,
            trophy_group_id=trophy_group_id,
            account_id=self.account_id,
        )

    @overload
    def trophy_groups_summary(
        self,
        np_communication_id: str,
        platform: PlatformType,
        include_progress: Literal[False] = False,
    ) -> TrophyGroupsSummary[TrophyGroupSummary]: ...
    @overload
    def trophy_groups_summary(
        self,
        np_communication_id: str,
        platform: PlatformType,
        include_progress: Literal[True],
    ) -> TrophyGroupsSummary[TrophyGroupSummaryWithProgress]: ...
    def trophy_groups_summary(
        self,
        np_communication_id: str,
        platform: PlatformType,
        include_progress: bool = False,
    ) -> TrophyGroupsSummary[TrophyGroupSummary] | TrophyGroupsSummary[TrophyGroupSummaryWithProgress]:
        """Retrieves the trophy groups for a title and their respective trophy count.

        This is most commonly seen in games which have expansions where additional trophies are added.

        :param np_communication_id: Unique ID of the title used to request trophy information
        :param platform: The platform this title belongs to.
        :param platform: The platform this title belongs to.
        :param include_progress: If True, will fetch results from another endpoint and include progress for trophy group
            such as name and detail

        .. warning::

            Setting ``include_progress`` to ``True`` will use twice the amount of rate limit since the API wrapper has
            to obtain progress from a separate endpoint.

        :returns: TrophyGroupSummary object containing title and title groups trophy information.

        :raises PSNAWPNotFoundError: If you don't have any trophies for that game.
        :raises PSNAWPForbiddenError: If the user's profile is private.

        """
        if not include_progress:
            return TrophyGroupsSummaryBuilder(
                authenticator=self.authenticator,
                np_communication_id=np_communication_id,
            ).game_title_trophy_groups_summary(platform=platform)
        return TrophyGroupsSummaryBuilder(
            authenticator=self.authenticator,
            np_communication_id=np_communication_id,
        ).earned_user_trophy_groups_summary(
            account_id=self.account_id,
            platform=platform,
        )

    def title_stats(
        self,
        *,
        limit: int | None = None,
        offset: int = 0,
        page_size: int = 200,
    ) -> TitleStatsIterator:
        """Retrieve a list of titles with their stats and basic meta-data.

        :param limit: Limit of titles returned.
        :param page_size: The number of items to receive per api request.
        :param offset: Specifies the offset for paginator.

        .. warning::

            Only returns data for PS4 games and above.

        :returns: Iterator class for TitleStats

        .. code-block:: Python

            user_example = psnawp.user(online_id="jeranther")
            for title in user_example.title_stats():
                ...

        """
        pg_args = PaginationArguments(
            total_limit=limit,
            offset=offset,
            page_size=page_size,
        )
        return TitleStatsIterator.from_endpoint(
            authenticator=self.authenticator,
            account_id=self.account_id,
            pagination_args=pg_args,
        )

    def __repr__(self) -> str:
        """Returns a detailed string representation of the object for debugging."""
        return f"<User online_id:{self.online_id} account_id:{self.account_id}>"

    def __str__(self) -> str:
        """Returns a human-readable summary of the trophy group."""
        return f"Online ID: {self.online_id} Account ID: {self.account_id}"
