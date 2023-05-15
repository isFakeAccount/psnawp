from __future__ import annotations

from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Iterator, Any

from attrs import define

from psnawp_api.core.psnawp_exceptions import PSNAWPForbidden
from psnawp_api.utils.endpoints import BASE_PATH, API_PATH
from psnawp_api.utils.misc import iso_format_to_datetime, play_duration_to_timedelta
from psnawp_api.utils.request_builder import RequestBuilder


class PlatformCategory(Enum):
    UNKNOWN = "unknown"
    PS4 = "ps4_game"
    PS5 = "ps5_native_game"


def platform_str_to_enum(platform_type_str: Optional[str]) -> PlatformCategory:
    return PlatformCategory(platform_type_str) if platform_type_str is not None else PlatformCategory.UNKNOWN


@define(frozen=True)
class TitleStats:
    """A class that represents a PlayStation Video Game Play Time Stats."""

    # Title and Stats Data
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
    total_items_count: Optional[int]
    "Total Number of Titles a user own"

    @classmethod
    def from_dict(cls, game_stats_dict: dict[str, Any]) -> TitleStats:
        title_instance = cls(
            title_id=game_stats_dict.get("titleId"),
            name=game_stats_dict.get("name"),
            image_url=game_stats_dict.get("imageUrl"),
            category=platform_str_to_enum(game_stats_dict.get("category")),
            play_count=game_stats_dict.get("playCount"),
            first_played_date_time=iso_format_to_datetime(game_stats_dict.get("firstPlayedDateTime")),
            last_played_date_time=iso_format_to_datetime(game_stats_dict.get("lastPlayedDateTime")),
            play_duration=play_duration_to_timedelta(game_stats_dict.get("playDuration")),
            total_items_count=game_stats_dict.get("totalItemCount"),
        )
        return title_instance

    @classmethod
    def from_endpoint(cls, request_builder: RequestBuilder, account_id: str, limit: Optional[int], offset: Optional[int] = 0) -> Iterator[TitleStats]:

        limit_per_page = min(limit, 200) if limit is not None else 200
        params: dict[str, Any] = {"categories": "ps4_game,ps5_native_game", "limit": limit_per_page, "offset": offset}

        while True:
            params["offset"] = offset
            try:
                response = request_builder.get(
                    url=f"{BASE_PATH['games_list']}{API_PATH['user_game_data'].format(account_id=account_id)}",
                    params=params,
                ).json()
            except PSNAWPForbidden as forbidden:
                raise PSNAWPForbidden("The following user has made their profile private.") from forbidden

            titles: list[dict[str, Any]] = response.get("titles")

            per_page_items = 0
            for title in titles:
                title_instance = TitleStats.from_dict({**title, "totalItemCount": response.get("totalItemCount")})
                yield title_instance
                per_page_items += 1

            if limit is not None:
                limit -= per_page_items
                params["limit"] = min(limit, limit_per_page)

                # If limit is reached
                if limit <= 0:
                    break

            offset = response.get("nextOffset") or 0
            # If there is not more offset, we've reached the end
            if offset <= 0:
                break
