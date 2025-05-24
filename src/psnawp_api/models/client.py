"""Provides Class Client representing the logged in user."""

from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Any, Literal, overload

from psnawp_api.models.game_entitlements import GameEntitlementsIterator
from psnawp_api.models.group.group import Group
from psnawp_api.models.listing import PaginationArguments
from psnawp_api.models.title_stats import TitleStatsIterator
from psnawp_api.models.trophies import (
    TrophyGroupsSummaryBuilder,
    TrophyIterator,
    TrophySummary,
    TrophyTitleIterator,
    TrophyWithProgressIterator,
)
from psnawp_api.models.user import User
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


class Client:
    """The Client class provides the information and methods for the currently authenticated user.

    :var Authenticator authenticator: An instance of :py:class:`~psnawp_api.core.authenticator.Authenticator` used to
        authenticate and make HTTPS requests.

    .. note::

        This class is intended to be used via PSNAWP. See :py:meth:`psnawp_api.psnawp.PSNAWP.me`

    """

    def __init__(self, authenticator: Authenticator) -> None:
        """Initialize a Client instance.

        :param authenticator: The Authenticator instance used for making authenticated requests to the API.

        """
        self.authenticator = authenticator

    @cached_property
    def online_id(self) -> str:
        """Gets the online ID of the client logged in the api.

        :returns: online ID of logged in user.

        .. code-block:: Python

            client = psnawp.me()
            print(client.online_id)

        """
        response = self.authenticator.get(
            url=f"{BASE_PATH['profile_uri']}{API_PATH['profiles'].format(account_id=self.account_id)}",
        ).json()
        online_id: str = response["onlineId"]
        return online_id

    @cached_property
    def account_id(self) -> str:
        """Gets the account ID of the client logged in the api.

        :returns: account ID of logged in user.

        .. code-block:: Python

            client = psnawp.me()
            print(client.account_id)

        """
        response = self.authenticator.get(
            url=f"{BASE_PATH['account_uri']}{API_PATH['my_account']}",
        ).json()
        account_id: str = response["accountId"]
        return account_id

    def get_region(self) -> Country | None:
        """Gets the region of the client logged in the api.

        :returns: Returns Country object from Pycountry for logged in user or None if not found.

        .. code-block:: Python

            client = psnawp.me()
            print(client.get_region())

        .. note::

            See https://github.com/pycountry/pycountry for more info on Country object.

        """
        response = self.get_profile_legacy()
        npid = response.get("profile", {}).get("npId", "")
        return extract_region_from_npid(npid)

    def get_profile_legacy(self) -> dict[str, Any]:
        """Gets the profile info from legacy api endpoint. Useful for legacy console (PS3, PS4) presence.

        :returns: A dict containing info similar to what is shown below:

            .. literalinclude:: ../examples/client/get_profile_legacy.json
                :language: json


        .. code-block:: Python

            client = psnawp.me()
            print(client.get_profile_legacy())

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

    def get_account_devices(self) -> list[dict[str, Any]]:
        """Gets the list of devices the client is logged into.

        :returns: A dict containing info similar to what is shown below:

            .. literalinclude:: ../examples/client/get_account_devices.json
                :language: json


        .. code-block:: Python

            client = psnawp.me()
            print(client.get_account_devices())

        """
        params = {
            "includeFields": "device,systemData",
            "platform": "PS5,PS4,PS3,PSVita",
        }
        response = self.authenticator.get(
            url=f"{BASE_PATH['account_uri']}{API_PATH['my_account']}",
            params=params,
        ).json()

        # Just so mypy doesn't complain
        account_devices: list[dict[str, Any]] = response.get("accountDevices", [])
        return account_devices

    def friends_list(self, limit: int = 1000) -> Generator[User, None, None]:
        """Gets the friends list and returns an iterator of User objects.

        :param limit: The number of items from input max is 1000.

        :returns: All friends in your friends list.

        .. code-block:: Python

            client = psnawp.me()
            friends_list = client.friends_list()

            for friend in friends_list:
                ...

        """
        limit = min(1000, limit)

        params = {"limit": limit}
        response = self.authenticator.get(
            url=f"{BASE_PATH['profile_uri']}{API_PATH['friends_list'].format(account_id='me')}",
            params=params,
        ).json()
        return (
            User.from_account_id(
                authenticator=self.authenticator,
                account_id=account_id,
            )
            for account_id in response["friends"]
        )

    def friend_requests(self) -> Generator[User, None, None]:
        """Get the friend request list and returns Generator of received requests.

        :returns: All your friend requests.

        """
        response = self.authenticator.get(
            url=f"{BASE_PATH['profile_uri']}{API_PATH['friends_request'].format(account_id='me')}",
        ).json()
        return (
            User.from_account_id(
                authenticator=self.authenticator,
                account_id=request["accountId"],
            )
            for request in response["receivedRequests"]
        )

    def get_presences(self, account_ids: list[str]) -> dict[str, Any]:
        """Gets the presences all the account Ids passed as param.

        :returns: A dict containing info similar to what is shown below:

            .. literalinclude:: ../examples/client/get_presences.json
                :language: json


        .. code-block:: Python

            client = psnawp.me()
            print(client.get_presences())

        """
        params = {
            "type": "primary",
            "accountIds": ",".join(account_ids),
            "platforms": "PS4,PS5,MOBILE_APP,PSPC",
            "withOwnGameTitleInfo": "true",
        }
        response: dict[str, Any] = self.authenticator.get(
            url=f"{BASE_PATH['profile_uri_v2']}/{API_PATH['basic_presences']}",
            params=params,
        ).json()
        return response

    def available_to_play(self) -> Generator[User, None, None]:
        """Gets the list of users on your "Notify when available" subscription list.

        :returns: Iterator of user objects.

        .. code-block:: Python

            client = psnawp.me()
            available_to_play = client.available_to_play()

            for user in available_to_play:
                ...

        """
        response = self.authenticator.get(
            url=f"{BASE_PATH['profile_uri']}{API_PATH['available_to_play']}",
        ).json()
        return (
            User.from_account_id(
                authenticator=self.authenticator,
                account_id=account_id_dict["accountId"],
            )
            for account_id_dict in response["settings"]
        )

    def blocked_list(self) -> Generator[User, None, None]:
        """Gets the blocked list and return their account ids.

        :returns: Al blocked users on your block list.

        .. code-block:: Python

            client = psnawp.me()
            blocked_list = client.blocked_list()

            for blocked_users in blocked_list:
                ...

        """
        response = self.authenticator.get(
            url=f"{BASE_PATH['profile_uri']}{API_PATH['blocked_users']}",
        ).json()
        return (
            User.from_account_id(
                authenticator=self.authenticator,
                account_id=account_id,
            )
            for account_id in response["blockList"]
        )

    def get_shareable_profile_link(self) -> dict[str, str]:
        """Gets the shareable link and QR code for the PlayStation profile.

        This method fetches the URL that can be used to easily share the user's PlayStation profile. Additionally, it
        provides a QR code image URL that corresponds to the shareable URL.

        :returns: A dict containing info similar to what is shown below:

            .. literalinclude:: ../examples/client/shareable_profile.json
                :language: json


        .. code-block:: Python

            client = psnawp.me()
            print(client.get_shareable_profile_link())

        """
        response: dict[str, str] = self.authenticator.get(
            url=f"{BASE_PATH['cpss']}{API_PATH['share_profile'].format(account_id=self.account_id)}",
        ).json()
        return response

    def get_groups(
        self,
        limit: int = 200,
        offset: int = 0,
    ) -> Generator[Group, None, None]:
        """Gets all the groups you have participated in.

        :param limit: The number of groups to receive.
        :param offset: Lets you exclude first N items groups. Offset = 10 lets you skip the first 10 groups.

        :returns: Generator of Group Objects.

        """
        param: dict[str, str | int] = {
            "includeFields": "members",
            "limit": limit,
            "offset": offset,
        }

        response = self.authenticator.get(
            url=f"{BASE_PATH['gaming_lounge']}{API_PATH['my_groups']}",
            params=param,
        ).json()

        return (
            Group.create_from_group_id(
                authenticator=self.authenticator,
                group_id=group_info["groupId"],
            )
            for group_info in response["groups"]
        )

    def trophy_summary(self) -> TrophySummary:
        """Retrieve an overall summary of the number of trophies earned for a user broken down by.

        - type
        - overall trophy level
        - progress towards the next level
        - current tier

        :returns: Trophy Summary Object containing all information

        .. code-block:: Python

            client = psnawp.me()
            print(client.trophy_summary())

        """
        return TrophySummary.from_endpoint(
            authenticator=self.authenticator,
            account_id="me",
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
            account_id="me",
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
            account_id="me",
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
            account_id="me",
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
        ).earned_user_trophy_groups_summary(account_id="me", platform=platform)

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
        :param offset: Specifies the offset for paginator

        .. important::

            Only returns data for PS4 games and above.

        :returns: Iterator class for TitleStats

        .. code-block:: Python

            user_example = psnawp.client()
            titles = list(user_example.title_stats())

        """
        pg_args = PaginationArguments(
            total_limit=limit,
            offset=offset,
            page_size=page_size,
        )
        return TitleStatsIterator.from_endpoint(
            authenticator=self.authenticator,
            account_id="me",
            pagination_args=pg_args,
        )

    def game_entitlements(
        self,
        limit: int | None = None,
        offset: int = 0,
        page_size: int = 20,
        title_ids: list[str] | None = None,
    ) -> GameEntitlementsIterator:
        """Returns an iterator for retrieving game entitlements (owned titles) associated with the authenticated client.

        .. note::

            This class retrieves only PS4 and PS5 game entitlements, as the underlying API endpoints accessed via the
            PlayStation Android app are limited to these platforms.

        :param limit: Limit of titles returned.
        :param page_size: The number of items to receive per api request.
        :param offset: Specifies the offset for paginator.
        :param title_ids: Filter by a specific game title IDs to check if the client owns it.

        :returns: Iterator class GameEntitlementsIterator

        """
        pg_args = PaginationArguments(
            total_limit=limit,
            offset=offset,
            page_size=page_size,
        )

        title_ids_str = "" if title_ids is None else ",".join(title_ids)
        return GameEntitlementsIterator.from_endpoint(authenticator=self.authenticator, pagination_args=pg_args, title_ids=title_ids_str)

    def __repr__(self) -> str:
        """Returns a detailed string representation of the object for debugging."""
        return f"<Client online_id:{self.online_id} account_id:{self.account_id}>"

    def __str__(self) -> str:
        """Returns a human-readable summary of the trophy group."""
        return f"Online ID: {self.online_id} Account ID: {self.account_id}"
