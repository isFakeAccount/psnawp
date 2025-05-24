"""Defines the Trophy class and methods to access individual trophies within a trophy group, such as those from the main game or DLCs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, TypedDict

from typing_extensions import Self, override

from psnawp_api.models.listing import PaginationIterator
from psnawp_api.models.trophies.trophy_utils import (
    trophy_rarity_to_enum,
    trophy_type_str_to_enum,
)
from psnawp_api.utils import iso_format_to_datetime
from psnawp_api.utils.endpoints import API_PATH, BASE_PATH

if TYPE_CHECKING:
    from collections.abc import Generator
    from datetime import datetime

    from psnawp_api.core import Authenticator
    from psnawp_api.models.listing import PaginationArguments
    from psnawp_api.models.trophies.trophy_constants import (
        PlatformType,
        TrophyRarity,
        TrophyType,
    )


@dataclass(frozen=True)
class Trophy:
    """A class that represents a PlayStation Video Game Trophy.

    :var str | None trophy_set_version: The current version of the trophy set.
    :var bool | None has_trophy_groups: True if this title has additional trophy groups.
    :var int | None trophy_id: Unique ID for this trophy.
    :var bool | None trophy_hidden: True if this is a secret trophy (Only for client).
    :var TrophyType | None trophy_type: Type of the trophy.
    :var str | None trophy_name: Name of trophy.
    :var str | None trophy_detail: Description of the trophy.
    :var str | None trophy_icon_url: URL for the graphic associated with the trophy.
    :var str | None trophy_group_id: ID of the trophy group this trophy belongs to.
    :var int | None trophy_progress_target_value: Trophy progress towards it being unlocked (PS5 Only).
    :var str | None trophy_reward_name: Name of the reward earning the trophy grants (PS5 Only).
    :var str | None trophy_reward_img_url: URL for the graphic associated with the reward (PS5 Only).

    To initialize this class, you need the :py:meth:`Trophy.from_trophy_dict`.

    """

    # Trophy Group Metadata
    trophy_set_version: str | None
    has_trophy_groups: bool | None

    # Trophy Meta
    trophy_id: int | None
    trophy_hidden: bool | None
    trophy_type: TrophyType | None
    trophy_name: str | None
    trophy_detail: str | None
    trophy_icon_url: str | None
    trophy_group_id: str | None
    trophy_progress_target_value: int | None
    trophy_reward_name: str | None
    trophy_reward_img_url: str | None

    @classmethod
    def from_trophy_dict(cls, trophy_dict: dict[str, Any]) -> Self:
        """Creates an instance of :py:class:`Trophy` from a dictionary."""
        return cls(
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


@dataclass(frozen=True)
class TrophyWithProgress(Trophy):
    """Earned Trophy Info.

    :var bool | None earned: True if this trophy has been earned.
    :var int | None progress: If the trophy tracks progress towards unlock this is number of steps currently completed
        (ie. 73/300) (PS5 titles only).
    :var int | None progress_rate: If the trophy tracks progress towards unlock this is the current percentage complete
        (PS5 titles only).
    :var datetime.datetime | None progressed_date_time: If the trophy tracks progress towards unlock, and some progress
        has been made, then this returns the date progress was last updated. (PS5 titles only).
    :var datetime.datetime | None earned_date_time: Date trophy was earned.
    :var TrophyRarity | None trophy_rarity: Rarity of the trophy.
    :var float | None trophy_earn_rate: Percentage of all users who have earned the trophy.

    To initialize this class, you need the :py:meth:`TrophyWithProgress.from_trophy_dict`.

    """

    earned: bool | None
    progress: int | None
    progress_rate: int | None
    progressed_date_time: datetime | None
    earned_date_time: datetime | None
    trophy_rarity: TrophyRarity | None
    trophy_earn_rate: float | None

    @classmethod
    def from_trophy_dict(cls, trophy_dict: dict[str, Any]) -> Self:
        """Creates an instance of :py:class:`TrophyWithProgress` from a dictionary."""
        return cls(
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
            progressed_date_time=iso_format_to_datetime(
                trophy_dict.get("progressedDateTime"),
            ),
            earned_date_time=iso_format_to_datetime(trophy_dict.get("earnedDateTime")),
            trophy_rarity=trophy_rarity_to_enum(trophy_dict.get("trophyRare")),
            trophy_earn_rate=trophy_dict.get("trophyEarnedRate"),
        )

    @classmethod
    def from_trophies_list(
        cls,
        trophies_dict: list[dict[str, Any]] | None,
    ) -> list[Trophy]:
        """Creates an list of :py:class:`TrophyWithProgress` from list of dictionaries."""
        trophy_list: list[Trophy] = []
        if trophies_dict is None:
            return trophy_list

        for trophy_dict in trophies_dict:
            trophy_instance = cls.from_trophy_dict(trophy_dict)
            trophy_list.append(trophy_instance)
        return trophy_list


class TrophyIterator(PaginationIterator[Trophy]):
    """Class for Iterating over all trophies for a specified group within a game title.

    To initialize this class, you need the :py:meth:`TrophyIterator.from_endpoint`

    .. note::

        This class is intended to be used via Client or User class. See
        :py:meth:`psnawp_api.models.client.Client.trophies` or :py:meth:`psnawp_api.models.user.User.trophies`.

    """

    def __init__(
        self,
        authenticator: Authenticator,
        url: str,
        pagination_args: PaginationArguments,
        platform: PlatformType,
    ) -> None:
        """Init for TrophyIterator."""
        super().__init__(
            authenticator=authenticator,
            url=url,
            pagination_args=pagination_args,
        )
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
        """Creates an instance of :py:class:`TrophyIterator` from api endpoint."""
        url = f"{BASE_PATH['trophies']}{API_PATH['trophies_for_title'].format(np_communication_id=np_communication_id, trophy_group_id=trophy_group_id)}"
        return cls(authenticator, url, pagination_args, platform)

    @override
    def fetch_next_page(self) -> Generator[Trophy, None, None]:
        """Fetches the next page in endpoint with pagination."""
        service_name = self.platform.get_trophy_service_name()
        params = {
            "npServiceName": service_name,
        } | self._pagination_args.get_params_dict()
        response = self.authenticator.get(url=self._url, params=params).json()
        self._total_item_count = response.get("totalItemCount", 0)

        trophies: list[dict[str, Any]] = response.get("trophies", [])
        for trophy in trophies:
            trophy_instance = Trophy.from_trophy_dict(
                {
                    **trophy,
                    "trophySetVersion": response.get("trophySetVersion"),
                    "hasTrophyGroups": response.get("hasTrophyGroups"),
                },
            )
            self._pagination_args.increment_offset()
            yield trophy_instance

        offset = response.get("nextOffset") or 0
        if offset > 0:
            self._has_next = True
        else:
            self._has_next = False


class RarestTrophies(TypedDict):
    """Represents the rarest trophies in a game title."""

    trophyId: int
    trophyHidden: bool
    earned: bool
    earnedDateTime: str
    trophyType: str
    trophyRare: int
    trophyEarnedRate: str


class TrophyWithProgressIterator(PaginationIterator[TrophyWithProgress]):
    """Class for Iterating over all trophies for a specified group within a game title, this class includes user progress for each trophy.

    To initialize this class, you need the :meth:`TrophyWithProgressIterator.from_endpoint`.

    .. warning::

        Retrieving the progress of Trophies will require double the number of request because the progress has to be
        fetched via separate endpoint.

    .. note::

        This class is intended to be used via Client or User class. See
        :py:meth:`psnawp_api.models.client.Client.trophies` or :py:meth:`psnawp_api.models.user.User.trophies`.

    """

    def __init__(
        self,
        authenticator: Authenticator,
        url: str,
        pagination_args: PaginationArguments,
        platform: PlatformType,
        progress_url: str,
    ) -> None:
        """Init for TrophyWithProgressIterator."""
        super().__init__(
            authenticator=authenticator,
            url=url,
            pagination_args=pagination_args,
        )
        self.platform = platform
        self._progress_url = progress_url

        self.rarest_trophies: list[RarestTrophies] | None = None

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
        """Fetches the next page in endpoint with pagination."""
        url = f"{BASE_PATH['trophies']}{API_PATH['trophies_for_title'].format(np_communication_id=np_communication_id, trophy_group_id=trophy_group_id)}"
        progress_url = (
            f"{BASE_PATH['trophies']}"
            f"{API_PATH['trophies_earned_for_title'].format(account_id=account_id, np_communication_id=np_communication_id, trophy_group_id=trophy_group_id)}"
        )
        return cls(authenticator, url, pagination_args, platform, progress_url)

    @override
    def fetch_next_page(self) -> Generator[TrophyWithProgress, None, None]:
        """Fetches the next page in endpoint with pagination."""
        service_name = self.platform.get_trophy_service_name()
        params = {
            "npServiceName": service_name,
        } | self._pagination_args.get_params_dict()

        response = self.authenticator.get(url=self._url, params=params).json()
        self._total_item_count = response.get("totalItemCount", 0)
        trophies: list[dict[str, Any]] = response.get("trophies")

        response_progress = self.authenticator.get(
            url=self._progress_url,
            params=params,
        ).json()
        self.rarest_trophies = response_progress.get("rarestTrophies")
        trophies_progress: list[dict[str, Any]] = response_progress.get("trophies")

        for trophy, progress in zip(trophies, trophies_progress, strict=False):
            trophy_instance = TrophyWithProgress.from_trophy_dict(
                {
                    **trophy,
                    **progress,
                    "trophySetVersion": response.get("trophySetVersion"),
                    "hasTrophyGroups": response.get("hasTrophyGroups"),
                },
            )
            self._pagination_args.increment_offset()
            yield trophy_instance

        offset = response.get("nextOffset") or 0
        if offset > 0:
            self._has_next = True
        else:
            self._has_next = False
