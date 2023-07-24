from __future__ import annotations

from datetime import datetime
from typing import Optional, Iterator, Any

from attrs import define, field

from psnawp_api.core.psnawp_exceptions import PSNAWPNotFound, PSNAWPBadRequest
from psnawp_api.models.trophies.trophy import Trophy
from psnawp_api.models.trophies.trophy_constants import TrophySet, PlatformType

from psnawp_api.utils.endpoints import BASE_PATH, API_PATH
from psnawp_api.utils.misc import iso_format_to_datetime
from psnawp_api.utils.request_builder import RequestBuilder


@define(frozen=True)
class TrophyTitle:
    """A class containing summary of trophy data for a user for a game title"""

    # Trophy Title Metadata
    total_items_count: Optional[int]
    "The total number of trophy titles for this account"

    np_service_name: Optional[str]
    "trophy for PS3, PS4, or PS Vita platforms and trophy2 for the PS5 platform"
    np_communication_id: Optional[str]
    "Unique ID of the title"
    trophy_set_version: Optional[str]
    "The current version of the trophy set"
    title_name: Optional[str]
    "Title name"
    title_detail: Optional[str]
    "Title description (PS3, PS4 and PS Vita titles only)"
    title_icon_url: Optional[str]
    "URL of the icon for the title"
    title_platform: frozenset[PlatformType]
    "Platforms this title belongs to"
    has_trophy_groups: Optional[bool]
    "True if the title has multiple groups of trophies (eg. DLC trophies which are separate from the main trophy list)"
    progress: Optional[int]
    "Percentage of trophies earned for the title"
    hidden_flag: Optional[bool]
    "Title has been hidden on the accounts trophy list (Only for Client)"
    earned_trophies: TrophySet
    "Number of trophies for the title which have been earned by type"
    defined_trophies: TrophySet
    "Number of trophies for the title by type"
    last_updated_date_time: Optional[datetime] = field(converter=iso_format_to_datetime)
    "Date most recent trophy earned for the title (UTC+00:00 TimeZone)"
    # when title_id is passed
    np_title_id: Optional[str]
    "Title ID of the title if passed"
    rarest_trophies: list[Trophy] = field(factory=list, hash=False)
    "Returns the trophy where earned is true with the lowest trophyEarnedRate"


