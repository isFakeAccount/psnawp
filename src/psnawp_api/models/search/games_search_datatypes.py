"""Contains datatypes for the game search result endpoint."""

from __future__ import annotations

from enum import IntEnum
from typing import Literal, TypedDict


class SearchDomain(IntEnum):
    """Enum representing the different domains for game search results."""

    FULL_GAMES = 0
    ADD_ONS = 1
    USERS = 2


class GameRootResponse(TypedDict):
    """Top-level response wrapper for game search data."""

    data: GameContextContainer


class GameContextContainer(TypedDict):
    """Holds the universal context search section of the response."""

    universalContextSearch: GameUniversalContextSearchResponse


class GameDomainContainer(TypedDict):
    """Wraps the `universalDomainSearch` payload, which may either carry only cursors or full result lists."""

    universalDomainSearch: GameUniversalDomainSearchResponse


class GameUniversalContextSearchResponse(TypedDict):
    """Represents aggregated search results across all domains."""

    __typename: Literal["UniversalContextSearchResponse"]
    queryFrequency: GameQueryFrequency
    results: list[GameUniversalDomainSearchResponse]


class GameQueryFrequency(TypedDict):
    """Timing settings for debouncing search queries."""

    __typename: Literal["QueryFrequency"]
    filterDebounceMs: int
    searchDebounceMs: int


class GameUniversalDomainSearchResponse(TypedDict):
    """Search results scoped to a single domain."""

    __typename: Literal["UniversalDomainSearchResponse"]
    domain: str
    domainTitle: str
    next: str
    searchResults: list[GameSearchResultItem]
    totalResultCount: int
    zeroState: bool


class GameSearchResultItem(TypedDict):
    """A single item in a domain-specific search result list."""

    __typename: Literal["SearchResultItem"]
    highlight: GameItemHighlight
    id: str
    result: GameConceptResult | GameProductResult
    resultOriginFlag: list[str] | None


class GameItemHighlight(TypedDict):
    """Text highlighting metadata for search result fields."""

    __typename: Literal["ItemHighlight"]
    name: list[str] | None


class GameConceptResult(TypedDict):
    """Represents a conceptual search result with optional default product."""

    __typename: Literal["Concept"]
    defaultProduct: GameProductResult | None
    id: str
    invariantName: str
    itemType: str
    localizedStoreDisplayClassification: str | None
    media: list[GameMedia]
    name: str
    platforms: list[str]
    price: GameSkuPrice | None
    storeDisplayClassification: str | None
    type: str


class GameProductResult(TypedDict):
    """Represents a concrete product search result."""

    __typename: Literal["Product"]
    id: str
    invariantName: str
    itemType: str
    localizedStoreDisplayClassification: str | None
    media: list[GameMedia]
    name: str
    platforms: list[str]
    price: GameSkuPrice | None
    storeDisplayClassification: str | None
    type: str


class GameMedia(TypedDict):
    """Media asset metadata for search results (images, videos, etc.)."""

    __typename: Literal["Media"]
    role: str
    type: str
    url: str


class GameSkuPrice(TypedDict):
    """Pricing details for a given SKU in search results."""

    __typename: Literal["SkuPrice"]
    basePrice: str
    basePriceValue: int
    campaignId: str | None
    currencyCode: str
    discountText: str | None
    discountedPrice: str
    discountedValue: int
    endTime: str | None
    isExclusive: bool
    isFree: bool
    isTiedToSubscription: bool
    qualifications: list[GameQualification] | None
    rewardId: str
    serviceBranding: list[str]
    skuId: str
    upsellServiceBranding: list[str]
    upsellText: str | None


class GameQualification(TypedDict):
    """Qualification metadata linked to discounted SKUs."""

    __typename: Literal["Qualification"]
    type: str
    value: str


def default_game_root_response() -> GameRootResponse:
    """Build a fresh GameRootResponse with “empty” defaults.

    - All literal strings are set to "" or their Literal value
    - All ints to 0, bools to False, lists to []
    - Contains two placeholder domain entries

    """

    def _default_domain() -> GameUniversalDomainSearchResponse:
        """Helper: empty placeholder for a single domain search response."""
        return {
            "__typename": "UniversalDomainSearchResponse",
            "domain": "",
            "domainTitle": "",
            "next": "",
            "searchResults": [],
            "totalResultCount": 0,
            "zeroState": False,
        }

    return {
        "data": {
            "universalContextSearch": {
                "__typename": "UniversalContextSearchResponse",
                "queryFrequency": {
                    "__typename": "QueryFrequency",
                    "filterDebounceMs": 0,
                    "searchDebounceMs": 0,
                },
                "results": [
                    _default_domain(),
                    _default_domain(),
                ],
            },
        }
    }
