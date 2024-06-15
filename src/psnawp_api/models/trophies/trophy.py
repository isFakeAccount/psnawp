from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any, Generator, Optional, TypedDict

from typing_extensions import Self

from psnawp_api.models.listing import PaginationIterator
from psnawp_api.models.trophies.trophy_constants import PlatformType, TrophyRarity, TrophyType
from psnawp_api.models.trophies.utility_functions import (
    trophy_rarity_to_enum,
    trophy_type_str_to_enum,
)
from psnawp_api.utils import iso_format_to_datetime
from psnawp_api.utils.endpoints import API_PATH, BASE_PATH

if TYPE_CHECKING:
    from psnawp_api.core import Authenticator
    from psnawp_api.models.listing import PaginationArguments


@dataclass(frozen=True)
class Trophy:
    """A class that represents a PlayStation Video Game Trophy."""

    # Trophy Group Metadata
    trophy_set_version: Optional[str]
    "The current version of the trophy set"
    has_trophy_groups: Optional[bool]
    "True if this title has additional trophy groups"

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

    @classmethod
    def from_trophy_dict(cls, trophy_dict: dict[str, Any]) -> Self:
        trophy_instance = cls(
            trophy_set_version=trophy_dict.get("trophySetVersion"),
            has_trophy_groups=trophy_dict.get("hasTrophyGroups"),
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
        )
        return trophy_instance


@dataclass(frozen=True)
class TrophyWithProgress(Trophy):
    # Earned Trophy Info
    earned: Optional[bool]
    "True if this trophy has been earned"
    progress: Optional[int]
    "If the trophy tracks progress towards unlock this is number of steps currently completed (ie. 73/300) (PS5 titles only)"
    progress_rate: Optional[int]
    "If the trophy tracks progress towards unlock this is the current percentage complete (PS5 titles only)"
    progressed_date_time: Optional[datetime]
    "If the trophy tracks progress towards unlock, and some progress has been made, then this returns the date progress was last updated. (PS5 titles only)"
    earned_date_time: Optional[datetime]
    "Date trophy was earned"
    trophy_rarity: Optional[TrophyRarity]
    "Rarity of the trophy"
    trophy_earn_rate: Optional[float]
    "Percentage of all users who have earned the trophy"

    @classmethod
    def from_trophy_dict(cls, trophy_dict: dict[str, Any]) -> Self:
        trophy_instance = cls(
            trophy_set_version=trophy_dict.get("trophySetVersion"),
            has_trophy_groups=trophy_dict.get("hasTrophyGroups"),
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
            progressed_date_time=iso_format_to_datetime(trophy_dict.get("progressedDateTime")),
            earned_date_time=iso_format_to_datetime(trophy_dict.get("earnedDateTime")),
            trophy_rarity=trophy_rarity_to_enum(trophy_dict.get("trophyRare")),
            trophy_earn_rate=trophy_dict.get("trophyEarnedRate"),
        )
        return trophy_instance

    @classmethod
    def from_trophies_list(cls, trophies_dict: Optional[list[dict[str, Any]]]) -> list[Trophy]:
        trophy_list: list[Trophy] = []
        if trophies_dict is None:
            return trophy_list

        for trophy_dict in trophies_dict:
            trophy_instance = cls.from_trophy_dict(trophy_dict)
            trophy_list.append(trophy_instance)
        return trophy_list


