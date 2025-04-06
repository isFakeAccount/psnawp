"""Provides Universal Search Class to search the Playstation network."""

from __future__ import annotations

import json
from enum import IntEnum
from typing import TYPE_CHECKING, Any

from typing_extensions import Self

from psnawp_api.models.listing import PaginationIterator
from psnawp_api.models.search.search_datatypes import SearchResult
from psnawp_api.utils import BASE_PATH

if TYPE_CHECKING:
    from collections.abc import Generator

    from psnawp_api.core import Authenticator
    from psnawp_api.models.listing import PaginationArguments
    from psnawp_api.models.search.search_datatypes import GameSearchResult, UniversalContextSearch, UniversalDomainSearch


class SearchDomain(IntEnum):
    """Enum representing the different domains for search results."""

    FULL_GAMES = 0
    ADD_ONS = 1


SEARCH_COMMON_HEADER: dict[str, str] = {
    "Content-Type": "Application/json",
    "apollographql-client-name": "PlayStationApp-Android",
    "apollographql-client-version": "24.4.1",
}


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

        variables: dict[str, str | int] = {
            "searchTerm": search_query,
            "searchContext": "MobileUniversalSearchGame",
            "displayTitleLocale": "en-US",
        }

        extensions = {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "a2fbc15433b37ca7bfcd7112f741735e13268f5e9ebd5ffce51b85acc126f41d",
            },
        }

        self.params = {
            "operationName": "metGetContextSearchResults",
            "variables": json.dumps(variables),
            "extensions": json.dumps(extensions),
        }

    def search_game(self, search_domain: SearchDomain) -> Generator[SearchResult, None, None]:
        """Searches games/game-addons on the Playstation Network."""
        response: dict[str, Any] = self.authenticator.get(
            url=BASE_PATH["graph_ql"],
            headers=SEARCH_COMMON_HEADER,
            params=self.params,
        ).json()

        data: GameSearchResult = response.get("data", {"universalDomainSearch": {"results": []}})
        universal_search: UniversalContextSearch | dict[str, list[Any]] = data.get(
            "universalContextSearch",
            {"results": []},
        )

        search_results_container = universal_search.get("results", [])[search_domain]
        search_results = search_results_container.get("searchResults", [])

        for search_result in search_results:
            if self.pagination_args.is_limit_reached():
                return

            self.pagination_args.increment_offset()
            yield search_result

        search_iter = UniversalDomainSearchIterator.from_endpoint(
            authenticator=self.authenticator,
            pagination_args=self.pagination_args,
            search_query=self.search_query,
            search_domain=search_domain,
            next_cursor=search_results_container["next"],
        )

        for search_result in search_iter:
            yield search_result


class UniversalDomainSearchIterator(PaginationIterator[SearchResult]):
    """Iterator for paginating over universal search results within a specific domain.

    This iterator handles the pagination logic for querying the PlayStation Network's universal search API, which can be
    used to search across different domains (e.g., games, add-ons, users). It allows for iterating over search results
    based on the provided search query and domain.

    :var str search_query: The search query string used to query the universal search endpoint.
    :var SearchDomain search_domain: The specific domain within which the search is performed (e.g., games, add-ons,
        users).
    :var str next_cursor: The cursor used for paginating to the next set of results.

    .. note::

        This class is intended to be used via UniversalSearch. See :py:class:`~UniversalSearch`.

    """

    def __init__(
        self,
        authenticator: Authenticator,
        url: str,
        pagination_args: PaginationArguments,
        search_query: str,
        search_domain: SearchDomain,
        next_cursor: str,
    ) -> None:
        """Initializes the UniversalDomainSearchIterator with the provided parameters.

        This iterator fetches search results from the PlayStation universal search API and manages pagination.

        :param authenticator: The Authenticator instance used for making authenticated requests to the API.
        :param url: The URL of the universal search endpoint.
        :param pagination_args: Pagination-specific arguments, such as page size and limit, passed to the endpoint.
        :param search_query: The search query string to search for specific content.
        :param search_domain: The domain to search within (e.g., games, add-ons, users).
        :param next_cursor: The cursor for fetching the next page of results.

        """
        super().__init__(
            authenticator=authenticator,
            url=url,
            pagination_args=pagination_args,
        )
        self.search_query = search_query
        self.search_domain = search_domain
        self.next_cursor = next_cursor

    @classmethod
    def from_endpoint(
        cls,
        authenticator: Authenticator,
        pagination_args: PaginationArguments,
        search_query: str,
        search_domain: SearchDomain,
        next_cursor: str,
    ) -> Self:
        """Creates an instance of :py:class:`UniversalDomainSearchIterator` from api endpoint."""
        return cls(
            authenticator=authenticator,
            url=BASE_PATH["graph_ql"],
            pagination_args=pagination_args,
            search_query=search_query,
            search_domain=search_domain,
            next_cursor=next_cursor,
        )

    def fetch_next_page(self) -> Generator[SearchResult, None, None]:
        """Fetches the next page of Search Result objects from the API.

        :yield: A generator yielding Result objects.

        """
        variables: dict[str, str | int] = {
            "searchTerm": self.search_query,
            "searchDomain": ("MobileGames" if self.search_domain == SearchDomain.FULL_GAMES else "MobileAddOns"),
            "pageSize": self._pagination_args.adjusted_page_size,
            "pageOffset": self._pagination_args.offset,
            "nextCursor": self.next_cursor,
        }

        extensions = {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "b51624299bd17b3799f77c9f097cc8887a04d3873f0329095976a841595bc902",
            },
        }

        params = {
            "operationName": "metGetDomainSearchResults",
            "variables": json.dumps(variables),
            "extensions": json.dumps(extensions),
        }

        response: dict[str, Any] = self.authenticator.get(
            url=BASE_PATH["graph_ql"],
            headers=SEARCH_COMMON_HEADER,
            params=params,
        ).json()

        default_instance: UniversalDomainSearch = {
            "__typename": "",
            "domain": "",
            "domainTitle": "",
            "next": "",
            "searchResults": [],
            "totalResultCount": 0,
            "zeroState": False,
        }

        data: GameSearchResult = response.get("data", {"universalDomainSearch": default_instance})
        universal_search = data.get("universalDomainSearch", default_instance)

        search_results = universal_search["searchResults"]
        self._total_item_count = universal_search.get("totalResultCount", 0)
        self.next_cursor = universal_search.get("next", "")

        for search_result in search_results:
            if self._pagination_args.is_limit_reached():
                return

            self._pagination_args.increment_offset()
            yield search_result

        if self.next_cursor:
            self._has_next = True
        else:
            self._has_next = False
