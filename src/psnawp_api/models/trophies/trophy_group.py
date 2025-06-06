"""Provides the TrophyGroupsSummary class for retrieving trophy summary for main game and each expansion in the video game title."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from typing_extensions import Self

from psnawp_api.core import PSNAWPNotFoundError
from psnawp_api.models.trophies import PlatformType, TrophySet
from psnawp_api.utils import API_PATH, BASE_PATH, iso_format_to_datetime

if TYPE_CHECKING:
    from datetime import datetime

    from psnawp_api.core import Authenticator


@dataclass(frozen=True)
class TrophyGroupSummary:
    """TrophyGroupSummary contains trophy count data for one trophy group of a game title.

    :var str | None trophy_group_id: ID for the trophy group (all titles have default, additional groups are 001
        incrementing).
    :var str | None trophy_group_name: Trophy group name.
    :var str | None trophy_group_detail: Trophy group description (PS3, PS4 and PS Vita titles only).
    :var str | None trophy_group_icon_url: URL of the icon for the trophy group.
    :var TrophySet defined_trophies: Number of trophies for the trophy group by type.

    .. note::

        To initialize this class, use the class method :py:meth:`TrophyGroupSummary.from_dict`.

    """

    trophy_group_id: str | None
    trophy_group_name: str | None
    trophy_group_detail: str | None
    trophy_group_icon_url: str | None
    defined_trophies: TrophySet

    @classmethod
    def from_dict(cls, trophy_group_dict: dict[str, Any]) -> Self:
        """Creates an instance of :py:class:`~TrophyGroupSummary` from a dictionary.

        :param data: Dictionary containing data, typically from an API response.

        :returns: A new instance of :py:class:`~TrophyGroupSummary`.

        Expected keys vary by class but generally map to instance attributes. Missing keys may default to ``None`` or
        reasonable defaults.

        """
        return cls(
            trophy_group_id=trophy_group_dict.get("trophyGroupId"),
            trophy_group_name=trophy_group_dict.get("trophyGroupName"),
            trophy_group_detail=trophy_group_dict.get("trophyGroupDetail"),
            trophy_group_icon_url=trophy_group_dict.get("trophyGroupIconUrl"),
            defined_trophies=TrophySet(
                **trophy_group_dict.get(
                    "definedTrophies",
                    {"bronze": 0, "silver": 0, "gold": 0, "platinum": 0},
                ),
            ),
        )


@dataclass(frozen=True)
class TrophyGroupSummaryWithProgress(TrophyGroupSummary):
    """TrophyGroupSummaryWithProgress contains trophy count data for one trophy group of a game title and user progress for each trophy group.

    :var int | None progress: Percentage of trophies earned for group.
    :var TrophySet earned_trophies: Number of trophies for the group which have been earned by type.
    :var datetime.datetime | None last_updated_datetime: Date most recent trophy earned for the group.

    .. note::

        To initialize this class, use the class method :meth:`TrophyGroupSummaryWithProgress.from_dict`.

    """

    progress: int | None
    earned_trophies: TrophySet
    last_updated_datetime: datetime | None

    @classmethod
    def from_dict(cls, trophy_group_dict: dict[str, Any]) -> Self:
        """Creates an instance of :py:class:`~TrophyGroupSummaryWithProgress` from a dictionary.

        :param data: Dictionary containing data, typically from an API response.

        :returns: A new instance of :py:class:`~TrophyGroupSummaryWithProgress`.

        Expected keys vary by class but generally map to instance attributes. Missing keys may default to ``None`` or
        reasonable defaults.

        """
        return cls(
            trophy_group_id=trophy_group_dict.get("trophyGroupId"),
            trophy_group_name=trophy_group_dict.get("trophyGroupName"),
            trophy_group_detail=trophy_group_dict.get("trophyGroupDetail"),
            trophy_group_icon_url=trophy_group_dict.get("trophyGroupIconUrl"),
            defined_trophies=TrophySet(
                **trophy_group_dict.get(
                    "definedTrophies",
                    {"bronze": 0, "silver": 0, "gold": 0, "platinum": 0},
                ),
            ),
            progress=trophy_group_dict.get("progress"),
            earned_trophies=TrophySet(
                **trophy_group_dict.get(
                    "earnedTrophies",
                    {"bronze": 0, "silver": 0, "gold": 0, "platinum": 0},
                ),
            ),
            last_updated_datetime=iso_format_to_datetime(trophy_group_dict.get("lastUpdatedDateTime")),
        )


T = TypeVar("T", bound=TrophyGroupSummary)


class TrophyGroupsSummary(Generic[T]):
    """Summary of trophy data for a PlayStation game title.

    This class encapsulates the trophy summary information returned by the PlayStation API. It provides overall trophy
    counts for a game title as well as detailed summaries for each trophy group. A trophy group represents a segment of
    the title such as the main game or any associated DLCs/expansions. For example, if a game has two DLCs, the
    trophy_groups list will include three entries: one for the main game and one for each DLC.

    :var str | None trophy_set_version: The current version of the trophy set.
    :var str | None trophy_title_name: Title name.
    :var str | None trophy_title_detail: Title description (PS3, PS4 and PS Vita titles only).
    :var str | None trophy_title_icon_url: URL of the icon for the trophy title.
    :var set[PlatformType] trophy_title_platform: The platform this title belongs to.
    :var TrophySet defined_trophies: Total number of trophies for the title by type.
    :var list[T] trophy_groups: Individual object for each trophy group returned.
    :var bool | None hidden_flag: Whether title has been hidden on the accounts trophy list (Authenticating account
        only).
    :var int | None progress: Percentage of trophies earned for the title.
    :var TrophySet earned_trophies: Number of trophies for the title which have been earned by type.
    :var datetime.datetime | None last_updated_datetime: Date most recent trophy earned for the title (UTC+00:00
        TimeZone).

    .. note::

        To initialize this class, you need the :py:meth:`TrophyGroupsSummaryBuilder.game_title_trophy_groups_summary` or
        :py:meth:`TrophyGroupsSummaryBuilder.earned_user_trophy_groups_summary`.

    """

    def __init__(
        self,
        trophy_set_version: str | None,
        trophy_title_name: str | None,
        trophy_title_detail: str | None,
        trophy_title_icon_url: str | None,
        trophy_title_platform: set[PlatformType],
        defined_trophies: TrophySet,
        trophy_groups: list[T],
        hidden_flag: bool | None,
        progress: int | None,
        earned_trophies: TrophySet,
        last_updated_datetime: datetime | None,
    ) -> None:
        """Initialize a TrophyGroupsSummary instance with PlayStation trophy data."""
        self.trophy_set_version = trophy_set_version
        self.trophy_title_name = trophy_title_name
        self.trophy_title_detail = trophy_title_detail
        self.trophy_title_icon_url = trophy_title_icon_url
        self.trophy_title_platform = trophy_title_platform
        self.defined_trophies = defined_trophies
        self.trophy_groups = trophy_groups
        self.hidden_flag = hidden_flag
        self.progress = progress
        self.earned_trophies = earned_trophies
        self.last_updated_datetime = last_updated_datetime

    def __str__(self) -> str:
        """Returns a human-readable summary of the trophy group."""
        return (
            f"TrophyGroupsSummary(Title: {self.trophy_title_name}, Defined: {self.defined_trophies}, Earned: {self.earned_trophies}, Progress: {self.progress})"
        )

    def __repr__(self) -> str:
        """Returns a detailed string representation of the object for debugging."""
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
            f"last_updated_datetime={self.last_updated_datetime})"
        )


class TrophyGroupsSummaryBuilder:
    """Provides methods to build a TrophyGroupsSummary from PlayStation Network endpoints.

    :var Authenticator authenticator: An instance of :py:class:`~psnawp_api.core.authenticator.Authenticator` used to
        authenticate and make HTTPS requests.
    :var str np_communication_id: Unique identifier associated with a game's trophy set, essential for accessing trophy
        data.

    .. note::

        This class is intended to be used via Client or User class. See
        :py:meth:`psnawp_api.models.client.Client.trophy_groups_summary` or
        :py:meth:`psnawp_api.models.user.User.trophy_groups_summary`.

    """

    def __init__(self, authenticator: Authenticator, np_communication_id: str) -> None:
        """Initializes the TrophyGroupsSummaryBuilder.

        :param Authenticator authenticator: Instance used to make HTTP requests.
        :param str np_communication_id: Unique ID of a game title used to request trophy information. This can be
            obtained from the :py:class:`~psnawp_api.models.game_title.GameTitle` class.

        """
        self.authenticator = authenticator
        self.np_communication_id: str = np_communication_id

    @staticmethod
    def trophy_groups_dict_to_obj(
        trophy_groups_dict: dict[str, Any],
        trophy_groups: list[T],
    ) -> TrophyGroupsSummary[T]:
        """Takes list of TrophyGroupSummary and TrophyGroupSummaryWithProgress converts them to Class instance.

        :param trophy_groups_dict: dict from endpoint.
        :param trophy_groups: list of TrophyGroupSummary or TrophyGroupSummaryWithProgress

        :returns: TrophyGroupsSummary containing list of TrophyGroupSummary or TrophyGroupSummaryWithProgress along with
            some more information.

        """
        return TrophyGroupsSummary(
            trophy_set_version=trophy_groups_dict.get("trophySetVersion"),
            trophy_title_name=trophy_groups_dict.get("trophyTitleName"),
            trophy_title_detail=trophy_groups_dict.get("trophyTitleDetail"),
            trophy_title_icon_url=trophy_groups_dict.get("trophyTitleIconUrl"),
            trophy_title_platform={
                PlatformType(platform_str)
                for platform_str in trophy_groups_dict.get(
                    "trophyTitlePlatform",
                    "",
                ).split(",")
            },
            defined_trophies=TrophySet(
                **trophy_groups_dict.get(
                    "definedTrophies",
                    {"bronze": 0, "silver": 0, "gold": 0, "platinum": 0},
                ),
            ),
            trophy_groups=trophy_groups,
            hidden_flag=trophy_groups_dict.get("hiddenFlag"),
            progress=trophy_groups_dict.get("progress"),
            earned_trophies=TrophySet(
                **trophy_groups_dict.get(
                    "earnedTrophies",
                    {"bronze": 0, "silver": 0, "gold": 0, "platinum": 0},
                ),
            ),
            last_updated_datetime=iso_format_to_datetime(trophy_groups_dict.get("lastUpdatedDateTime")),
        )

    def game_title_trophy_groups_summary(
        self,
        platform: PlatformType,
    ) -> TrophyGroupsSummary[TrophyGroupSummary]:
        """Retrieves the trophy groups for a title and their respective trophy count.

        This is most commonly seen in games which have expansions where additional trophies are added.

        :param platform: The platform this title belongs to.

        :returns: TrophyGroupSummary object containing title and title groups trophy information.

        :raises PSNAWPNotFoundError: if you don't have any trophies for that game.
        :raises PSNAWPForbiddenError: If the user's profile is private.

        """
        service_name = platform.get_trophy_service_name()
        params = {"npServiceName": service_name}
        try:
            response = self.authenticator.get(
                url=f"{BASE_PATH['trophies']}{API_PATH['title_trophy_group'].format(np_communication_id=self.np_communication_id)}",
                params=params,
            ).json()
        except PSNAWPNotFoundError as not_found:
            raise PSNAWPNotFoundError(
                "The following user has no trophies for the given game title.",
            ) from not_found

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

        .. warning::

            Retrieving the progress of TrophyGroupSummary will require double the number of request because the progress
            has to be fetched via separate endpoint.

        :param account_id: The account whose trophy list is being accessed.
        :param platform: The platform this title belongs to.

        :returns: TrophyGroupSummary object containing title and title groups trophy information.

        :raises PSNAWPNotFoundError: if you don't have any trophies for that game.
        :raises PSNAWPForbiddenError: If the user's profile is private.

        """
        service_name = platform.get_trophy_service_name()
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
            x[0] | x[1]
            for x in zip(
                trophy_groups_metadata.get("trophyGroups"),
                trophy_groups_user_data.get("trophyGroups"),
                strict=False,
            )
        ]
        merged_data["trophyGroups"] = merged_trophy_groups

        trophy_groups = [TrophyGroupSummaryWithProgress.from_dict(trophy_group) for trophy_group in merged_data.get("trophyGroups", [])]

        return type(self).trophy_groups_dict_to_obj(
            merged_data,
            trophy_groups,
        )
