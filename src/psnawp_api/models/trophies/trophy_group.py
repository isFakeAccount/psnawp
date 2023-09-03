from __future__ import annotations

from datetime import datetime
from typing import Optional, Literal, Any

from attrs import define, field

from psnawp_api.core.psnawp_exceptions import PSNAWPNotFound, PSNAWPForbidden
from psnawp_api.models.trophies.trophy_constants import PlatformType, TrophySet
from psnawp_api.utils.endpoints import BASE_PATH, API_PATH
from psnawp_api.utils.misc import iso_format_to_datetime
from psnawp_api.utils.request_builder import RequestBuilder


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

    # Earned Trophy Group Summary
    progress: Optional[int]
    "Percentage of trophies earned for group"
    earned_trophies: TrophySet
    "Number of trophies for the group which have been earned by type"
    last_updated_datetime: Optional[datetime] = field(converter=iso_format_to_datetime)
    "Date most recent trophy earned for the group"


@define(frozen=True)
class TrophyGroupsSummary:
    """TrophyGroupsSummary contains trophy count data for all the groups in a game title combined and individual."""

    trophy_set_version: Optional[str]
    "The current version of the trophy set"
    trophy_title_name: Optional[str]
    "Title name"
    trophy_title_detail: Optional[str]
    "Title description (PS3, PS4 and PS Vita titles only)"
    trophy_title_icon_url: Optional[str]
    "URL of the icon for the trophy title"
    trophy_title_platform: frozenset[PlatformType]
    "The platform this title belongs to"
    defined_trophies: TrophySet
    "Total number of trophies for the title by type"
    trophy_groups: list[TrophyGroupSummary] = field(hash=False)
    "Individual object for each trophy group returned"

    # Earned Trophy Groups Summary
    hidden_flag: Optional[bool]
    "Whether title has been hidden on the accounts trophy list (Authenticating account only)"
    progress: Optional[int]
    "Percentage of trophies earned for the title"
    earned_trophies: TrophySet
    "Number of trophies for the title which have been earned by type"
    last_updated_date_time: Optional[datetime] = field(converter=iso_format_to_datetime)
    "Date most recent trophy earned for the title (UTC+00:00 TimeZone)"