class TrophyTitles:
    """Retrieve all game titles associated with an account, and a summary of trophies earned from them."""

    def __init__(self, request_builder: RequestBuilder, account_id: str):
        """Constructor of TrophyTitles class.

        .. note::

            This class is intended to be interfaced with through PSNAWP.

        :param request_builder: The instance of RequestBuilder. Used to make HTTPRequests.
        :type request_builder: RequestBuilder
        :param account_id: The account whose trophy list is being accessed
        :type account_id: str

        """
        self._request_builder = request_builder
        self._account_id = account_id

    def get_trophy_titles(self, limit: Optional[int]) -> Iterator[TrophyTitle]:
        """Retrieve all game titles associated with an account, and a summary of trophies earned from them.

        :param limit: Limit of titles returned, None means to return all trophy titles.
        :type limit: Optional[int]

        :returns: Generator object with TitleTrophySummary objects
        :rtype: Iterator[TrophyTitle]

        :raises: ``PSNAWPForbidden`` If the user's profile is private

        """
        offset = 0
        limit_per_request = min(limit, 800) if limit is not None else 800
        while True:
            params = {"limit": limit_per_request, "offset": offset}
            response = self._request_builder.get(
                url=f"{BASE_PATH['trophies']}{API_PATH['trophy_titles'].format(account_id=self._account_id)}",
                params=params,
            ).json()

            per_page_items = 0
            trophy_titles: list[dict[Any, Any]] = response.get("trophyTitles")
            for trophy_title in trophy_titles:
                title_trophy_sum = TrophyTitle(
                    total_items_count=response.get("totalItemCount"),
                    np_service_name=trophy_title.get("npServiceName"),
                    np_communication_id=trophy_title.get("npCommunicationId"),
                    trophy_set_version=trophy_title.get("trophySetVersion"),
                    title_name=trophy_title.get("trophyTitleName"),
                    title_detail=trophy_title.get("trophyTitleDetail"),
                    title_icon_url=trophy_title.get("trophyTitleIconUrl"),
                    title_platform=frozenset(
                        [
                            PlatformType(platform_str) if platform_str else PlatformType("UNKNOWN")
                            for platform_str in trophy_title.get("trophyTitlePlatform", "").split(",")
                        ]
                    ),
                    has_trophy_groups=trophy_title.get("hasTrophyGroups"),
                    progress=trophy_title.get("progress"),
                    hidden_flag=trophy_title.get("hiddenFlag"),
                    last_updated_date_time=trophy_title.get("lastUpdatedDateTime"),
                    defined_trophies=TrophySet(
                        **trophy_title.get(
                            "definedTrophies",
                            {"bronze": 0, "silver": 0, "gold": 0, "platinum": 0},
                        ),
                    ),
                    earned_trophies=TrophySet(
                        **trophy_title.get(
                            "earnedTrophies",
                            {"bronze": 0, "silver": 0, "gold": 0, "platinum": 0},
                        )
                    ),
                    np_title_id=None,
                    rarest_trophies=Trophy.from_trophies_list(trophy_title.get("rarestTrophies")),
                )
                yield title_trophy_sum
                per_page_items += 1

            if limit is not None:
                limit -= per_page_items
                limit_per_request = min(limit, 800)

                # If limit is reached
                if limit <= 0:
                    break

            offset = response.get("nextOffset", 0)
            # If end is reached the end
            if offset <= 0:
                break

    def get_trophy_summary_for_title(self, title_ids: list[str]) -> Iterator[TrophyTitle]:
        """Retrieve a summary of the trophies earned by a user for specific titles.

        :param title_ids: Unique ID of the title
        :type title_ids: list[str]

        :returns: Generator object with TitleTrophySummary objects
        :rtype: Iterator[TrophyTitle]

        :raises: ``PSNAWPForbidden`` If the user's profile is private

        """
        params = {"npTitleIds": ",".join(title_ids)}
        response = self._request_builder.get(
            url=f"{BASE_PATH['trophies']}{API_PATH['trophy_titles_for_title'].format(account_id=self._account_id)}",
            params=params,
        ).json()

        for title in response.get("titles"):
            for trophy_title in title.get("trophyTitles"):
                title_trophy_sum = TrophyTitle(
                    total_items_count=response.get("totalItemCount"),
                    np_service_name=trophy_title.get("npServiceName"),
                    np_communication_id=trophy_title.get("npCommunicationId"),
                    trophy_set_version=trophy_title.get("trophySetVersion"),
                    title_name=trophy_title.get("trophyTitleName"),
                    title_detail=trophy_title.get("trophyTitleDetail"),
                    title_icon_url=trophy_title.get("trophyTitleIconUrl"),
                    title_platform=frozenset(
                        [
                            PlatformType(platform_str) if platform_str else PlatformType("UNKNOWN")
                            for platform_str in trophy_title.get("trophyTitlePlatform", "").split(",")
                        ]
                    ),
                    has_trophy_groups=trophy_title.get("hasTrophyGroups"),
                    progress=trophy_title.get("progress"),
                    hidden_flag=trophy_title.get("hiddenFlag"),
                    last_updated_date_time=trophy_title.get("lastUpdatedDateTime"),
                    defined_trophies=trophy_title.get(
                        "definedTrophies",
                        {"bronze": 0, "silver": 0, "gold": 0, "platinum": 0},
                    ),
                    earned_trophies=trophy_title.get(
                        "earnedTrophies",
                        {"bronze": 0, "silver": 0, "gold": 0, "platinum": 0},
                    ),
                    np_title_id=title.get("npTitleId"),
                    rarest_trophies=Trophy.from_trophies_list(trophy_title.get("rarestTrophies")),
                )
                yield title_trophy_sum

    @staticmethod
    def get_np_communication_id(request_builder: RequestBuilder, title_id: str, account_id: str) -> str:
        """Returns the np communication id of title. This is required for requesting detail about a titles trophies.

        .. note::

            The endpoint only returns useful response back if the account has played that particular video game.

        :param request_builder: The instance of RequestBuilder. Used to make HTTPRequests.
        :type request_builder: RequestBuilder
        :param title_id: Unique ID of the title
        :type title_id: str
        :param account_id: Account ID of the user.
        :type account_id: str

        :returns: np communication id of title
        :rtype: str

        :raises: ``PSNAWPNotFound`` If the user does not have any trophies for that game or the game doesn't exist.

        """
        params = {"npTitleIds": f"{title_id},"}

        try:
            response = request_builder.get(
                url=f"{BASE_PATH['trophies']}{API_PATH['trophy_titles_for_title'].format(account_id=account_id)}",
                params=params,
            ).json()
        except (PSNAWPBadRequest, PSNAWPNotFound) as bad_req:
            raise PSNAWPNotFound(f"Could not find a Video Game with Title: {title_id}") from bad_req

        if len(response.get("titles")[0].get("trophyTitles")) == 0:
            raise PSNAWPNotFound(f"Could not find a Video Game with Title: {title_id}. Most likely the user doesn't own the game.")

        np_comm_id: str = response.get("titles")[0].get("trophyTitles")[0].get("npCommunicationId", title_id)
        return np_comm_id
