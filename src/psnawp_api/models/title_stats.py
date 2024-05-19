from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Generator, Optional

from typing_extensions import Self

from psnawp_api.core import RequestBuilder
from psnawp_api.models.listing import PaginationArguments, PaginationIterator
from psnawp_api.utils.endpoints import API_PATH, BASE_PATH
from psnawp_api.utils.misc import iso_format_to_datetime


class PlatformCategory(Enum):
    UNKNOWN = "unknown"
    PS4 = "ps4_game"
    PS5 = "ps5_native_game"

    @classmethod
    def _missing_(cls, value: object) -> "PlatformCategory":
        _ = value
        return cls.UNKNOWN


PT_REGEX = re.compile(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?")


def play_duration_to_timedelta(play_duration: Optional[str]) -> timedelta:
    """Provides a timedelta object for the play duration PSN sends. If for some reason the string is malformed or None, timedelta will return 0

    Valid patters: PT243H18M48S, PT21M18S, PT18H, PT18H20S, PT4H21M

    :param play_duration: String from API
    :type play_duration: Optional[str]

    :returns: String parsed into a timedelta object
    :rtype: timedelta

    .. note::

        PSN API returns the duration in this format: PT243H18M48S. The maximum time Unit is Hours, it does not extend to Days or Months.

    """
    hours = 0
    minutes = 0
    seconds = 0

    if play_duration:
        match = re.search(PT_REGEX, play_duration)
        if not match:
            return timedelta(hours=hours, minutes=minutes, seconds=seconds)

        hours = int(match.group(1)) if match.group(1) else 0
        minutes = int(match.group(2)) if match.group(2) else 0
        seconds = int(match.group(3)) if match.group(3) else 0

    return timedelta(hours=hours, minutes=minutes, seconds=seconds)


@dataclass(frozen=True)
class TitleStats:
    """A class that represents a PlayStation Video Game Play Time Stats."""

    title_id: Optional[str]
    "Game title id"
    name: Optional[str]
    "Game title name"
    image_url: Optional[str]
    "Image URL"
    category: Optional[PlatformCategory]
    "Category/Platform Type"
    play_count: Optional[int]
    "Number of times the game has been played"
    first_played_date_time: Optional[datetime]
    "First time the game was played"
    last_played_date_time: Optional[datetime]
    "Last time the game was played"
    play_duration: Optional[timedelta]
    "Total time the game has been played. Example: PT1H51M21S"

    @classmethod
    def from_dict(cls, game_stats_dict: dict[str, Any]) -> TitleStats:
        title_instance = cls(
            title_id=game_stats_dict.get("titleId"),
            name=game_stats_dict.get("name"),
            image_url=game_stats_dict.get("imageUrl"),
            category=PlatformCategory(game_stats_dict.get("category")),
            play_count=game_stats_dict.get("playCount"),
            first_played_date_time=iso_format_to_datetime(game_stats_dict.get("firstPlayedDateTime")),
            last_played_date_time=iso_format_to_datetime(game_stats_dict.get("lastPlayedDateTime")),
            play_duration=play_duration_to_timedelta(game_stats_dict.get("playDuration")),
        )
        return title_instance


class TitleStatsListing(PaginationIterator[TitleStats]):
    def __init__(self, *, request_builder: RequestBuilder, url: str, pagination_args: PaginationArguments) -> None:
        super().__init__(request_builder=request_builder, url=url, pagination_args=pagination_args)

    def fetch_next_page(self) -> Generator[TitleStats, None, None]:
        response = self._request_builder.get(url=self._url, params=self._pagination_args.get_params_dict()).json()
        titles: list[dict[str, Any]] = response.get("titles")
        for title in titles:
            title_instance = TitleStats.from_dict(title)
            self._total_item_count = response["totalItemCount"]
            self._pagination_args.increment_offset()
            yield title_instance

        offset = response.get("nextOffset") or 0
        if offset > 0:
            self._has_next = True
        else:
            self._has_next = False

    @classmethod
    def from_endpoint(cls, request_builder: RequestBuilder, account_id: str, pagination_args: PaginationArguments) -> Self:
        url = f"{BASE_PATH['games_list']}{API_PATH['user_game_data'].format(account_id=account_id)}"
        return cls(request_builder=request_builder, url=url, pagination_args=pagination_args)
