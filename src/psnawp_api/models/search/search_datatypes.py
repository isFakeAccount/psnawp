"""Contains datatypes for search result endpoint."""

from __future__ import annotations

from typing import Any

from typing_extensions import NotRequired, TypedDict


class Highlight(TypedDict):
    """Represents highlighted search terms."""

    __typename: str
    name: list[str] | None


class Media(TypedDict):
    """Represents media assets associated with a product."""

    __typename: str
    role: str
    type: str
    url: str


class Qualification(TypedDict):
    """Represents qualifications for pricing or discounts."""

    __typename: str
    type: str
    value: str


class Price(TypedDict):
    """Represents pricing details of a product."""

    __typename: str
    basePrice: str
    basePriceValue: int
    campaignId: Any | None
    currencyCode: str
    discountText: Any | None
    discountedPrice: str
    discountedValue: int
    endTime: Any | None
    isExclusive: bool
    isFree: bool
    isTiedToSubscription: bool
    qualifications: list[Qualification] | None
    rewardId: str
    serviceBranding: list[str]
    skuId: str
    upsellServiceBranding: list[str]
    upsellText: Any | None


class DefaultProductOrResult(TypedDict):
    """Represents a product or search result with metadata."""

    __typename: str
    id: str
    invariantName: str
    itemType: str
    localizedStoreDisplayClassification: str | None
    media: list[Media]
    name: str
    platforms: list[str]
    price: Price
    storeDisplayClassification: None
    type: NotRequired[str]
    defaultProduct: NotRequired[DefaultProductOrResult]


class SearchResult(TypedDict):
    """Represents an individual search result entry."""

    __typename: str
    highlight: Highlight
    id: str
    result: DefaultProductOrResult


class Result(TypedDict):
    """Represents a paginated set of search results."""

    __typename: str
    domain: str
    domainTitle: str
    next: str
    searchResults: list[SearchResult]
    totalResultCount: int
    zeroState: bool


class UniversalContextSearch(TypedDict):
    """Represents search results across multiple domains."""

    __typename: str
    results: list[Result]


class UniversalDomainSearch(TypedDict):
    """Represents search results within a single domain."""

    __typename: str
    domain: str
    domainTitle: str
    next: str
    searchResults: list[SearchResult]
    totalResultCount: int
    zeroState: bool


class GameSearchResult(TypedDict):
    """Represents the overall structure of a game search response."""

    universalDomainSearch: NotRequired[UniversalDomainSearch]
    universalContextSearch: NotRequired[UniversalContextSearch]
