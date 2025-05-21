"""Provides endpoint to fetch the info from Game Entitlements info for client."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from typing_extensions import Self

from psnawp_api.models.listing import PaginationArguments, PaginationIterator
from psnawp_api.utils.endpoints import API_PATH, BASE_PATH

if TYPE_CHECKING:
    from collections.abc import Generator

    from psnawp_api.core import Authenticator


class GameEntitlementsIterator(PaginationIterator[dict[str, Any]]):
    """An iterator for retrieving the authenticated user's game entitlements (owned games) from the PlayStation Network.

    .. note::

        This class retrieves only PS4 and PS5 game entitlements, as the underlying API endpoints accessed via the
        PlayStation Android app are limited to these platforms.

    :var Authenticator authenticator: An instance of :py:class:`~psnawp_api.core.authenticator.Authenticator` used to
        authenticate and make HTTPS requests.
    :var str title_ids: Comma-separated string of title IDs to filter and check if the client owns any of the specified
        titles.

    """

    def __init__(
        self,
        authenticator: Authenticator,
        url: str,
        pagination_args: PaginationArguments,
        title_ids: str,
    ) -> None:
        """Init for GameEntitlementsIterator."""
        super().__init__(
            authenticator=authenticator,
            url=url,
            pagination_args=pagination_args,
        )

        self.title_ids = title_ids

    def fetch_next_page(self) -> Generator[dict[str, Any], None, None]:
        """Fetches the next page of Entitlements objects from the API.

        :yield: A generator yielding Entitlements objects.

        """
        params = {
            "entitlementType": "1,2,3,4,5",
            "fields": "titleMeta,gameMeta,conceptMeta,rewardMeta,rewardMeta.retentionPolicy,rewardMeta.rewardMembershipType",
            "gameMetaPackageType": "PSGD,PS4GD",
            "titleId": self.title_ids,
        } | self._pagination_args.get_params_dict()

        response = self.authenticator.get(
            url=self._url,
            params=params,
        ).json()
        self._total_item_count = response.get("totalResults", 0)

        entitlements: list[dict[str, Any]] = response.get("entitlements")
        for entitlement in entitlements:
            self._pagination_args.increment_offset()
            yield entitlement

        if (self._pagination_args.total_limit is not None and (self._pagination_args.total_limit > self._pagination_args.offset)) or (
            self._total_item_count > self._pagination_args.offset
        ):
            self._has_next = True
        else:
            self._has_next = False

    @classmethod
    def from_endpoint(cls, authenticator: Authenticator, pagination_args: PaginationArguments, title_ids: str) -> Self:
        """Creates an instance of GameEntitlementsIterator from the given endpoint.

        :param authenticator: The Authenticator instance used for making authenticated requests to the API.
        :param pagination_args: Arguments for handling pagination, including limit, offset, and page size.
        :param title_ids: Comma-separated string of title IDs to filter and check if the client owns any of the
            specified titles.

        :returns: An instance of GameEntitlementsIterator.

        """
        url = f"{BASE_PATH['psn_np_mobile_base_url']}{API_PATH['entitlements']}"
        return cls(
            authenticator=authenticator,
            url=url,
            pagination_args=pagination_args,
            title_ids=title_ids,
        )
