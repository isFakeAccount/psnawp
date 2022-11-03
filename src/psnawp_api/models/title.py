from __future__ import annotations

from typing import Any

from psnawp_api.utils.endpoints import BASE_PATH, API_PATH
from psnawp_api.utils.request_builder import RequestBuilder


class Title:
    def __init__(self, request_builder: RequestBuilder, title_id: str):
        """The Title class provides the information and methods for retrieving .

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

    def trophies(self):
        ...

    def trophy_groups(self, trophy_group_id: str = "all"):
        ...

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
