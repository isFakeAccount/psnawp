"""Contains datatypes for users search result endpoint."""

from typing import Literal, TypedDict


class QueryFrequencyDict(TypedDict):
    """Represents debounce timing for query filtering and searching."""

    __typename: Literal["QueryFrequency"]
    filterDebounceMs: int
    searchDebounceMs: int


class PlayerHighlightDict(TypedDict):
    """Highlight snippets for various player name fields."""

    __typename: Literal["PlayerHighlight"]
    firstName: list[str | None]
    lastName: list[str | None]
    middleName: str | None
    onlineId: list[str]
    verifiedUserName: str | None


class PlayerDict(TypedDict):
    """Detailed player information returned in a search result."""

    __typename: Literal["Player"]
    accountId: str
    avatarUrl: str
    displayName: str
    displayNameHighlighted: list[str]
    firstName: str
    id: str
    isPsPlus: bool
    itemType: str
    lastName: str
    middleName: str | None
    onlineId: str
    onlineIdHighlighted: list[str]
    profilePicUrl: str
    relationshipState: str | None


class SearchResultItemDict(TypedDict):
    """One item in the array of search results."""

    __typename: Literal["SearchResultItem"]
    highlight: PlayerHighlightDict
    id: str
    result: PlayerDict
    resultOriginFlag: str | None


class UniversalDomainSearchResponseDict(TypedDict):
    """Response for a single search domain (e.g. users, games)."""

    __typename: Literal["UniversalDomainSearchResponse"]
    domain: str
    domainTitle: str
    next: str
    searchResults: list[SearchResultItemDict]
    totalResultCount: int
    zeroState: bool


class UniversalContextSearchDict(TypedDict):
    """Top-level search response container."""

    __typename: Literal["UniversalContextSearchResponse"]
    queryFrequency: QueryFrequencyDict
    results: list[UniversalDomainSearchResponseDict]


class UsersSearchResults(TypedDict):
    """Holds the `universalContextSearch` field."""

    universalContextSearch: UniversalContextSearchDict
