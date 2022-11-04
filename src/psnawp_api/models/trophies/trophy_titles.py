from __future__ import annotations

from datetime import datetime
from typing import NamedTuple, Optional, Iterator, Any

from psnawp_api.models.trophies.trophy_set import TrophySet
from psnawp_api.utils.endpoints import BASE_PATH, API_PATH
from psnawp_api.utils.request_builder import RequestBuilder


class TitleTrophySummary(NamedTuple):
    """A class containing summary of trophy data for a user"""

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
    title_platform: list[Optional[str]]
    "Platforms this title belongs to"
    has_trophy_groups: bool
    "True if the title has multiple groups of trophies (eg. DLC trophies which are separate from the main trophy list)"
    progress: int
    "Percentage of trophies earned for the title"
    hidden_flag: bool
    "Title has been hidden on the accounts trophy list (Only for Client)"
    last_updated_date_time: datetime
    "Date most recent trophy earned for the title (UTC+00:00 TimeZone)"
    earned_trophies: TrophySet
    "Number of trophies for the title which have been earned by type"
    defined_trophies: TrophySet
    "Number of trophies for the title by type"


class TrophyTitles:
    def __init__(self, request_builder: RequestBuilder, account_id: str):
        """Retrieve all game titles associated with an account, and a summary of trophies earned from them.

        .. note::

            This class is intended to be interfaced with through PSNAWP.

        :param request_builder: The instance of RequestBuilder. Used to make
            HTTPRequests.
        :type request_builder: RequestBuilder
        :param account_id: The account whose trophy list is being accessed
        :type account_id: str

        """
        self._request_builder = request_builder
        self._account_id = account_id

    def get_title_trophies(self, limit: Optional[int]) -> Iterator[TitleTrophySummary]:
        """Retrieve all game titles associated with an account, and a summary of trophies earned from them.

        :param limit: Limit of titles returned, None means to return all trophy titles.
        :type limit: Optional[int]

        :returns: Generator object with TitleTrophySummary objects
        :rtype: Iterator[TitleTrophySummary]

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
                title_trophy_sum = TitleTrophySummary(
                    np_service_name=trophy_title.get("npServiceName"),
                    np_communication_id=trophy_title.get("npCommunicationId"),
                    trophy_set_version=trophy_title.get("trophySetVersion"),
                    title_name=trophy_title.get("trophyTitleName"),
                    title_detail=trophy_title.get("trophyTitleDetail"),
                    title_icon_url=trophy_title.get("trophyTitleIconUrl"),
                    title_platform=trophy_title.get("trophyTitlePlatform", "").split(
                        ","
                    ),
                    has_trophy_groups=trophy_title.get("hasTrophyGroups", False),
                    progress=trophy_title.get("progress", 0),
                    hidden_flag=trophy_title.get("hiddenFlag", False),
                    last_updated_date_time=datetime.fromisoformat(
                        trophy_title.get(
                            "lastUpdatedDateTime", "1969-12-31T19+00:00"
                        ).replace("Z", "+00:00")
                    ),
                    defined_trophies=TrophySet(
                        **trophy_title.get(
                            "definedTrophies",
                            {"bronze": 0, "silver": 0, "gold": 0, "platinum": 0},
                        )
                    ),
                    earned_trophies=TrophySet(
                        **trophy_title.get(
                            "earnedTrophies",
                            {"bronze": 0, "silver": 0, "gold": 0, "platinum": 0},
                        )
                    ),
                )
                yield title_trophy_sum
                per_page_items += 1

            if limit is not None:
                limit -= per_page_items
                limit_per_request = min(limit, 800)

                # If limit is reached
                if limit <= 0:
                    break

            offset = response.get('nextOffset', 0)
            # If end is reached the end
            if offset <= 0:
                break
