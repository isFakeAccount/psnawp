"""Listing package for the PlayStation API wrapper.

This package provides generic support for paginated responses returned by the API. It includes abstractions to make
paginated data iterable and easier to work with.

Modules in this package include:

- Generic pagination utilities.
- Iterable wrappers for list-style API endpoints.
- Internal helpers for handling cursor- or offset-based pagination.

"""

from psnawp_api.models.listing.pagination_iterator import (
    PaginationArguments,
    PaginationIterator,
)

__all__ = [
    "PaginationArguments",
    "PaginationIterator",
]
