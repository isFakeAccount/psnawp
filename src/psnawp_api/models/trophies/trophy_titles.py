"""Provides the TrophyTitle class for retrieving overall trophy summary for each video game title."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from typing_extensions import Self, override

from psnawp_api.core import PSNAWPBadRequestError, PSNAWPNotFoundError
from psnawp_api.models.listing import PaginationIterator
from psnawp_api.models.trophies import PlatformType, TrophySet
from psnawp_api.utils import API_PATH, BASE_PATH, iso_format_to_datetime

if TYPE_CHECKING:
    from collections.abc import Generator
    from datetime import datetime

    from psnawp_api.core import Authenticator
    from psnawp_api.models.listing import PaginationArguments


@dataclass(frozen=True)
class TrophyTitle:
    """A class containing summary of trophy data for a user for a game title.

    :var str | None np_service_name: trophy for PS3, PS4, or PS Vita platforms and trophy2 for the PS5 platform.
    :var str | None np_communication_id: Unique ID of the title.
    :var str | None trophy_set_version: The current version of the trophy set.
    :var str | None title_name: Title name.
    :var str | None title_detail: Title description (PS3, PS4 and PS Vita titles only).
    :var str | None title_icon_url: URL of the icon for the title.
    :var frozenset[PlatformType] title_platform: Platforms this title belongs to.
    :var bool | None has_trophy_groups: True if the title has multiple groups of trophies (eg. DLC trophies which are
        separate from the main trophy list).
    :var int | None progress: Percentage of trophies earned for the title.
    :var bool | None hidden_flag: Title has been hidden on the accounts trophy list (Only for Client).
    :var TrophySet earned_trophies: Number of trophies for the title which have been earned by type.
    :var TrophySet defined_trophies: Number of trophies for the title by type.
    :var datetime.datetime | None last_updated_datetime: Date most recent trophy earned for the title (UTC+00:00
        TimeZone).
    :var str | None np_title_id: Title ID of the title if passed.

    """

    np_service_name: str | None
    np_communication_id: str | None
    trophy_set_version: str | None
    title_name: str | None
    title_detail: str | None
    title_icon_url: str | None
    title_platform: frozenset[PlatformType]
    has_trophy_groups: bool | None
    progress: int | None
    hidden_flag: bool | None
    earned_trophies: TrophySet
    defined_trophies: TrophySet
    last_updated_datetime: datetime | None
    np_title_id: str | None  # when title_id is passed


class TrophyTitleIterator(PaginationIterator[TrophyTitle]):
    """Retrieve all game titles associated with an account, and a summary of trophies earned from them.

    :var list[str] title_ids: Optional param that can be passed via init. Lets user fetch Trophy for specific title ids.

    .. note::

        This class is intended to be used via Client or User class. See
        :py:meth:`psnawp_api.models.client.Client.trophy_titles`,
        :py:meth:`psnawp_api.models.client.Client.trophy_titles_for_title`,
        :py:meth:`psnawp_api.models.user.User.trophy_titles`, and
        :py:meth:`psnawp_api.models.user.User.trophy_titles_for_title`.

    """

    def __init__(
        self,
        authenticator: Authenticator,
        url: str,
        pagination_args: PaginationArguments,
        title_ids: list[str] | None,
    ) -> None:
        """Constructor of TrophyTitles class.

        :param authenticator: The Authenticator instance used for making authenticated requests to the API.
        :param url: The url of endpoint.
        :param pagination_args: Arguments related to pagination like limit and offset.

        """
        super().__init__(
            authenticator=authenticator,
            url=url,
            pagination_args=pagination_args,
        )
        self.title_ids = title_ids

    @classmethod
    def from_endpoint(
        cls,
        authenticator: Authenticator,
        pagination_args: PaginationArguments,
        account_id: str,
        title_ids: list[str] | None,
    ) -> Self:
        """Creates an instance of :py:class:`TrophyTitleIterator` from api endpoint."""
        if title_ids is None:
            url = f"{BASE_PATH['trophies']}{API_PATH['trophy_titles'].format(account_id=account_id)}"
        else:
            url = f"{BASE_PATH['trophies']}{API_PATH['trophy_titles_for_title'].format(account_id=account_id)}"
        return cls(
            authenticator,
            url,
            pagination_args,
            title_ids,
        )

    @override
    def fetch_next_page(self) -> Generator[TrophyTitle, None, None]:
        """Fetches the next page in endpoint with pagination."""
        if self.title_ids is None:
            return self.get_trophy_title()
        return self.get_trophy_summary_for_title()

    def get_trophy_title(self) -> Generator[TrophyTitle, None, None]:
        """Retrieve all game titles associated with an account, and a summary of trophies earned from them.

        :param limit: Limit of titles returned, None means to return all trophy titles.

        :returns: Generator object with TitleTrophySummary objects

        :raises PSNAWPForbiddenError: If the user's profile is private

        """
        response = self.authenticator.get(
            url=self._url,
            params=self._pagination_args.get_params_dict(),
        ).json()
        self._total_item_count = response.get("totalItemCount", 0)

        trophy_titles: list[dict[str, Any]] = response.get("trophyTitles")
        for trophy_title in trophy_titles:
            title_trophy_sum = TrophyTitle(
                np_service_name=trophy_title.get("npServiceName"),
                np_communication_id=trophy_title.get("npCommunicationId"),
                trophy_set_version=trophy_title.get("trophySetVersion"),
                title_name=trophy_title.get("trophyTitleName"),
                title_detail=trophy_title.get("trophyTitleDetail"),
                title_icon_url=trophy_title.get("trophyTitleIconUrl"),
                title_platform=frozenset(
                    [
                        PlatformType(platform_str)
                        for platform_str in trophy_title.get(
                            "trophyTitlePlatform",
                            "",
                        ).split(",")
                    ],
                ),
                has_trophy_groups=trophy_title.get("hasTrophyGroups"),
                progress=trophy_title.get("progress"),
                hidden_flag=trophy_title.get("hiddenFlag"),
                last_updated_datetime=iso_format_to_datetime(trophy_title.get("lastUpdatedDateTime")),
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
                    ),
                ),
                np_title_id=None,
            )
            self._pagination_args.increment_offset()
            yield title_trophy_sum

        offset = response.get("nextOffset") or 0
        if offset > 0:
            self._has_next = True
        else:
            self._has_next = False

    def get_trophy_summary_for_title(self) -> Generator[TrophyTitle, None, None]:
        """Retrieve a summary of the trophies earned by a user for specific titles.

        :param list[str] title_ids: Unique ID of the title

        :returns: Generator object with TitleTrophySummary objects

        :raises PSNAWPForbiddenError: If the user's profile is private

        """
        params = {
            "npTitleIds": ",".join(
                self.title_ids if self.title_ids is not None else [],
            ),
        }
        response = self.authenticator.get(url=self._url, params=params).json()
        self._total_item_count = response.get("totalItemCount", 0)

        for title in response.get("titles"):
            for trophy_title in title.get("trophyTitles"):
                title_trophy_sum = TrophyTitle(
                    np_service_name=trophy_title.get("npServiceName"),
                    np_communication_id=trophy_title.get("npCommunicationId"),
                    trophy_set_version=trophy_title.get("trophySetVersion"),
                    title_name=trophy_title.get("trophyTitleName"),
                    title_detail=trophy_title.get("trophyTitleDetail"),
                    title_icon_url=trophy_title.get("trophyTitleIconUrl"),
                    title_platform=frozenset(
                        [
                            PlatformType(platform_str)
                            for platform_str in trophy_title.get(
                                "trophyTitlePlatform",
                                "",
                            ).split(",")
                        ],
                    ),
                    has_trophy_groups=trophy_title.get("hasTrophyGroups"),
                    progress=trophy_title.get("progress"),
                    hidden_flag=trophy_title.get("hiddenFlag"),
                    last_updated_datetime=iso_format_to_datetime(trophy_title.get("lastUpdatedDateTime")),
                    defined_trophies=trophy_title.get(
                        "definedTrophies",
                        {"bronze": 0, "silver": 0, "gold": 0, "platinum": 0},
                    ),
                    earned_trophies=trophy_title.get(
                        "earnedTrophies",
                        {"bronze": 0, "silver": 0, "gold": 0, "platinum": 0},
                    ),
                    np_title_id=title.get("npTitleId"),
                )
                yield title_trophy_sum

        # This endpoint does not have pagination
        self._has_next = False

    @staticmethod
    def get_np_communication_id(
        authenticator: Authenticator,
        title_id: str,
        account_id: str,
    ) -> str:
        """Returns the np communication id of title. This is required for requesting detail about a titles trophies.

        .. note::

            The endpoint only returns useful response back if the account has played that particular video game.

        :param authenticator: The Authenticator instance used for making authenticated requests to the API.
        :param title_id: Unique ID of the title
        :param account_id: Account ID of the user.

        :returns: np communication id of title

        :raises PSNAWPNotFoundError: If the user does not have any trophies for that game or the game doesn't exist.

        """
        params = {"npTitleIds": f"{title_id},"}

        try:
            response = authenticator.get(
                url=f"{BASE_PATH['trophies']}{API_PATH['trophy_titles_for_title'].format(account_id=account_id)}",
                params=params,
            ).json()
        except (PSNAWPBadRequestError, PSNAWPNotFoundError) as bad_req:
            raise PSNAWPNotFoundError(
                f"Could not find a Video Game with Title: {title_id}",
            ) from bad_req

        if len(response.get("titles")[0].get("trophyTitles")) == 0:
            raise PSNAWPNotFoundError(
                f"Could not find a Video Game with Title: {title_id}. Most likely the user doesn't own the game.",
            )

        np_comm_id: str = response.get("titles")[0].get("trophyTitles")[0].get("npCommunicationId", title_id)
        return np_comm_id
