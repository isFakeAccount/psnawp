from __future__ import annotations

from typing import Any, Optional, Literal

from psnawp_api.models.trophies.trophy_group import (
    TrophyGroup,
    TrophyGroupSummary,
    PlatformType,
)
from psnawp_api.models.trophies.trophy_set import TrophySet
from psnawp_api.utils.endpoints import BASE_PATH, API_PATH
from psnawp_api.utils.request_builder import RequestBuilder


class Title:
    def __init__(self, request_builder: RequestBuilder, title_id: str):
        """The Title class provides the information and methods for retrieving.

        .. note::

            This class is intended to be interfaced with through PSNAWP.

        :param request_builder: The instance of RequestBuilder. Used to make
            HTTPRequests.
        :type request_builder: RequestBuilder
        :param title_id: unique id of game.
        :type title_id: str

        """
        self._request_builder = request_builder
        self.title_id = title_id

    def trophies(self, trophy_group_id: str = "all", limit: Optional[int] = None):
        ...

    def trophy_groups(
            self, platform: Literal["PS Vita", "PS3", "PS4", "PS5"]
    ) -> TrophyGroupSummary:
        """Retrieves the trophy groups for a title. This is most commonly seen in games which have expansions where additional trophies are added.

        :param platform: The platform this title belongs to.

        :returns: TrophyGroupSummary object containing title and title groups trophy
            information.
        :rtype: TrophyGroupSummary

        """

        service_name = "trophy2" if platform == "PS5" else "trophy"
        params = {"npServiceName": service_name}
        response = self._request_builder.get(
            url=f"{BASE_PATH['trophies']}{API_PATH['title_trophy_group'].format(np_communication_id=self.title_id)}",
            params=params,
        ).json()
        trophy_groups = []
        for trophy_group in response.get("trophyGroups"):
            trophy_group_instance = TrophyGroup(
                trophy_group_id=trophy_group.get("trophyGroupId"),
                trophy_group_name=trophy_group.get("trophyGroupName"),
                trophy_group_detail=trophy_group.get("trophyGroupDetail"),
                trophy_group_icon_url=trophy_group.get("trophyGroupIconUrl"),
                defined_trophies=TrophySet(**trophy_group.get("definedTrophies")),
            )
            trophy_groups.append(trophy_group_instance)

        trophy_group_summary = TrophyGroupSummary(
            trophy_set_version=response.get("trophySetVersion"),
            trophy_title_name=response.get("trophyTitleName"),
            trophy_title_detail=response.get("trophyTitleDetail"),
            trophy_title_icon_url=response.get("trophyTitleIconUrl"),
            trophy_title_platform=PlatformType(response.get("trophyTitlePlatform")),
            defined_trophies=TrophySet(**response.get("definedTrophies")),
            trophy_groups=trophy_groups,
        )
        return trophy_group_summary

    def get_details(self) -> dict[str, Any]:
        """Get title details.

        :returns: A dict containing info similar to what is shown below (Not all values
            are shown because of space limitations):
        :rtype: dict[str, Any]

            .. literalinclude:: examples/title/get_title_details.json
                :language: json

        """

        param = {"age": 99, "country": "US", "language": "en-US"}

        response: dict[str, Any] = self._request_builder.get(
            url=f"{BASE_PATH['game_titles']}{API_PATH['title_concept'].format(title_id=self.title_id)}",
            params=param,
        ).json()

        return response
