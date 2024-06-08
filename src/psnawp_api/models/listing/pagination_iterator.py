from __future__ import annotations

from abc import abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass
from typing import TYPE_CHECKING, Generator, Generic, Optional, TypeVar

if TYPE_CHECKING:
    from psnawp_api.core import Authenticator

T = TypeVar("T")


class PaginationIterator(Iterator[T], Generic[T]):
    """Iterator class for iterating over paginated API endpoints."""

    def __init__(self, *, authenticator: Authenticator, url: str, pagination_args: PaginationArguments):
        """Initialize the PaginationIterator.

        :param authenticator: An instance of Authenticator for making API requests.
        :param url: The URL of the endpoint.
        :param params: Dictionary of parameters to be passed in the API request.

        """
        self.authenticator = authenticator
        self._url = url
        self._pagination_args = pagination_args

        self.__iterator: Optional[Generator[T, None, None]] = None
        self._has_next = False
        self._total_item_count = 0

    def __iter__(self) -> PaginationIterator[T]:
        """Return the iterator object.

        :returns: The iterator object.

        """
        return self

    def __next__(self) -> T:
        if self.__iterator is None:
            self.__iterator = self.fetch_next_page()
        try:
            return self.__iterator.__next__()
        except StopIteration:  # If all items on single page have been yielded
            # If we run out of pages
            if not self._has_next:
                raise StopIteration

            # If limit is reached
            if self._pagination_args.total_limit is not None:
                if self._pagination_args.is_limit_reached():
                    raise StopIteration

            # If there are pages remaining and limit is not reached
            self.__iterator = self.fetch_next_page()
            return self.__next__()

    def __len__(self) -> int:
        return self._total_item_count

    @abstractmethod
    def fetch_next_page(self) -> Generator[T, None, None]:
        """Fetch the next page of items from the API.

        .. note::

            The implementation of this methods are also responsible for incrementing the offset using ``increment_offset()`` and setting the
            ``self._total_item_count``.

        """
        raise NotImplementedError("Subclasses must implement the fetch_next_page method")

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
    total_limit: Optional[int]
    page_size: int
    offset: int

    def get_params_dict(self) -> dict[str, int]:
        return {"limit": self.adjusted_page_size, "offset": self.offset}

    def increment_offset(self) -> None:
        self.offset += 1

    def is_limit_reached(self) -> bool:
        return self.offset == self.total_limit

    @property
    def adjusted_page_size(self) -> int:
        """Calculates the adjusted page size based on the total limit.

        If total_limit is None, returns the original page_size. If total_limit is less than page_size, returns total_limit.

        """
        if self.total_limit is None:
            return self.page_size
        return min(self.page_size, self.total_limit - self.offset)
