"""Provides Class for Trophy Summary."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from psnawp_api.core import PSNAWPForbiddenError
from psnawp_api.models.trophies.trophy_constants import TrophySet
from psnawp_api.utils import API_PATH, BASE_PATH

if TYPE_CHECKING:
    from psnawp_api.core import Authenticator


@dataclass(frozen=True)
class TrophySummary:
    """Class representing the overall summary of the number of trophies earned by a user.

    To create instance of this class, use the class method :py:meth:`TrophySummary.from_endpoint`

    :var str account_id: The ID of the account being accessed.
    :var int trophy_level: The overall trophy level.
    :var int progress: Percentage process towards the next trophy level.
    :var int tier: The tier this trophy level is in.
    :var TrophySet earned_trophies: Number of trophies which have been earned by type.

    .. note::

        This class is intended to be used via Client or User Class. See
        :py:meth:`psnawp_api.models.client.Client.trophy_summary` or
        :py:meth:`psnawp_api.models.user.User.trophy_summary` to create an instance of this class.

    """

    account_id: str
    trophy_level: int
    progress: int
    tier: int
    earned_trophies: TrophySet

    @classmethod
    def from_endpoint(
        cls,
        authenticator: Authenticator,
        account_id: str,
    ) -> TrophySummary:
        """Retrieve an overall summary of the number of trophies earned for a user broken down by.

        - type
        - overall trophy level
        - progress towards the next level
        - current tier

        :returns: TrophySummary object with all the information

        :raises PSNAWPForbiddenError: If the user's profile is private

        """
        try:
            response = authenticator.get(
                url=f"{BASE_PATH['trophies']}{API_PATH['trophy_summary'].format(account_id=account_id)}",
            ).json()
        except PSNAWPForbiddenError as forbidden:
            raise PSNAWPForbiddenError(
                "The target user has set their trophies visibility to private.",
            ) from forbidden
        return cls(
            account_id=account_id,
            trophy_level=response.get("trophyLevel", -1),
            progress=response.get("progress", -1),
            tier=response.get("tier", -1),
            earned_trophies=TrophySet(
                **response.get(
                    "earnedTrophies",
                    {"bronze": 0, "silver": 0, "gold": 0, "platinum": 0},
                ),
            ),
        )
