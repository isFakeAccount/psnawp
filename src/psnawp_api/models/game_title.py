from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from psnawp_api.models.listing import PaginationArguments
from psnawp_api.models.trophies import TrophyIterator
from psnawp_api.models.trophies.trophy_group import (
    TrophyGroupsSummary,
    TrophyGroupsSummaryBuilder,
)
from psnawp_api.models.trophies.trophy_titles import TrophyTitleIterator
from psnawp_api.utils import API_PATH, BASE_PATH

if TYPE_CHECKING:
    from psnawp_api.core import Authenticator
    from psnawp_api.models.trophies import PlatformType, TrophyGroupsSummary, TrophyGroupSummary


class GameTitle:
    """The GameTitle class provides the information and methods for retrieving Game details and trophies.

    .. note::

        This class is only useful if the user has played that video game. See :py:meth:`psnawp_api.psnawp.PSNAWP.game_title` for more information.

    """

    def __init__(self, authenticator: Authenticator, title_id: str, account_id: str, np_communication_id: Optional[str]):
        """The GameTitle class constructor.

        .. note::

            This class is intended to be interfaced with through PSNAWP.

        .. note::

            During the construction of the object, an additional call is made to get the np_communication_id. This ID is important for getting trophy data. You
            can avoid this additional HTTP request by passing in ``np_communication_id`` if you have it already.

        .. note::

            ``title_id`` can be obtained from https://andshrew.github.io/PlayStation-Titles/ or from :py:class:`psnawp_api.models.search.Search`

        :param authenticator: The Authenticator instance used for making authenticated requests to the API.
        :param title_id: unique id of game.
        :param: account_id: The account whose trophy list is being accessed.
        :param np_communication_id: Unique ID of a game title used to request trophy information.

        :raises PSNAWPNotFound: If the user does not have any trophies for that game or the game doesn't exist.

        """
        self.authenticator = authenticator
        self.title_id = title_id
        if np_communication_id is None:
            self.np_communication_id = TrophyTitleIterator.get_np_communication_id(authenticator, title_id, account_id)
        else:
            self.np_communication_id = np_communication_id

    def get_details(self) -> list[dict[str, Any]]:
        """Get game details such as full name, description, genre, promotional videos/images, etc...

        :returns: A list of dicts containing info similar to what is shown below (Not all values are shown because of space limitations):

            .. literalinclude:: examples/game_title/get_details.json
                :language: json

        """

        param: dict[str, int | str] = {"age": 99, "country": "US", "language": "en-US"}

        response: list[dict[str, Any]] = self.authenticator.get(
            url=f"{BASE_PATH['game_titles']}{API_PATH['title_concept'].format(title_id=self.title_id)}",
            params=param,
        ).json()

        return response

    def trophies(
        self,
        platform: PlatformType,
        trophy_group_id: str = "default",
        limit: Optional[int] = None,
        offset: int = 0,
        page_size: int = 200,
    ) -> TrophyIterator:
        """Retrieves the individual trophy detail of a single - or all - trophy groups for a title.

        :param platform: The platform this title belongs to.
        :param trophy_group_id: ID for the trophy group. Each game expansion is represented by a separate ID. all to return all trophies for the title, default
            for the game itself, and additional groups starting from 001 and so on return expansions trophies.
        :param limit: Limit of trophies returned, None means to return all trophy titles.
        :param offset: The starting point within the collection of trophies.
        :param page_size: The number of trophies to return per page.

        :returns: Returns the Trophy Generator object with all the information

        :raises PSNAWPNotFound: If you don't have any trophies for that game.

        """

        pg_args = PaginationArguments(total_limit=limit, offset=offset, page_size=page_size)
        return TrophyIterator.from_endpoint(
            authenticator=self.authenticator,
            pagination_args=pg_args,
            np_communication_id=self.np_communication_id,
            platform=platform,
            trophy_group_id=trophy_group_id,
        )

    def trophy_groups_summary(self, platform: PlatformType) -> TrophyGroupsSummary[TrophyGroupSummary]:
        """Retrieves the trophy groups for a title and their respective trophy count.

        This is most commonly seen in games which have expansions where additional trophies are added.

        :param platform: The platform this title belongs to.

        :returns: TrophyGroupSummary object containing title and title groups trophy information.

        :raises PSNAWPNotFound: If you don't have any trophies for that game.

        """
        return TrophyGroupsSummaryBuilder(
            authenticator=self.authenticator,
            np_communication_id=self.np_communication_id,
        ).game_title_trophy_groups_summary(platform=platform)
