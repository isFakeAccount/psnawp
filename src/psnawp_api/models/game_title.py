"""Provides GameTitle class for retrieving Game details and trophies."""

from __future__ import annotations

import hashlib
import hmac
from typing import TYPE_CHECKING, Any, ClassVar

from typing_extensions import Self

from psnawp_api.core.psnawp_exceptions import PSNAWPIllegalArgumentError
from psnawp_api.models.listing import PaginationArguments
from psnawp_api.models.trophies import PlatformType, TrophyIterator, TrophyTitleIterator
from psnawp_api.models.trophies.trophy_group import (
    TrophyGroupsSummary,
    TrophyGroupsSummaryBuilder,
)
from psnawp_api.utils import API_PATH, BASE_PATH

if TYPE_CHECKING:
    from psnawp_api.core import Authenticator
    from psnawp_api.models.trophies import (
        TrophyGroupsSummary,
        TrophyGroupSummary,
    )


class GameTitle:
    """The GameTitle class provides the information and methods for retrieving Game details and trophies.

    Used for fetching game details and trophies for title that client doesn't own.

    :var Authenticator authenticator: An instance of :py:class:`~psnawp_api.core.authenticator.Authenticator` used to
        authenticate and make HTTPS requests.
    :var str title_id: Unique identifier for the game, used across PSN services except for trophy data, which requires
        the np_communication_id. However, the title_id is used to fetch the np_communication_id.
    :var PlatformType platform: The platform this title belongs to.
    :var str np_communication_id: Unique identifier associated with a game's trophy set, essential for accessing trophy
        data.

    .. note::

        This class is intended to be used via PSNAWP. See :py:meth:`psnawp_api.psnawp.PSNAWP.game_title`.

    """

    HMAC_SHA1_KEY: ClassVar[bytes] = bytes.fromhex(
        "F5DE66D2680E255B2DF79E74F890EBF349262F618BCAE2A9ACCDEE5156CE8DF2CDF2D48C71173CDC2594465B87405D197CF1AED3B7E9671EEB56CA6753C2E6B0"
    )

    def __init__(
        self,
        authenticator: Authenticator,
        title_id: str,
        platform: PlatformType,
        np_communication_id: str,
    ) -> None:
        """The GameTitle class constructor.

        :param authenticator: The Authenticator instance used for making authenticated requests to the API.
        :param title_id: unique id of game.
        :param platform: The platform this title belongs to.
        :param np_communication_id: Unique ID of a game title used to request trophy information.

        """
        self.authenticator = authenticator
        self.title_id = title_id
        self.platform = platform
        self.np_communication_id = np_communication_id

    @classmethod
    def with_np_communication_id(
        cls,
        authenticator: Authenticator,
        title_id: str,
        platform: PlatformType,
        np_communication_id: str,
    ) -> Self:
        """Initialize instance of GameTitle class with ``np_communication_id`` provided.

        :param authenticator: The Authenticator instance used for making authenticated requests to the API.
        :param title_id: unique id of game.
        :param platform: The platform this title belongs to.
        :param np_communication_id: Unique ID of a game title used to request trophy information.

        :returns: Instance of :py:class:`GameTitle`

        """
        return cls(authenticator, title_id, platform, np_communication_id)

    @classmethod
    def from_title_id(
        cls,
        authenticator: Authenticator,
        title_id: str,
        platform: PlatformType,
        account_id: str,
    ) -> Self:
        """Initialize instance of GameTitle class from just the title_id.

        During the construction of the object, an additional call is made to get the ``np_communication_id``. This ID is
        important for getting trophy data. You can avoid this additional HTTP request by using the
        :py:meth:`with_np_communication_id` class method.

        :param authenticator: The Authenticator instance used for making authenticated requests to the API.
        :param title_id: unique id of game.
        :param platform: The platform this title belongs to.

        :returns: Instance of :py:class:`GameTitle`

        :raises PSNAWPNotFoundError: If the user does not have any trophies for that game or the game doesn't exist.

        """
        np_communication_id = TrophyTitleIterator.get_np_communication_id(
            authenticator,
            title_id,
            account_id,
        )
        return cls(authenticator, title_id, platform, np_communication_id)

    def get_details(self, country: str | None = None, language: str | None = None) -> list[dict[str, Any]]:
        """Get game details such as full name, description, genre, promotional videos/images, etc...

        If `country` or `language` is not provided, defaults will be used from the authenticator headers.

        :param country: The country code used to retrieve localized content, in ISO 3166-1 alpha-2 format (e.g., "US",
            "JP").
        :param language: The language code used to retrieve localized content, using the IETF BCP 47 format (e.g.,
            "en-US", "fr-FR").

        :returns: A list of dicts containing info similar to what is shown below (Not all values are shown because of
            space limitations):

            .. literalinclude:: ../examples/game_title/get_details.json
                :language: json

        """
        country = country or self.authenticator.common_headers.get("Country", "US")
        language = language or self.authenticator.common_headers.get("Accept-Language", "en-US")
        param: dict[str, int | str] = {"age": 99, "country": country, "language": language}

        response: list[dict[str, Any]] = self.authenticator.get(
            url=f"{BASE_PATH['game_titles']}{API_PATH['title_concept'].format(title_id=self.title_id)}",
            params=param,
        ).json()

        return response

    def trophies(
        self,
        trophy_group_id: str = "default",
        limit: int | None = None,
        offset: int = 0,
        page_size: int = 200,
    ) -> TrophyIterator:
        """Retrieves the individual trophy detail of a single - or all - trophy groups for a title.

        :param trophy_group_id: ID for the trophy group. Each game expansion is represented by a separate ID. all to
            return all trophies for the title, default for the game itself, and additional groups starting from 001 and
            so on return expansions trophies.
        :param limit: Limit of trophies returned, None means to return all trophy titles.
        :param offset: The starting point within the collection of trophies.
        :param page_size: The number of trophies to return per page.

        :returns: Returns the Trophy Generator object with all the information

        :raises PSNAWPNotFoundError: If you don't have any trophies for that game.

        """
        pg_args = PaginationArguments(
            total_limit=limit,
            offset=offset,
            page_size=page_size,
        )
        return TrophyIterator.from_endpoint(
            authenticator=self.authenticator,
            pagination_args=pg_args,
            np_communication_id=self.np_communication_id,
            platform=self.platform,
            trophy_group_id=trophy_group_id,
        )

    def trophy_groups_summary(
        self,
    ) -> TrophyGroupsSummary[TrophyGroupSummary]:
        """Retrieves the trophy groups for a title and their respective trophy count.

        This is most commonly seen in games which have expansions where additional trophies are added.

        :returns: TrophyGroupSummary object containing title and title groups trophy information.

        :raises PSNAWPNotFoundError: If you don't have any trophies for that game.

        """
        return TrophyGroupsSummaryBuilder(
            authenticator=self.authenticator,
            np_communication_id=self.np_communication_id,
        ).game_title_trophy_groups_summary(platform=self.platform)

    def get_title_icon_url(self) -> str:
        """Generate/retrieve the title icon URL for a PlayStation 3/4 title.

        :returns: the title icon URL

        :raises PSNAWPIllegalArgumentError: If the platform is not supported.

        """
        digest = hmac.new(type(self).HMAC_SHA1_KEY, self.title_id.encode(), hashlib.sha1).hexdigest().upper()

        if self.platform is PlatformType.PS3:
            return f"https://tmdb.np.dl.playstation.net/tmdb/{self.title_id}_{digest}/ICON0.PNG"

        if self.platform is PlatformType.PS4:
            json_url = f"https://tmdb.np.dl.playstation.net/tmdb2/{self.title_id}_{digest}/{self.title_id}.json"
            info: dict[str, Any] = self.authenticator.get(url=json_url).json()
            icon_url: str = info["icons"][0]["icon"]
            return icon_url

        raise PSNAWPIllegalArgumentError(f"Unsupported or unknown platform: {self.platform}")
