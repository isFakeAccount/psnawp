from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Generic, Optional, TypeVar

from attrs import define, field
from typing_extensions import Self

from psnawp_api.core import PSNAWPNotFound
from psnawp_api.models.trophies import PlatformType, TrophySet
from psnawp_api.utils import API_PATH, BASE_PATH, iso_format_to_datetime

if TYPE_CHECKING:
    from psnawp_api.core import Authenticator


@define(frozen=True)
class TrophyGroupSummary:
    """TrophyGroupSummary contains trophy count data for one trophy group of a game title."""

    trophy_group_id: Optional[str]
    "ID for the trophy group (all titles have default, additional groups are 001 incrementing)"
    trophy_group_name: Optional[str]
    "Trophy group name"
    trophy_group_detail: Optional[str]
    "Trophy group description (PS3, PS4 and PS Vita titles only)"
    trophy_group_icon_url: Optional[str]
    "URL of the icon for the trophy group"
    defined_trophies: TrophySet
    "Number of trophies for the trophy group by type"

    @classmethod
    def from_dict(cls, trophy_group_dict: dict[str, Any]) -> Self:
        return cls(
            trophy_group_id=trophy_group_dict.get("trophyGroupId"),
            trophy_group_name=trophy_group_dict.get("trophyGroupName"),
            trophy_group_detail=trophy_group_dict.get("trophyGroupDetail"),
            trophy_group_icon_url=trophy_group_dict.get("trophyGroupIconUrl"),
            defined_trophies=TrophySet(
                **trophy_group_dict.get(
                    "definedTrophies",
                    {"bronze": 0, "silver": 0, "gold": 0, "platinum": 0},
                )
            ),
        )


@define(frozen=True)
class TrophyGroupSummaryWithProgress(TrophyGroupSummary):
    """TrophyGroupSummaryWithProgress contains trophy count data for one trophy group of a game title and user progress for each trophy group."""

    progress: Optional[int]
    "Percentage of trophies earned for group"
    earned_trophies: TrophySet
    "Number of trophies for the group which have been earned by type"
    last_updated_datetime: Optional[datetime] = field(converter=iso_format_to_datetime)
    "Date most recent trophy earned for the group"

    @classmethod
    def from_dict(cls, trophy_group_dict: dict[str, Any]) -> Self:
        return cls(
            trophy_group_id=trophy_group_dict.get("trophyGroupId"),
            trophy_group_name=trophy_group_dict.get("trophyGroupName"),
            trophy_group_detail=trophy_group_dict.get("trophyGroupDetail"),
            trophy_group_icon_url=trophy_group_dict.get("trophyGroupIconUrl"),
            defined_trophies=TrophySet(
                **trophy_group_dict.get(
                    "definedTrophies",
                    {"bronze": 0, "silver": 0, "gold": 0, "platinum": 0},
                )
            ),
            progress=trophy_group_dict.get("progress"),
            earned_trophies=TrophySet(
                **trophy_group_dict.get(
                    "earnedTrophies",
                    {"bronze": 0, "silver": 0, "gold": 0, "platinum": 0},
                )
            ),
            last_updated_datetime=trophy_group_dict.get("lastUpdatedDateTime"),
        )


T = TypeVar("T", bound=TrophyGroupSummary)


class TrophyGroupsSummary(Generic[T]):
    """TrophyGroupsSummary contains trophy count data for all the groups in a game title combined and individual."""

    def __init__(
        self,
        trophy_set_version: Optional[str],
        trophy_title_name: Optional[str],
        trophy_title_detail: Optional[str],
        trophy_title_icon_url: Optional[str],
        trophy_title_platform: set[PlatformType],
        defined_trophies: TrophySet,
        trophy_groups: list[T],
        hidden_flag: Optional[bool],
        progress: Optional[int],
        earned_trophies: TrophySet,
        last_updated_date_time: Optional[str],
    ) -> None:
        self.trophy_set_version = trophy_set_version
        "The current version of the trophy set"
        self.trophy_title_name = trophy_title_name
        "Title name"
        self.trophy_title_detail = trophy_title_detail
        "Title description (PS3, PS4 and PS Vita titles only)"
        self.trophy_title_icon_url = trophy_title_icon_url
        "URL of the icon for the trophy title"
        self.trophy_title_platform = trophy_title_platform
        "The platform this title belongs to"
        self.defined_trophies = defined_trophies
        "Total number of trophies for the title by type"
        self.trophy_groups = trophy_groups
        "Individual object for each trophy group returned"
        self.hidden_flag = hidden_flag
        "Whether title has been hidden on the accounts trophy list (Authenticating account only)"
        self.progress = progress
        "Percentage of trophies earned for the title"
        self.earned_trophies = earned_trophies
        "Number of trophies for the title which have been earned by type"
        self.last_updated_date_time = iso_format_to_datetime(last_updated_date_time)
        "Date most recent trophy earned for the title (UTC+00:00 TimeZone)"

    def __str__(self) -> str:
        return (
            f"TrophyGroupsSummary(Title: {self.trophy_title_name}, "
            f"Defined: {self.defined_trophies}, "
            f"Earned: {self.earned_trophies}, "
            f"Progress: {self.progress})"
        )

    def __repr__(self) -> str:
        return (
            f"TrophyGroupsSummary(trophy_set_version={self.trophy_set_version}, "
            f"trophy_title_name={self.trophy_title_name}, "
            f"trophy_title_detail={self.trophy_title_detail}, "
            f"trophy_title_icon_url={self.trophy_title_icon_url}, "
            f"trophy_title_platform={self.trophy_title_platform}, "
            f"defined_trophies={self.defined_trophies}, "
            f"trophy_groups={self.trophy_groups}, "
            f"hidden_flag={self.hidden_flag}, "
            f"progress={self.progress}, "
            f"earned_trophies={self.earned_trophies}, "
            f"last_updated_date_time={self.last_updated_date_time})"
        )


