from __future__ import annotations

from typing import Any, Optional, Literal, Iterator

from psnawp_api.models.trophies.trophy import Trophy, TrophyBuilder
from psnawp_api.models.trophies.trophy_group import (
    TrophyGroupsSummary,
    TrophyGroupsSummaryBuilder,
)
from psnawp_api.models.trophies.trophy_titles import TrophyTitles
from psnawp_api.utils.endpoints import BASE_PATH, API_PATH
from psnawp_api.utils.request_builder import RequestBuilder


class GameTitle:
    """The GameTitle class provides the information and methods for retrieving Game details and trophies.

    .. note::

        This class is only useful if the user has played that video game. See
        :py:meth:`psnawp_api.psnawp.PSNAWP.game_title` for more information.

    """

    def __init__(
        self,
        request_builder: RequestBuilder,
        title_id: str,
        account_id: str,
    ):
        """The GameTitle class constructor.

        .. note::

            This class is intended to be interfaced with through PSNAWP.

        :param request_builder: The instance of RequestBuilder. Used to make
            HTTPRequests.
        :type request_builder: RequestBuilder
        :param title_id: unique id of game.
        :type title_id: str
        :param: account_id: The account whose trophy list is being accessed
        :type account_id: str

        """
        self._request_builder = request_builder
        self.title_id = title_id
        self.np_communication_id: str = TrophyTitles.get_np_communication_id(
            request_builder, title_id, account_id
        )

    def get_details(self) -> list[dict[str, Any]]:
        """Get game details.

        :returns: A list of dicts containing info similar to what is shown below (Not
            all values are shown because of space limitations):
        :rtype: list[dict[str, Any]]

            .. literalinclude:: examples/game_title/get_details.json
                :language: json

        """

        param = {"age": 99, "country": "US", "language": "en-US"}

        response: list[dict[str, Any]] = self._request_builder.get(
            url=f"{BASE_PATH['game_titles']}{API_PATH['title_concept'].format(title_id=self.title_id)}",
            params=param,
        ).json()

        return response

    def trophies(
        self,
        platform: Literal["PS Vita", "PS3", "PS4", "PS5"],
        trophy_group_id: str = "default",
        limit: Optional[int] = None,
    ) -> Iterator[Trophy]:
        """Retrieves the individual trophy detail of a single - or all - trophy groups for a title.

        :param platform: The platform this title belongs to.
        :type platform: Literal
        :param trophy_group_id: ID for the trophy group. Each game expansion is
            represented by a separate ID. all to return all trophies for the title,
            default for the game itself, and additional groups starting from 001 and so
            on return expansions trophies.
        :type trophy_group_id: str
        :param limit: Limit of trophies returned, None means to return all trophy
            titles.
        :type limit: Optional[int]

        :returns: Returns the Trophy Generator object with all the information
        :rtype: Iterator[Trophy]

        """
        return TrophyBuilder(
            self._request_builder, self.np_communication_id
        ).game_trophies(platform, trophy_group_id, limit)

    def trophy_groups_summary(
        self, platform: Literal["PS Vita", "PS3", "PS4", "PS5"]
    ) -> TrophyGroupsSummary:
        """Retrieves the trophy groups for a title and their respective trophy count.

        This is most commonly seen in games which have expansions where additional
        trophies are added.

        :param platform: The platform this title belongs to.
        :type platform: Literal

        :returns: TrophyGroupSummary object containing title and title groups trophy
            information.
        :rtype: TrophyGroupsSummary

        """
        return TrophyGroupsSummaryBuilder(
            self._request_builder,
            self.np_communication_id,
        ).game_title_trophy_groups_summary(platform)
