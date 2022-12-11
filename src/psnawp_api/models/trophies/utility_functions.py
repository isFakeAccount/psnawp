from __future__ import annotations

from typing import Optional

from psnawp_api.models.trophies.trophy_constants import TrophyType, TrophyRarity


def trophy_type_str_to_enum(trophy_type_str: Optional[str]) -> Optional[TrophyType]:
    return TrophyType(trophy_type_str) if trophy_type_str is not None else None


def trophy_rarity_to_enum(trophy_rarity: Optional[int]) -> Optional[TrophyRarity]:
    return TrophyRarity(trophy_rarity) if trophy_rarity is not None else None