class TrophyGroupsSummaryBuilder:
    """Class for providing convenient method to Build TrophyGroupsSummary from PlayStation Endpoints"""

    def __init__(self, authenticator: Authenticator, np_communication_id: str):
        """:param request_builder: The instance of authenticator. Used to make HTTPRequests.
        :param np_communication_id: Unique ID of a game title used to request trophy information. This can be obtained from ``GameTitle`` class.

        """
        self.authenticator = authenticator
        self.np_communication_id: str = np_communication_id

    @staticmethod
    def trophy_groups_dict_to_obj(trophy_groups_dict: dict[str, Any], trophy_groups: list[T]) -> TrophyGroupsSummary[T]:
        """Takes list of TrophyGroupSummary and TrophyGroupSummaryWithProgress and returns TrophyGroupsSummary[TrophyGroupSummary]
            or TrophyGroupsSummary[TrophyGroupSummaryWithProgress].

        :param trophy_groups_dict: dict from endpoint.
        :param trophy_groups: list of TrophyGroupSummary or TrophyGroupSummaryWithProgress

        :returns: TrophyGroupsSummary containing list of TrophyGroupSummary or TrophyGroupSummaryWithProgress along with some more information.

        """
        trophy_group_summary = TrophyGroupsSummary(
            trophy_set_version=trophy_groups_dict.get("trophySetVersion"),
            trophy_title_name=trophy_groups_dict.get("trophyTitleName"),
            trophy_title_detail=trophy_groups_dict.get("trophyTitleDetail"),
            trophy_title_icon_url=trophy_groups_dict.get("trophyTitleIconUrl"),
            trophy_title_platform=set(
                [PlatformType(platform_str) for platform_str in trophy_groups_dict.get("trophyTitlePlatform", "").split(",")],
            ),
            defined_trophies=TrophySet(
                **trophy_groups_dict.get(
                    "definedTrophies",
                    {"bronze": 0, "silver": 0, "gold": 0, "platinum": 0},
                )
            ),
            trophy_groups=trophy_groups,
            hidden_flag=trophy_groups_dict.get("hiddenFlag"),
            progress=trophy_groups_dict.get("progress"),
            earned_trophies=TrophySet(
                **trophy_groups_dict.get(
                    "earnedTrophies",
                    {"bronze": 0, "silver": 0, "gold": 0, "platinum": 0},
                )
            ),
            last_updated_date_time=trophy_groups_dict.get("lastUpdatedDateTime"),
        )
        return trophy_group_summary

    def game_title_trophy_groups_summary(
        self,
        platform: PlatformType,
    ) -> TrophyGroupsSummary[TrophyGroupSummary]:
        """Retrieves the trophy groups for a title and their respective trophy count.

        This is most commonly seen in games which have expansions where additional trophies are added.

        :param platform: The platform this title belongs to.

        :returns: TrophyGroupSummary object containing title and title groups trophy information.

        :raises PSNAWPNotFound: if you don't have any trophies for that game.
        :raises PSNAWPForbidden: If the user's profile is private.

        """

        service_name = "trophy2" if platform == PlatformType.PS5 else "trophy"
        params = {"npServiceName": service_name}
        try:
            response = self.authenticator.get(
                url=f"{BASE_PATH['trophies']}{API_PATH['title_trophy_group'].format(np_communication_id=self.np_communication_id)}",
                params=params,
            ).json()
        except PSNAWPNotFound as not_found:
            raise PSNAWPNotFound("The following user has no trophies for the given game title.") from not_found

        trophy_groups = [TrophyGroupSummary.from_dict(trophy_group) for trophy_group in response.get("trophyGroups", [])]

        return type(self).trophy_groups_dict_to_obj(
            response,
            trophy_groups,
        )

    def earned_user_trophy_groups_summary(
        self,
        account_id: str,
        platform: PlatformType,
    ) -> TrophyGroupsSummary[TrophyGroupSummaryWithProgress]:
        """Retrieves the earned trophy groups for a title and their respective trophy count along with their trophy earned progress.

        This is most commonly seen in games which have expansions where additional trophies are added.

        :param account_id: The account whose trophy list is being accessed.
        :param platform: The platform this title belongs to.

        :returns: TrophyGroupSummary object containing title and title groups trophy information.

        :raises PSNAWPNotFound: if you don't have any trophies for that game.
        :raises PSNAWPForbidden: If the user's profile is private.

        """

        service_name = "trophy2" if platform == PlatformType.PS5 else "trophy"
        params = {"npServiceName": service_name}

        trophy_groups_metadata = self.authenticator.get(
            url=f"{BASE_PATH['trophies']}{API_PATH['title_trophy_group'].format(np_communication_id=self.np_communication_id)}",
            params=params,
        ).json()

        trophy_groups_user_data = self.authenticator.get(
            url=f"{BASE_PATH['trophies']}{API_PATH['user_title_trophy_group'].format(account_id=account_id, np_communication_id=self.np_communication_id)}",
            params=params,
        ).json()

        merged_data: dict[str, Any] = trophy_groups_metadata | trophy_groups_user_data
        merged_trophy_groups: list[dict[str, Any]] = [
            x[0] | x[1] for x in zip(trophy_groups_metadata.get("trophyGroups"), trophy_groups_user_data.get("trophyGroups"))
        ]
        merged_data["trophyGroups"] = merged_trophy_groups

        trophy_groups = [TrophyGroupSummaryWithProgress.from_dict(trophy_group) for trophy_group in merged_data.get("trophyGroups", [])]

        return type(self).trophy_groups_dict_to_obj(
            merged_data,
            trophy_groups,
        )
