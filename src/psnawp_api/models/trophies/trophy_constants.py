from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class TrophyType(Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


class PlatformType(Enum):
    UNKNOWN = "UNKNOWN"
    PS_VITA = "PSVITA"
    PS3 = "PS3"
    PS4 = "PS4"
    PS5 = "PS5"
    PSPC = "PSPC"

    @classmethod
    def _missing_(cls, value: object) -> "PlatformType":
        _ = value
        return cls.UNKNOWN


class TrophyRarity(Enum):
    ULTRA_RARE = 0
    VERY_RARE = 1
    RARE = 2
    COMMON = 3


@dataclass(frozen=True)
class TrophySet:
    bronze: int = field(default=0)
    silver: int = field(default=0)
    gold: int = field(default=0)
    platinum: int = field(default=0)
