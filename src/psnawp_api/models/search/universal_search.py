"""Provides Universal Search Class to search the Playstation network."""

from __future__ import annotations

from typing import TYPE_CHECKING

from psnawp_api.models.search.games_search import UniversalDomainSearchIterator
from psnawp_api.models.search.users_search import UniversalUsersSearchIterator

if TYPE_CHECKING:
    from collections.abc import Generator

    from psnawp_api.core import Authenticator
    from psnawp_api.models.listing import PaginationArguments
    from psnawp_api.models.search.games_search_datatypes import GameSearchResultItem, SearchDomain
    from psnawp_api.models.search.users_result_datatypes import UserSearchResultItem


class UniversalSearch:
    """A class to interact with the PlayStation Universal Search endpoint.

    The UniversalSearch class allows querying the PlayStation API to search for video games, add-ons, and other users.
    It constructs the necessary parameters and handles pagination for performing the search.

    :var Authenticator authenticator: An instance of :py:class:`~psnawp_api.core.authenticator.Authenticator` used to
        authenticate and make HTTPS requests.
    :var PaginationArguments pagination_args: Pagination-specific arguments, such as page size and limit, passed to the
        endpoint.
    :var str search_query: The search query string that will be passed to the API endpoint to search for content.

    .. note::

        This class is intended to be used via PSNAWP class. See :py:meth:`psnawp_api.psnawp.PSNAWP.search`.

    """

    def __init__(
        self,
        authenticator: Authenticator,
        pagination_args: PaginationArguments,
        search_query: str,
    ) -> None:
        """Initializes the UniversalSearch object.

        :param authenticator: The Authenticator instance used for making authenticated requests to the API.
        :param pagination_args: Arguments related to pagination like limit and offset.
        :param search_query: The search query string that will be passed to the API endpoint to search for content.

        """
        self.authenticator = authenticator
        self.pagination_args = pagination_args
        self.search_query = search_query

    def search_game(self, search_domain: SearchDomain) -> Generator[GameSearchResultItem, None, None]:
        """Searches games/game-addons on the Playstation Network.

        :param search_domain: The specific domain within which the search is performed (e.g., games, add-ons, users).

        """
        return UniversalDomainSearchIterator.fetch_results(
            authenticator=self.authenticator,
            pagination_args=self.pagination_args,
            search_query=self.search_query,
            search_domain=search_domain,
        )

    def search_user(self) -> Generator[UserSearchResultItem, None, None]:
        """Searches users on the Playstation Network."""
        return UniversalUsersSearchIterator.fetch_results(
            authenticator=self.authenticator,
            pagination_args=self.pagination_args,
            search_query=self.search_query,
        )
