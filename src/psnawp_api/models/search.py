from __future__ import annotations

import json
from enum import IntEnum
from typing import TYPE_CHECKING, Any, Generator, Optional

from typing_extensions import List, NotRequired, Self, TypedDict

from psnawp_api.models.listing import PaginationIterator
from psnawp_api.utils import BASE_PATH

if TYPE_CHECKING:
    from psnawp_api.core import Authenticator
    from psnawp_api.models.listing import PaginationArguments


class Data(TypedDict):
    universalDomainSearch: NotRequired[UniversalDomainSearch]
    universalContextSearch: NotRequired[UniversalContextSearch]


class UniversalContextSearch(TypedDict):
    __typename: str
    results: List[Result]


class UniversalDomainSearch(TypedDict):
    __typename: str
    domain: str
    domainTitle: str
    next: str
    searchResults: List[SearchResult]
    totalResultCount: int
    zeroState: bool


class Result(TypedDict):
    __typename: str
    domain: str
    domainTitle: str
    next: str
    searchResults: List[SearchResult]
    totalResultCount: int
    zeroState: bool


class SearchResult(TypedDict):
    __typename: str
    highlight: Highlight
    id: str
    result: DefaultProductOrResult


class Highlight(TypedDict):
    __typename: str
    name: Optional[List[str]]


class DefaultProductOrResult(TypedDict):
    __typename: str
    id: str
    invariantName: str
    itemType: str
    localizedStoreDisplayClassification: Optional[str]
    media: List[Media]
    name: str
    platforms: List[str]
    price: Price
    storeDisplayClassification: Optional[None]
    type: NotRequired[str]
    defaultProduct: NotRequired[DefaultProductOrResult]


class Media(TypedDict):
    __typename: str
    role: str
    type: str
    url: str


class Price(TypedDict):
    __typename: str
    basePrice: str
    basePriceValue: int
    campaignId: Optional[Any]
    currencyCode: str
    discountText: Optional[Any]
    discountedPrice: str
    discountedValue: int
    endTime: Optional[Any]
    isExclusive: bool
    isFree: bool
    isTiedToSubscription: bool
    qualifications: Optional[List[Qualification]]
    rewardId: str
    serviceBranding: List[str]
    skuId: str
    upsellServiceBranding: List[str]
    upsellText: Optional[Any]


class Qualification(TypedDict):
    __typename: str
    type: str
    value: str


class SearchDomain(IntEnum):
    FULL_GAMES = 0
    ADD_ONS = 1


class UniversalSearch:
    def __init__(self, authenticator: Authenticator, pagination_args: PaginationArguments, search_query: str) -> None:
        self.authenticator = authenticator
        self.pagination_args = pagination_args
        self.search_query = search_query
        self._search_common_header = {
            "Content-Type": "Application/json",
            "apollographql-client-name": "PlayStationApp-Android",
            "apollographql-client-version": "24.4.1",
        }

        variables: dict[str, str | int] = {
            "searchTerm": search_query,
            "searchContext": "MobileUniversalSearchGame",
            "displayTitleLocale": "en-US",
        }

        extensions = {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "a2fbc15433b37ca7bfcd7112f741735e13268f5e9ebd5ffce51b85acc126f41d",
            }
        }

        self.params = {
            "operationName": "metGetContextSearchResults",
            "variables": json.dumps(variables),
            "extensions": json.dumps(extensions),
        }

    def search_full_game(self) -> Generator[SearchResult, None, None]:
        response: dict[str, Any] = self.authenticator.get(
            url=BASE_PATH["graph_ql"],
            headers=self._search_common_header,
            params=self.params,
        ).json()

        data: Data = response.get("data", {"universalDomainSearch": {"results": []}})
        universal_search: UniversalContextSearch | dict[str, list[Any]] = data.get("universalContextSearch", {"results": []})
        full_games = universal_search.get("results", [])[SearchDomain.FULL_GAMES]
        search_results = full_games["searchResults"]

        for search_result in search_results:
            if self.pagination_args.is_limit_reached():
                return

            self.pagination_args.increment_offset()
            yield search_result

        search_iter = UniversalDomainSearchIterator.from_endpoint(
            authenticator=self.authenticator,
            pagination_args=self.pagination_args,
            search_query=self.search_query,
            search_domain=SearchDomain.FULL_GAMES,
            next_cursor=full_games["next"],
        )

        for search_result in search_iter:
            yield search_result

    def search_add_onns(self) -> Generator[SearchResult, None, None]:
        response: dict[str, Any] = self.authenticator.get(
            url=BASE_PATH["graph_ql"],
            headers=self._search_common_header,
            params=self.params,
        ).json()

        data: Data = response.get("data", {"universalDomainSearch": {"results": []}})
        universal_search: UniversalContextSearch | dict[str, list[Any]] = data.get("universalContextSearch", {"results": []})
        addons = universal_search.get("results", [])[SearchDomain.ADD_ONS]
        search_results = addons["searchResults"]

        for search_result in search_results:
            if self.pagination_args.is_limit_reached():
                return

            self.pagination_args.increment_offset()
            yield search_result

        search_iter = UniversalDomainSearchIterator.from_endpoint(
            authenticator=self.authenticator,
            pagination_args=self.pagination_args,
            search_query=self.search_query,
            search_domain=SearchDomain.FULL_GAMES,
            next_cursor=addons["next"],
        )

        for search_result in search_iter:
            yield search_result


class UniversalDomainSearchIterator(PaginationIterator[SearchResult]):
    def __init__(
        self,
        authenticator: Authenticator,
        url: str,
        pagination_args: PaginationArguments,
        search_query: str,
        search_domain: SearchDomain,
        next_cursor: str,
    ) -> None:
        """The SearchGames class provides the information and methods for searching full games playstation network.

        .. note::

            This class is intended to be interfaced with through PSNAWP.

        :param authenticator: The Authenticator instance used for making authenticated requests to the API.

        """
        super().__init__(authenticator=authenticator, url=url, pagination_args=pagination_args)
        self.search_query = search_query
        self.search_domain = search_domain
        self._search_common_header = {
            "Content-Type": "Application/json",
            "apollographql-client-name": "PlayStationApp-Android",
            "apollographql-client-version": "24.4.1",
        }
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
            "searchDomain": "MobileGames" if self.search_domain == SearchDomain.FULL_GAMES else "MobileAddOns",
            "pageSize": self._pagination_args.adjusted_page_size,
            "pageOffset": self._pagination_args.offset,
            "nextCursor": self.next_cursor,
        }

        extensions = {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "b51624299bd17b3799f77c9f097cc8887a04d3873f0329095976a841595bc902",
            }
        }

        params = {
            "operationName": "metGetDomainSearchResults",
            "variables": json.dumps(variables),
            "extensions": json.dumps(extensions),
        }

        response: dict[str, Any] = self.authenticator.get(
            url=BASE_PATH["graph_ql"],
            headers=self._search_common_header,
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

        data: Data = response.get("data", {"universalDomainSearch": default_instance})
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
