from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from psnawp_api.core import PSNAWPForbidden
from psnawp_api.models.trophies.trophy_constants import TrophySet
from psnawp_api.utils import API_PATH, BASE_PATH

if TYPE_CHECKING:
    from psnawp_api.core import Authenticator


@dataclass(frozen=True)
class TrophySummary:
    """Class representing the overall summary of the number of trophies earned by a user."""

    account_id: str
    "The ID of the account being accessed"
    trophy_level: int
    "The overall trophy level"
    progress: int
    "Percentage process towards the next trophy level"
    tier: int
    "The tier this trophy level is in"
    earned_trophies: TrophySet
    "Number of trophies which have been earned by type"

    @classmethod
    def from_endpoint(cls, authenticator: Authenticator, account_id: str) -> TrophySummary:
        """Retrieve an overall summary of the number of trophies earned for a user broken down by

        - type
        - overall trophy level
        - progress towards the next level
        - current tier

        :returns: TrophySummary object with all the information
        :rtype: TrophySummary

        :raises PSNAWPForbidden: If the user's profile is private

        """
        try:
            response = authenticator.get(url=f"{BASE_PATH['trophies']}{API_PATH['trophy_summary'].format(account_id=account_id)}").json()
        except PSNAWPForbidden as forbidden:
            raise PSNAWPForbidden("The target user has set their trophies visibility to private.") from forbidden
        return cls(
            account_id=account_id,
            trophy_level=response.get("trophyLevel", -1),
            progress=response.get("progress", -1),
            tier=response.get("tier", -1),
            earned_trophies=TrophySet(
                **response.get(
                    "earnedTrophies",
                    {"bronze": 0, "silver": 0, "gold": 0, "platinum": 0},
                )
            ),
        )
