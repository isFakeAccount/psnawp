from __future__ import annotations

from datetime import datetime
from typing import Optional, Literal, Iterator, Any

from attrs import define

from psnawp_api.models.trophies.trophy_constants import TrophyType, TrophyRarity
from psnawp_api.models.trophies.utility_functions import (
    trophy_type_str_to_enum,
    iso_format_to_datetime,
    trophy_rarity_to_enum,
)
from psnawp_api.utils.endpoints import BASE_PATH, API_PATH
from psnawp_api.utils.request_builder import RequestBuilder


@define(frozen=True)
class Trophy:
    """A class that represents a PlayStation Video Game Trophy."""

    # Trophy Meta
    trophy_id: Optional[int]
    "Unique ID for this trophy"
    trophy_hidden: Optional[bool]
    "True if this is a secret trophy (Only for client)"
    trophy_type: Optional[TrophyType]
    "Type of the trophy"
    trophy_name: Optional[str]
    "Name of trophy"
    trophy_detail: Optional[str]
    "Description of the trophy"
    trophy_icon_url: Optional[str]
    "URL for the graphic associated with the trophy"
    trophy_group_id: Optional[str]
    "ID of the trophy group this trophy belongs to"
    trophy_progress_target_value: Optional[int]
    "Trophy progress towards it being unlocked (PS5 Only)"
    trophy_reward_name: Optional[str]
    "Name of the reward earning the trophy grants (PS5 Only)"
    trophy_reward_img_url: Optional[str]
    "URL for the graphic associated with the reward (PS5 Only)"

    # Earned Trophy Info
    earned: Optional[bool]
    "True if this trophy has been earned"
    progress: Optional[int]
    "If the trophy tracks progress towards unlock this is number of steps currently completed (ie. 73/300) (PS5 titles only)"
    progress_rate: Optional[int]
    "If the trophy tracks progress towards unlock this is the current percentage complete (PS5 titles only)"
    progressed_date_time: datetime
    "If the trophy tracks progress towards unlock, and some progress has been made, then this returns the date progress was last updated. (PS5 titles only)"
    earned_date_time: datetime
    "Date trophy was earned"
    trophy_rarity: Optional[TrophyRarity]
    "Rarity of the trophy"
    trophy_earn_rate: Optional[float]
    "Percentage of all users who have earned the trophy"

    @classmethod
    def from_trophy_dict(cls, trophy_dict: dict[str, Any]) -> Trophy:
        trophy_instance = cls(
            trophy_id=trophy_dict.get("trophyId"),
            trophy_hidden=trophy_dict.get("trophyHidden"),
            trophy_type=trophy_type_str_to_enum(trophy_dict.get("trophyType")),
            trophy_name=trophy_dict.get("trophyName"),
            trophy_detail=trophy_dict.get("trophyDetail"),
            trophy_icon_url=trophy_dict.get("trophyIconUrl"),
            trophy_group_id=trophy_dict.get("trophyGroupId"),
            trophy_progress_target_value=trophy_dict.get("trophyProgressTargetValue"),
            trophy_reward_name=trophy_dict.get("trophyRewardName"),
            trophy_reward_img_url=trophy_dict.get("trophyRewardImageUrl"),
            earned=trophy_dict.get("earned"),
            progress=trophy_dict.get("progress"),
            progress_rate=trophy_dict.get("progressRate"),
            progressed_date_time=iso_format_to_datetime(
                trophy_dict.get("progressedDateTime")
            ),
            earned_date_time=iso_format_to_datetime(trophy_dict.get("earnedDateTime")),
            trophy_rarity=trophy_rarity_to_enum(trophy_dict.get("trophyRare")),
            trophy_earn_rate=trophy_dict.get("trophyEarnedRate"),
        )
        return trophy_instance

    @classmethod
    def from_trophies_list(
        cls, trophies_dict: Optional[list[dict[str, Any]]]
    ) -> list[Trophy]:
        trophy_list: list[Trophy] = []
        if trophies_dict is None:
            return trophy_list

        for trophy_dict in trophies_dict:
            trophy_instance = cls.from_trophy_dict(trophy_dict)
            trophy_list.append(trophy_instance)
        return trophy_list


def _get_trophy_from_endpoint(
    endpoint: str,
    request_builder: RequestBuilder,
    platform: Literal["PS Vita", "PS3", "PS4", "PS5"],
    limit: Optional[int] = None,
) -> Iterator[Trophy]:
    offset = 0
    service_name = "trophy2" if platform == "PS5" else "trophy"
    params: dict[str, str | int] = {"npServiceName": service_name}
    limit_per_request = 400
    if limit is not None:
        params |= {"limit": min(limit, limit_per_request), "offset": offset}

    while True:
        if limit is not None:
            params["limit"] = min(limit, limit_per_request)
        response = request_builder.get(
            url=f"{BASE_PATH['trophies']}{endpoint}",
            params=params,
        ).json()

        per_page_items = 0
        trophies: list[dict[str, Any]] = response.get("trophies")
        for trophy in trophies:
            trophy_instance = Trophy.from_trophy_dict(trophy)
            yield trophy_instance
            per_page_items += 1

        if limit is not None:
            limit -= per_page_items
            limit_per_request = min(limit, 400)

            # If limit is reached
            if limit <= 0:
                break

        offset = response.get("nextOffset", 0)
        # If end is reached the end
        if offset <= 0:
            break