def _trophy_groups_dict_to_obj(trophy_groups_dict: Any) -> TrophyGroupsSummary:
    trophy_groups = []
    for trophy_group in trophy_groups_dict.get("trophyGroups"):
        trophy_group_instance = TrophyGroupSummary(
            trophy_group_id=trophy_group.get("trophyGroupId"),
            trophy_group_name=trophy_group.get("trophyGroupName"),
            trophy_group_detail=trophy_group.get("trophyGroupDetail"),
            trophy_group_icon_url=trophy_group.get("trophyGroupIconUrl"),
            defined_trophies=TrophySet(
                **trophy_group.get(
                    "definedTrophies",
                    {"bronze": 0, "silver": 0, "gold": 0, "platinum": 0},
                )
            ),
            progress=trophy_group.get("progress"),
            earned_trophies=TrophySet(
                **trophy_group.get(
                    "earnedTrophies",
                    {"bronze": 0, "silver": 0, "gold": 0, "platinum": 0},
                )
            ),
            last_updated_datetime=trophy_group.get("lastUpdatedDateTime"),
        )
        trophy_groups.append(trophy_group_instance)

    trophy_group_summary = TrophyGroupsSummary(
        trophy_set_version=trophy_groups_dict.get("trophySetVersion"),
        trophy_title_name=trophy_groups_dict.get("trophyTitleName"),
        trophy_title_detail=trophy_groups_dict.get("trophyTitleDetail"),
        trophy_title_icon_url=trophy_groups_dict.get("trophyTitleIconUrl"),
        trophy_title_platform=frozenset(
            [
                PlatformType(platform_str) if platform_str else PlatformType("UNKNOWN")
                for platform_str in trophy_groups_dict.get("trophyTitlePlatform", "").split(",")
            ]
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


class TrophyGroupsSummaryBuilder:
    """Class for providing convenient method to Build TrophyGroupsSummary from PlayStation Endpoints"""

    def __init__(self, request_builder: RequestBuilder, np_communication_id: str):
        """:param request_builder: The instance of RequestBuilder. Used to make HTTPRequests.
        :type request_builder: RequestBuilder
        :param np_communication_id: Unique ID of a game title used to request trophy information. This can be obtained from ``GameTitle`` class.
        :type np_communication_id: str

        """
        self._request_builder = request_builder
        self.np_communication_id: str = np_communication_id

    def game_title_trophy_groups_summary(
        self,
        platform: Literal["PS Vita", "PS3", "PS4", "PS5"],
    ) -> TrophyGroupsSummary:
        """Retrieves the trophy groups for a title and their respective trophy count.

        This is most commonly seen in games which have expansions where additional trophies are added.

        :param platform: The platform this title belongs to.
        :type platform: Literal

        :returns: TrophyGroupSummary object containing title and title groups trophy information.
        :rtype: TrophyGroupsSummary

        :raises: ``PSNAWPNotFound`` if you don't have any trophies for that game.

        :raises: ``PSNAWPForbidden`` If the user's profile is private

        """

        service_name = "trophy2" if platform == "PS5" else "trophy"
        params = {"npServiceName": service_name}
        try:
            response = self._request_builder.get(
                url=f"{BASE_PATH['trophies']}{API_PATH['title_trophy_group'].format(np_communication_id=self.np_communication_id)}",
                params=params,
            ).json()
        except PSNAWPNotFound as not_found:
            raise PSNAWPNotFound("The following user has no trophies for the given game title.") from not_found
        return _trophy_groups_dict_to_obj(response)

    def user_trophy_groups_summary(
        self,
        account_id: str,
        platform: Literal["PS Vita", "PS3", "PS4", "PS5"],
    ) -> TrophyGroupsSummary:
        """Retrieves the earned trophy groups for a title and their respective trophy count.

        This is most commonly seen in games which have expansions where additional trophies are added.

        :param account_id: The account whose trophy list is being accessed
        :type account_id: str
        :param platform: The platform this title belongs to.
        :type platform: Literal

        :returns: TrophyGroupSummary object containing title and title groups trophy information.
        :rtype: TrophyGroupsSummary

        :raises: ``PSNAWPNotFound`` if you don't have any trophies for that game.

        :raises: ``PSNAWPForbidden`` If the user's profile is private

        """

        service_name = "trophy2" if platform == "PS5" else "trophy"
        params = {"npServiceName": service_name}
        try:
            response = self._request_builder.get(
                url=f"{BASE_PATH['trophies']}{API_PATH['user_title_trophy_group'].format(account_id=account_id, np_communication_id=self.np_communication_id)}",
                params=params,
            ).json()
        except PSNAWPNotFound as not_found:
            raise PSNAWPNotFound("The following user has no trophies for the given game title.") from not_found
        except PSNAWPForbidden as forbidden:
            raise PSNAWPForbidden("The following user has made their trophy private.") from forbidden
        return _trophy_groups_dict_to_obj(response)

    def user_trophy_groups_summary_with_metadata(
        self,
        account_id: str,
        platform: Literal["PS Vita", "PS3", "PS4", "PS5"],
    ) -> TrophyGroupsSummary:
        """Retrieves the earned trophy groups for a title and their respective trophy count along with metadata.

        This is most commonly seen in games which have expansions where additional trophies are added.

        :param account_id: The account whose trophy list is being accessed
        :type account_id: str
        :param platform: The platform this title belongs to.
        :type platform: Literal

        :returns: TrophyGroupSummary object containing title and title groups trophy information.
        :rtype: TrophyGroupsSummary

        :raises: ``PSNAWPNotFound`` if you don't have any trophies for that game.

        :raises: ``PSNAWPForbidden`` If the user's profile is private

        """

        service_name = "trophy2" if platform == "PS5" else "trophy"
        params = {"npServiceName": service_name}

        trophy_groups_metadata = self._request_builder.get(
            url=f"{BASE_PATH['trophies']}{API_PATH['title_trophy_group'].format(np_communication_id=self.np_communication_id)}",
            params=params,
        ).json()

        trophy_groups_user_data = self._request_builder.get(
            url=f"{BASE_PATH['trophies']}{API_PATH['user_title_trophy_group'].format(account_id=account_id, np_communication_id=self.np_communication_id)}",
            params=params,
        ).json()
        merged_data = {**trophy_groups_metadata, **trophy_groups_user_data}
        merged_trophy_groups = [{**x[0], **x[1]} for x in zip(trophy_groups_metadata.get("trophyGroups"), trophy_groups_user_data.get("trophyGroups"))]
        merged_data["trophyGroups"] = merged_trophy_groups
        return _trophy_groups_dict_to_obj(merged_data)
