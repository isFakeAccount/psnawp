"""Provides the PaginationIterator class."""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from psnawp_api.core import Authenticator

T = TypeVar("T")


class PaginationIterator(Iterator[T], Generic[T]):
    """An iterator for paginated API endpoints.

    This class simplifies pagination by handling iteration over API responses. Subclasses only need to implement the
    :py:meth:`~PaginationIterator.fetch_next_page` method, while this class manages the iteration logic.

    :var Authenticator authenticator: An instance of :py:class:`~psnawp_api.core.authenticator.Authenticator` used to
        authenticate and make HTTPS requests.
    :var str _url: URL for the paginated endpoint.
    :var PaginationArguments _pagination_args: Pagination-specific arguments, such as page size and limit, passed to the
        endpoint.
    :var Iterator[T] | None _per_page_iterator: A generator that iterates over items in the fetched page.
    :var bool _has_next: Indicates whether more pages are available. Is updated when :py:meth:`fetch_next_page` is
        called.
    :var int _total_item_count: The total number of items available in the paginated endpoint.

    .. warning::

        This class is not meant to be used directly.

    """

    def __init__(
        self,
        *,
        authenticator: Authenticator,
        url: str,
        pagination_args: PaginationArguments,
    ) -> None:
        """Initialize the PaginationIterator instance.

        :param authenticator: An instance of Authenticator for making API requests.
        :param url: The URL of the endpoint.
        :param pagination_args: Pagination-related arguments, such as page size and limit.

        """
        self.authenticator = authenticator
        self._url = url
        self._pagination_args = pagination_args

        self._per_page_iterator: Iterator[T] | None = None
        self._has_next = False
        self._total_item_count = 0

    def __iter__(self) -> PaginationIterator[T]:
        """Return the iterator object.

        :returns: The iterator object.

        """
        return self

    def __next__(self) -> T:
        """Return the next item in iterator.

        When we exhaust the iterator, fetch the next page from API until end page is reached.

        """
        if self._per_page_iterator is None:
            self._per_page_iterator = self.fetch_next_page()
        try:
            return self._per_page_iterator.__next__()
        except StopIteration:  # If all items on single page have been yielded
            # If we run out of pages
            if not self._has_next:
                raise StopIteration from None

            # If limit is reached
            if self._pagination_args.total_limit is not None and self._pagination_args.is_limit_reached():
                raise StopIteration from None

            # If there are pages remaining and limit is not reached
            self._per_page_iterator = self.fetch_next_page()
            return self.__next__()

    def __len__(self) -> int:
        """Return the total items that can be fetched from endpoint."""
        return self._total_item_count

    @abstractmethod
    def fetch_next_page(self) -> Iterator[T]:
        """Fetch the next page of items from the API.

        .. note::

            The implementation of this methods are also responsible for incrementing the offset using
            :py:meth:`~PaginationArguments.increment_offset()`, setting the
            :py:attr:`~PaginationIterator._total_item_count`, and updating the :py:attr:`~PaginationIterator._has_next`.

        """
        raise NotImplementedError(
            "Subclasses must implement the fetch_next_page method",
        )

    def set_offset(self, offset: int) -> None:
        """Set the offset parameter for the API request.

        :param offset: The offset value to set.

        """
        self._pagination_args.offset = offset

    def set_page_size(self, page_size: int) -> None:
        """Set the page size (limit) parameter for the API request.

        :param page_size: The page size value to set.

        """
        self._pagination_args.page_size = page_size


@dataclass
class PaginationArguments:
    """Class representing the arguments PlayStation API needs for paginating over list items.

    Used by the implementations of :py:class:`~PaginationIterator`.

    :var int | None total_limit: The maximum number of items to retrieve across all pages. If ``None``, there is no
        limit.
    :var int page_size: The number of items to fetch per page.
    :var int offset: The starting index for fetching items.

    """

    total_limit: int | None
    page_size: int
    offset: int

    def get_params_dict(self) -> dict[str, int]:
        """Converts the object into serializable dict that can be passed as HTTPs request param.

        :returns: dict containing pagination params

        """
        return {"limit": self.adjusted_page_size, "offset": self.offset}

    def increment_offset(self) -> None:
        """Helper method to increment the offset class member."""
        self.offset += 1

    def is_limit_reached(self) -> bool:
        """Helper method to determine if we have reached end of pagination."""
        return self.offset == self.total_limit

    @property
    def adjusted_page_size(self) -> int:
        """Calculates the adjusted page size based on the total limit.

        If total_limit is None, returns the original page_size. If total_limit is less than page_size, returns
        total_limit.

        """
        if self.total_limit is None:
            return self.page_size
        return min(self.page_size, self.total_limit - self.offset)
