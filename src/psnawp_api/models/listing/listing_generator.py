from __future__ import annotations

from typing import Any, cast, Iterator, Dict

from psnawp_api.utils.request_builder import RequestBuilder


class ListingGenerator(Iterator[Dict[str, Any]]):
    """Iterator class for generating a list of items from an endpoint."""

    def __init__(self, *, request_builder: RequestBuilder, url: str, listing_name: str, params: dict[str, str | int]):
        """Initialize the ListingGenerator.

        :param request_builder: An instance of RequestBuilder for making API requests.
        :type request_builder: RequestBuilder
        :param url: The URL of the endpoint.
        :type url: str
        :param params: Dictionary of parameters to be passed in the API request.
        :type params: dict[str, str | int]

        """
        self._request_builder = request_builder
        self._url = url
        self._listing_name = listing_name
        self._params = params

        self._index = 0
        self._response: dict[str, Any] = {}
        self._has_next = True

    def __iter__(self) -> ListingGenerator:
        """Return the iterator object.

        :returns: The iterator object.

        """
        return self

    def __next__(self) -> dict[str, Any]:
        """Return the next item from the iterator.

        :returns: The next item from the iterator.

        :raises: If there are no more items in the iterator.

        """
        items_list = self._response.get(self._listing_name, [])
        if self._index >= len(items_list):
            if not self._has_next:
                raise StopIteration
            self._fetch_next_page()
            self._index = 0

        items_list = self._response.get(self._listing_name, [])
        if items_list:
            self._index += 1
            return {"item": items_list[self._index - 1], **self._response}
        else:
            raise StopIteration

    def _fetch_next_page(self) -> None:
        """Fetch the next page of items from the API."""
        self._response = self._request_builder.get(url=self._url, params=self._params).json()
        self._params["offset"] = self._response.get("nextOffset") or 0  # nextOffset is None when the list ends
        self._has_next = cast(int, self._params["offset"]) > 0

    def set_offset(self, offset: int) -> None:
        """Set the offset parameter for the API request.

        :param offset: The offset value to set.
        :type offset: int

        """
        self._params["offset"] = offset
        self._response[self._listing_name] = []

    def set_page_size(self, page_size: int) -> None:
        """Set the page size (limit) parameter for the API request.

        :param page_size: The page size value to set.
        :type page_size: int

        """
        self._params["limit"] = page_size
        self._response[self._listing_name] = []