class TrophyIterator(PaginationIterator[Trophy]):
    """Class for Iterating over all trophies for a specified group within a game title."""

    def __init__(
        self,
        authenticator: Authenticator,
        url: str,
        pagination_args: PaginationArguments,
        platform: PlatformType,
    ) -> None:
        super().__init__(authenticator=authenticator, url=url, pagination_args=pagination_args)
        self.platform = platform

    @classmethod
    def from_endpoint(
        cls,
        authenticator: Authenticator,
        pagination_args: PaginationArguments,
        np_communication_id: str,
        platform: PlatformType,
        trophy_group_id: str,
    ) -> Self:
        url = f"{BASE_PATH['trophies']}{API_PATH['trophies_for_title'].format(np_communication_id=np_communication_id, trophy_group_id=trophy_group_id)}"
        return cls(authenticator, url, pagination_args, platform)

    def fetch_next_page(self) -> Generator[Trophy, None, None]:
        service_name = "trophy2" if self.platform == PlatformType.PS5 else "trophy"
        params = {"npServiceName": service_name} | self._pagination_args.get_params_dict()
        response = self.authenticator.get(url=self._url, params=params).json()
        self._total_item_count = response.get("totalItemCount", 0)

        trophies: list[dict[str, Any]] = response.get("trophies", [])
        for trophy in trophies:
            trophy_instance = Trophy.from_trophy_dict(
                {
                    **trophy,
                    "trophySetVersion": response.get("trophySetVersion"),
                    "hasTrophyGroups": response.get("hasTrophyGroups"),
                }
            )
            self._pagination_args.increment_offset()
            yield trophy_instance

        offset = response.get("nextOffset") or 0
        if offset > 0:
            self._has_next = True
        else:
            self._has_next = False


class RarestTrophies(TypedDict):
    trophyId: int
    trophyHidden: bool
    earned: bool
    earnedDateTime: str
    trophyType: str
    trophyRare: int
    trophyEarnedRate: str


class TrophyWithProgressIterator(PaginationIterator[TrophyWithProgress]):
    """Class for Iterating over all trophies for a specified group within a game title, this class includes user progress for each trophy."""

    def __init__(
        self,
        authenticator: Authenticator,
        url: str,
        pagination_args: PaginationArguments,
        platform: PlatformType,
        progress_url: str,
    ) -> None:
        super().__init__(authenticator=authenticator, url=url, pagination_args=pagination_args)
        self.platform = platform
        self._progress_url = progress_url

        self.rarest_trophies: Optional[list[RarestTrophies]] = None

    @classmethod
    def from_endpoint(
        cls,
        authenticator: Authenticator,
        pagination_args: PaginationArguments,
        np_communication_id: str,
        platform: PlatformType,
        trophy_group_id: str,
        account_id: str,
    ) -> Self:
        url = f"{BASE_PATH['trophies']}{API_PATH['trophies_for_title'].format(np_communication_id=np_communication_id, trophy_group_id=trophy_group_id)}"
        progress_url = (
            f"{BASE_PATH['trophies']}"
            f"{API_PATH['trophies_earned_for_title'].format(account_id=account_id, np_communication_id=np_communication_id, trophy_group_id=trophy_group_id)}"
        )
        return cls(authenticator, url, pagination_args, platform, progress_url)

    def fetch_next_page(self) -> Generator[TrophyWithProgress, None, None]:
        service_name = "trophy2" if self.platform == PlatformType.PS5 else "trophy"
        params = {"npServiceName": service_name} | self._pagination_args.get_params_dict()

        response = self.authenticator.get(url=self._url, params=params).json()
        self._total_item_count = response.get("totalItemCount", 0)
        trophies: list[dict[str, Any]] = response.get("trophies")

        response_progress = self.authenticator.get(url=self._progress_url, params=params).json()
        self.rarest_trophies = response_progress.get("rarestTrophies")
        trophies_progress: list[dict[str, Any]] = response_progress.get("trophies")

        for trophy, progress in zip(trophies, trophies_progress):
            trophy_instance = TrophyWithProgress.from_trophy_dict(
                {
                    **trophy,
                    **progress,
                    "trophySetVersion": response.get("trophySetVersion"),
                    "hasTrophyGroups": response.get("hasTrophyGroups"),
                }
            )
            self._pagination_args.increment_offset()
            yield trophy_instance

        offset = response.get("nextOffset") or 0
        if offset > 0:
            self._has_next = True
        else:
            self._has_next = False
