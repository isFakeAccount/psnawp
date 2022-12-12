from __future__ import annotations
from enum import Enum

from datetime import datetime
from typing import Optional, Iterator, Any
from attrs import define

from psnawp_api.core.psnawp_exceptions import PSNAWPForbidden
from psnawp_api.utils.endpoints import BASE_PATH, API_PATH
from psnawp_api.utils.request_builder import RequestBuilder


class PlatformType(Enum):
    UNKNOWN = "unknown"
    PS4 = "ps4_game"
    PS5 = "ps5_native_game"


def platform_str_to_enum(platform_type_str: Optional[str]) -> PlatformType:
    return PlatformType(platform_type_str) if platform_type_str is not None else PlatformType.UNKNOWN


@define(frozen=True)
class TitleStats:
    """A class that represents a PlayStation Video Game Play Time Stats."""

    # Title and Stats Data
    title_id: Optional[str]
    "Game title name"
    name: Optional[str]
    "Image URL"
    image_url: Optional[str]
    "Platform Type"
    platform: Optional[PlatformType]
    "Number of times the game has been played"
    play_count: Optional[int]
    "First time the game was played"
    first_played_date_time: Optional[datetime]
    "Last time the game was played"
    last_played_date_time: Optional[datetime]
    "Total time the game has been played. Example: PT1H51M21S"
    play_duration: Optional[str]

    @classmethod
    def from_dict(cls, game_stats_dict: dict[str, Any]) -> TitleStats:
        title_instance = cls(
            title_id=game_stats_dict.get("titleId"),
            name=game_stats_dict.get("name"),
            image_url=game_stats_dict.get("imageUrl"),
            platform=platform_str_to_enum(game_stats_dict.get("category")),
            play_count=game_stats_dict.get("playCount"),
            first_played_date_time=game_stats_dict.get("firstPlayedDateTime"),
            last_played_date_time=game_stats_dict.get("lastPlayedDateTime"),
            play_duration=game_stats_dict.get("playDuration"),
        )
        return title_instance

    @classmethod
    def from_endpoint(cls, request_builder: RequestBuilder, account_id: str, limit: Optional[int] = 100) -> Iterator[TitleStats]:

        offset = 0
        params: dict[str, Any] = {"categories": "ps4_game,ps5_native_game", "limit": limit, "offset": offset}

        while True:
            params["offset"] = offset
            try:
                response = request_builder.get(
                    url=f"{BASE_PATH['games_list']}{API_PATH['user_game_data'].format(account_id=account_id)}",
                    params=params,
                ).json()
            except PSNAWPForbidden as forbidden:
                raise PSNAWPForbidden("The following user has made profile private.") from forbidden

            per_page_items = 0
            titles: list[dict[str, Any]] = response.get("titles")

            for title in titles:
                title_instance = TitleStats.from_dict(title)
                yield title_instance
                per_page_items += 1

            next_offset = response.get("nextOffset", None)
            offset = next_offset if next_offset is not None else 0
            # If there is not more offset, we've reached the end
            if offset <= 0:
                break
