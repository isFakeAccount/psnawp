"""Implements the endpoints to search users."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from typing_extensions import Self, override

from psnawp_api.models.listing import PaginationIterator
from psnawp_api.models.search.users_result_datatypes import UserSearchResultItem, default_user_root_response
from psnawp_api.utils import BASE_PATH

if TYPE_CHECKING:
    from collections.abc import Generator

    from psnawp_api.core import Authenticator
    from psnawp_api.models.listing import PaginationArguments
    from psnawp_api.models.search.users_result_datatypes import UserContextContainer, UserDomainContainer, UserRootResponse

SEARCH_COMMON_HEADER: dict[str, str] = {
    "accept": "application/json",
    "content-type": "application/json",
    "apollographql-client-name": "PlayStationApp-Android",
    "apollographql-client-version": "25.4.0",
}


class UniversalUsersSearchIterator(PaginationIterator[UserSearchResultItem]):
    """Iterator for paginating over universal search results within a specific domain.

    This iterator handles the pagination logic for querying the PlayStation Network's universal search API, which can be
    used to search across different domains (e.g., games, add-ons, users). It allows for iterating over search results
    based on the provided search query and domain.

    :var Authenticator authenticator: Instance of Authenticator class. Used to make authenticated HTTPs request to
        playstation server.
    :var str search_query: The search query string used to query the universal search endpoint.
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
        next_cursor: str,
    ) -> None:
        """Initializes the UniversalUsersSearchIterator with the provided parameters.

        This iterator fetches search results from the PlayStation universal search API and manages pagination.

        :param authenticator: The Authenticator instance used for making authenticated requests to the API.
        :param url: The URL of the universal search endpoint.
        :param pagination_args: Pagination-specific arguments, such as page size and limit, passed to the endpoint.
        :param search_query: The search query string to search for specific content.
        :param next_cursor: The cursor for fetching the next page of results.
        :param next_cursor: The cursor for fetching the next page of results.

        """
        super().__init__(
            authenticator=authenticator,
            url=url,
            pagination_args=pagination_args,
        )
        self.search_query = search_query
        self.next_cursor = next_cursor

    @classmethod
    def fetch_results(
        cls,
        authenticator: Authenticator,
        pagination_args: PaginationArguments,
        search_query: str,
    ) -> Generator[UserSearchResultItem, None, None]:
        """Initiates a user search and yields results based on the specified search domain.

        This method uses two endpoints:

        - The first retrieves a initial result for users.
        - The second iterates over paginated results.

        :param authenticator: Instance of :class:`Authenticator` used for authenticated API requests.
        :param pagination_args: Pagination control including current offset and limit.
        :param search_query: The query string to search for content.
        :param search_domain: The content domain to search within (e.g., full games or add-ons).

        :yield: Yields individual :class:`SearchResult` objects until the limit is reached. If more results are
            available, continues yielding from the appropriate paginated endpoint.

        """
        variables: dict[str, str | int] = {
            "searchTerm": search_query,
            "searchContext": "MobileUniversalSearchSocial",
            "displayTitleLocale": "en-US",
        }

        extensions = {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "ac5fb2b82c4d086ca0d272fba34418ab327a7762dd2cd620e63f175bbc5aff10",
            },
        }

        params = {
            "operationName": "metGetContextSearchResults",
            "variables": json.dumps(variables),
            "extensions": json.dumps(extensions),
        }

        response: dict[str, Any] = authenticator.get(
            url=BASE_PATH["graph_ql"],
            headers=SEARCH_COMMON_HEADER,
            params=params,
        ).json()

        default_value: UserRootResponse = default_user_root_response()

        user_context_container: UserContextContainer = response.get("data", default_value["data"])
        universal_context_search = user_context_container.get(
            "universalContextSearch",
            default_value["data"]["universalContextSearch"],
        )
        universal_domain_search = universal_context_search.get(
            "results",
            default_value["data"]["universalContextSearch"]["results"],
        )[0]
        search_results = universal_domain_search.get(
            "searchResults",
            default_value["data"]["universalContextSearch"]["results"][0]["searchResults"],
        )

        for search_result in search_results:
            if pagination_args.is_limit_reached():
                return

            pagination_args.increment_offset()
            yield search_result

        search_iter = cls.from_endpoint(
            authenticator=authenticator,
            pagination_args=pagination_args,
            search_query=search_query,
            next_cursor=universal_domain_search.get("next", ""),
        )

        for search_result in search_iter:
            yield search_result

    @classmethod
    def from_endpoint(
        cls,
        authenticator: Authenticator,
        pagination_args: PaginationArguments,
        search_query: str,
        next_cursor: str,
    ) -> Self:
        """Creates an instance of :py:class:`UniversalUsersSearchIterator` from api endpoint."""
        return cls(
            authenticator=authenticator,
            url=BASE_PATH["graph_ql"],
            pagination_args=pagination_args,
            search_query=search_query,
            next_cursor=next_cursor,
        )

    @override
    def fetch_next_page(self) -> Generator[UserSearchResultItem, None, None]:
        """Fetches the next page of Search Result objects from the API.

        :yield: A generator yielding Result objects.

        """
        variables: dict[str, str | int] = {
            "searchTerm": self.search_query,
            "searchDomain": "SocialAllAccounts",
            "displayTitleLocale": "en-US",
            "pageSize": self._pagination_args.adjusted_page_size,
            "pageOffset": self._pagination_args.offset,
            "nextCursor": self.next_cursor,
        }

        extensions = {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "23ece284bf8bdc50bfa30a4d97fd4d733e723beb7a42dff8c1ee883f8461a2e1",
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

        default_value: UserRootResponse = default_user_root_response()
        default_universal_domain_container = {"universalDomainSearch": default_value["data"]["universalContextSearch"]["results"][0]}

        universal_domain_container: UserDomainContainer = response.get("data", default_universal_domain_container)
        universal_domain_search = universal_domain_container.get("universalDomainSearch", default_value["data"]["universalContextSearch"]["results"][0])

        search_results = universal_domain_search.get("searchResults", default_value["data"]["universalContextSearch"]["results"][0]["searchResults"])

        self._total_item_count = universal_domain_search.get("totalResultCount", 0)
        self.next_cursor = universal_domain_search.get("next", "")

        for search_result in search_results:
            if self._pagination_args.is_limit_reached():
                return

            self._pagination_args.increment_offset()
            yield search_result

        if self.next_cursor:
            self._has_next = True
        else:
            self._has_next = False
