"""Provides types for the data received by trophy endpoints."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Literal


class TrophyType(Enum):
    """Represents the type of a PlayStation trophy.

    Trophies are awarded for in-game achievements and come in four types.

    """

    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


class PlatformType(Enum):
    """Represents the PlayStation platform associated with trophies.

    This enum is used in API responses and requests to specify which PlayStation system a trophy belongs to. If an
    unrecognized value is provided, it defaults to :py:attr:`PlatformType.UNKNOWN`.

    """

    UNKNOWN = "UNKNOWN"
    PS_VITA = "PSVITA"
    PS3 = "PS3"
    PS4 = "PS4"
    PS5 = "PS5"
    PSPC = "PSPC"

    @classmethod
    def _missing_(cls, value: object) -> PlatformType:
        """Handles unknown values by returning :py:attr:`PlatformType.UNKNOWN` instead of raising an error."""
        _ = value
        return cls.UNKNOWN

    def get_trophy_service_name(self) -> Literal["trophy", "trophy2"]:
        """Gets the appropriate trophy service name based on the game platform type."""
        return "trophy2" if self == PlatformType.PS5 else "trophy"


class TrophyRarity(Enum):
    """Represents the rarity of a PlayStation trophy.

    The rarity of a trophy is determined by how many users have earned it. Lower values indicate rarer trophies.

    """

    ULTRA_RARE = 0
    VERY_RARE = 1
    RARE = 2
    COMMON = 3


@dataclass(frozen=True)
class TrophySet:
    """Represents a collection of PlayStation trophies.

    Used in API requests and responses to indicate the number of trophies of each type a game or player has earned.

    """

    bronze: int = field(default=0)
    silver: int = field(default=0)
    gold: int = field(default=0)
    platinum: int = field(default=0)
