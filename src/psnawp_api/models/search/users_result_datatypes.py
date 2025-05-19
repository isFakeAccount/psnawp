"""Contains datatypes for users search result endpoint."""

from __future__ import annotations

from typing import Literal, TypedDict


class UserRootResponse(TypedDict):
    """Top-level wrapper for a user search GraphQL response."""

    data: UserContextContainer


class UserContextContainer(TypedDict):
    """Holds the universal context search portion of the response."""

    universalContextSearch: UserUniversalContextSearchResponse


class UserDomainContainer(TypedDict):
    """Wraps the `universalDomainSearch` payload, which may either carry only cursors or full result lists."""

    universalDomainSearch: UserUniversalDomainSearchResponse


class UserUniversalContextSearchResponse(TypedDict):
    """Aggregated search results across user-related domains."""

    __typename: Literal["UniversalContextSearchResponse"]
    queryFrequency: UserQueryFrequency
    results: list[UserUniversalDomainSearchResponse]


class UserQueryFrequency(TypedDict):
    """Debounce timing settings for search queries."""

    __typename: Literal["QueryFrequency"]
    filterDebounceMs: int
    searchDebounceMs: int


class UserUniversalDomainSearchResponse(TypedDict):
    """Search results scoped to a single user-related domain."""

    __typename: Literal["UniversalDomainSearchResponse"]
    domain: str
    domainTitle: str
    next: str
    searchResults: list[UserSearchResultItem]
    totalResultCount: int
    zeroState: bool


class UserSearchResultItem(TypedDict):
    """An individual search result entry for a user query."""

    __typename: Literal["SearchResultItem"]
    highlight: PlayerHighlight
    id: str
    result: Player
    resultOriginFlag: list[str] | None


class PlayerHighlight(TypedDict):
    """Highlighting metadata for player name and ID fields."""

    __typename: Literal["PlayerHighlight"]
    firstName: list[str]
    lastName: list[str]
    middleName: str | None
    onlineId: list[str]
    verifiedUserName: str | None


class Player(TypedDict):
    """Represents a player's public profile information."""

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


def default_user_root_response() -> UserRootResponse:
    """Returns a fresh UserRootResponse dict.

    - all Literal __typename fields are set to their exact value
    - all str fields == ""
    - all int fields == 0 (for queryFrequency)
    - all bool fields == False
    - all list fields == []
    - contains two placeholder UserUniversalDomainSearchResponse entries

    """

    def _default_domain() -> UserUniversalDomainSearchResponse:
        """Helper: empty placeholder for a single user-domain search response."""
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
                ],
            },
        }
    }
