"""Search package for the PlayStation API wrapper.

This package provides search modules that let users search for video games, add-ons, and other PlayStation Network
users.

Modules in this package include:

- Search request handling.
- Query construction and parameter management.
- Models for parsing and returning search results.

"""

from psnawp_api.models.search.games_search_datatypes import GameSearchResultItem, SearchDomain
from psnawp_api.models.search.universal_search import UniversalSearch
from psnawp_api.models.search.users_result_datatypes import UserSearchResultItem

__all__ = [
    "GameSearchResultItem",
    "SearchDomain",
    "UniversalSearch",
    "UserSearchResultItem",
]
