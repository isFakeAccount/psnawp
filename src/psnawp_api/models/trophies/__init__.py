"""Trophies package for the PlayStation API wrapper.

This package provides modules related to trophy data, including earned trophies, trophy titles, trophy groups, and user
progress.

Modules in this package include:

- Fetching and interacting with user trophy data.
- Accessing trophy metadata and groupings.
- Utilities for filtering or aggregating trophy information.

"""

from psnawp_api.models.trophies.trophy import (
    Trophy,
    TrophyIterator,
    TrophyWithProgress,
    TrophyWithProgressIterator,
)
from psnawp_api.models.trophies.trophy_constants import PlatformType, TrophySet
from psnawp_api.models.trophies.trophy_group import (
    TrophyGroupsSummary,
    TrophyGroupsSummaryBuilder,
    TrophyGroupSummary,
    TrophyGroupSummaryWithProgress,
)
from psnawp_api.models.trophies.trophy_summary import TrophySummary
from psnawp_api.models.trophies.trophy_titles import TrophyTitle, TrophyTitleIterator

__all__ = [
    "PlatformType",
    "Trophy",
    "TrophyGroupSummary",
    "TrophyGroupSummaryWithProgress",
    "TrophyGroupsSummary",
    "TrophyGroupsSummaryBuilder",
    "TrophyIterator",
    "TrophySet",
    "TrophySummary",
    "TrophyTitle",
    "TrophyTitleIterator",
    "TrophyWithProgress",
    "TrophyWithProgressIterator",
]
