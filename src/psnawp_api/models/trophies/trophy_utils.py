"""Provides helper functions for Trophy related classes."""

from __future__ import annotations

from psnawp_api.models.trophies.trophy_constants import TrophyRarity, TrophyType


def trophy_type_str_to_enum(trophy_type_str: str | None) -> TrophyType | None:
    """Converts a trophy type string to a :py:class:`~psnawp_api.models.trophies.trophy_constants.TrophyType` enum."""
    return TrophyType(trophy_type_str) if trophy_type_str is not None else None


def trophy_rarity_to_enum(trophy_rarity: int | None) -> TrophyRarity | None:
    """Converts a trophy rarity integer to a :py:class:`~psnawp_api.models.trophies.trophy_constants.TrophyRarity` enum."""
    return TrophyRarity(trophy_rarity) if trophy_rarity is not None else None
