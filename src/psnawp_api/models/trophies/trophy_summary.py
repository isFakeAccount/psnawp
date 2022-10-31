from __future__ import annotations

from psnawp_api.core.psnawp_exceptions import PSNAWPForbidden
from psnawp_api.models.trophies.trophy_set import TrophySet
from psnawp_api.utils.endpoints import BASE_PATH, API_PATH
from psnawp_api.utils.request_builder import RequestBuilder


class TrophySummary:
    def __init__(self, request_builder: RequestBuilder, account_id: str):
        """Retrieve an overall summary of the number of trophies earned for a user broken down by

        - type
        - overall trophy level
        - progress towards the next level
        - current tier

        .. note::

            This class is intended to be interfaced with through PSNAWP.

        :param request_builder: The instance of RequestBuilder. Used to make
            HTTPRequests.
        :type request_builder: RequestBuilder
        :param account_id: The account whose trophy list is being accessed
        :type account_id: str

        :raises: ``PSNAWPForbidden`` If the user's profile is private

        """
        self._request_builder = request_builder
        self._account_id = account_id
        self.trophy_level = -1
        "The overall trophy level"
        self.progress = -1
        "Percentage process towards the next trophy level"
        self.tier = -1
        "The tier this trophy level is in"
        self.earned_trophies = TrophySet()
        "Number of trophies which have been earned by type"
        try:
            self.__get_trophy_summary()
        except PSNAWPForbidden as forbidden:
            raise PSNAWPForbidden(
                "The target user has set their trophies visibility to private."
            ) from forbidden

    def __get_trophy_summary(self):
        """Retrieve an overall summary of the number of trophies earned for a user broken down by

        - type
        - overall trophy level
        - progress towards the next level
        - current tier

        :raises: ``PSNAWPForbidden`` If the user's profile is private

        """
        response = self._request_builder.get(
            url=f"{BASE_PATH['trophies']}{API_PATH['trophy_summary'].format(account_id=self._account_id)}"
        ).json()
        self.trophy_level = response.get("trophyLevel", -1)
        self.progress = response.get("progress", -1)
        self.tier = response.get("tier", -1)
        self.earned_trophies = TrophySet(**response.get("earnedTrophies"))

    def __repr__(self):
        return f"<User account_id:{self._account_id}>"

    def __str__(self):
        return (
            f"Trophy Level: {self.trophy_level} "
            f"Progress: {self.progress} "
            f"Tier: {self.tier} "
            f"Bronze: {self.earned_trophies.bronze} "
            f"Silver: {self.earned_trophies.silver} "
            f"Gold: {self.earned_trophies.gold} "
            f"Platinum: {self.earned_trophies.platinum}"
        )