class TrophyBuilder:
    """Class for providing convenient methods to Build Trophy from PlayStation Endpoints"""

    def __init__(self, request_builder: RequestBuilder, np_communication_id: str):
        """Constructor for class TrophyBuilder.

        :param request_builder: The instance of RequestBuilder. Used to make
            HTTPRequests.
        :type request_builder: RequestBuilder
        :param np_communication_id: Unique ID of a game title used to request trophy
            information. This can be obtained from ``GameTitle`` class.
        :type np_communication_id: str

        """
        self._request_builder = request_builder
        self.np_communication_id: str = np_communication_id

    def game_trophies(
        self,
        platform: Literal["PS Vita", "PS3", "PS4", "PS5"],
        trophy_group_id: str = "default",
        limit: Optional[int] = None,
    ) -> Iterator[Trophy]:
        """Retrieves the individual trophy detail of a single - or all - trophy groups for a title.

        :param platform: The platform this title belongs to.
        :type platform: Literal
        :param trophy_group_id: ID for the trophy group (all titles have default,
            additional groups are 001 incrementing)
        :type trophy_group_id: str
        :param limit: Limit of trophies returned, None means to return all trophy
            titles.
        :type limit: Optional[int]

        :returns: Returns the Trophy Generator object with all the information
        :rtype: Iterator[Trophy]

        """
        return _get_trophy_from_endpoint(
            API_PATH["trophies_for_title"].format(
                np_communication_id=self.np_communication_id,
                trophy_group_id=trophy_group_id,
            ),
            self._request_builder,
            platform,
            limit,
        )

    def earned_game_trophies(
        self,
        account_id: str,
        platform: Literal["PS Vita", "PS3", "PS4", "PS5"],
        trophy_group_id: str = "default",
        limit: Optional[int] = None,
    ) -> Iterator[Trophy]:
        """Retrieves the earned status individual trophy detail of a single - or all - trophy groups for a title.

        :param account_id: The account whose trophy list is being accessed.
        :type account_id: str
        :param platform: The platform this title belongs to.
        :type platform: Literal
        :param trophy_group_id: ID for the trophy group (all titles have default,
            additional groups are 001 incrementing)
        :type trophy_group_id: str
        :param limit: Limit of trophies returned, None means to return all trophy
            titles.
        :type limit: Optional[int]

        :returns: Returns the Trophy Generator object with all the information
        :rtype: Iterator[Trophy]

        """
        return _get_trophy_from_endpoint(
            API_PATH["trophies_earned_for_title"].format(
                account_id=account_id,
                np_communication_id=self.np_communication_id,
                trophy_group_id=trophy_group_id,
            ),
            self._request_builder,
            platform,
            limit,
        )

    def earned_game_trophies_with_metadata(
        self,
        account_id: str,
        platform: Literal["PS Vita", "PS3", "PS4", "PS5"],
        trophy_group_id: str = "default",
        limit: Optional[int] = None,
    ) -> Iterator[Trophy]:
        """Retrieves the earned status with metadata of individual trophy detail of a single - or all - trophy groups for a title.

        :param account_id: The account whose trophy list is being accessed.
        :type account_id: str
        :param platform: The platform this title belongs to.
        :type platform: Literal
        :param trophy_group_id: ID for the trophy group (all titles have default,
            additional groups are 001 incrementing)
        :type trophy_group_id: str
        :param limit: Limit of trophies returned, None means to return all trophy
            titles.
        :type limit: Optional[int]

        :returns: Returns the Trophy Generator object with all the information
        :rtype: Iterator[Trophy]

        """
        trophy_metadata = _get_trophy_from_endpoint(
            API_PATH["trophies_for_title"].format(
                np_communication_id=self.np_communication_id,
                trophy_group_id=trophy_group_id,
            ),
            self._request_builder,
            platform,
            limit,
        )
        trophy_earned_status = _get_trophy_from_endpoint(
            API_PATH["trophies_earned_for_title"].format(
                account_id=account_id,
                np_communication_id=self.np_communication_id,
                trophy_group_id=trophy_group_id,
            ),
            self._request_builder,
            platform,
            limit,
        )

        for combined_data in zip(trophy_metadata, trophy_earned_status):
            combined_data_dict = {}
            for key in dir(combined_data[0]):
                if key.startswith("_") or key.startswith("from"):
                    continue
                elif "time" in key:
                    combined_data_dict[key] = getattr(combined_data[1], key)
                else:
                    combined_data_dict[key] = getattr(combined_data[0], key) or getattr(
                        combined_data[1], key
                    )
            trophy_instance = Trophy(**combined_data_dict)
            yield trophy_instance
