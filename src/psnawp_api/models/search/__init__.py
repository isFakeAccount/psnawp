"""Search package for the PlayStation API wrapper.

This package provides search modules that let users search for video games, add-ons, and other PlayStation Network
users.

Modules in this package include:

- Search request handling.
- Query construction and parameter management.
- Models for parsing and returning search results.

"""

from psnawp_api.models.search.universal_search import SearchDomain, UniversalSearch

__all__ = [
    "SearchDomain",
    "UniversalSearch",
]
