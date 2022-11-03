from __future__ import annotations

from typing import Optional, Any, Iterator

from psnawp_api.core.psnawp_exceptions import (
    PSNAWPNotFound,
    PSNAWPForbidden,
    PSNAWPBadRequest,
)
from psnawp_api.models.trophies.trophy_summary import TrophySummary
from psnawp_api.models.trophies.trophy_titles import TrophyTitles, TitleTrophySummary
from psnawp_api.utils.endpoints import BASE_PATH, API_PATH
from psnawp_api.utils.request_builder import RequestBuilder


class User:
    """This class will contain the information about the PSN ID you passed in when creating object"""

    def __init__(
        self,
        request_builder: RequestBuilder,
        online_id: Optional[str],
        account_id: Optional[str],
    ):
        """Constructor of Class User. Creates user object using online id or account id.

        .. note::

            This class is intended to be interfaced with through PSNAWP.

        :param request_builder: Used to call http requests.
        :type request_builder: RequestBuilder
        :param online_id: Online ID (GamerTag) of the user.
        :type online_id: str
        :param account_id: Account ID of the user.
        :type account_id: str

        :raises: ``PSNAWPIllegalArgumentError`` If both online_id and account_id are not
            provided.

        :raises: ``PSNAWPNotFound`` If the online id or account id is not valid/found.

        """
        self._request_builder = request_builder
        self.online_id = online_id
        self.account_id = account_id
        self._prev_online_id = online_id

        if self.online_id is not None:
            profile = self._online_id_to_account_id()
            self.account_id = profile["profile"]["accountId"]
            self.online_id = profile["profile"].get(
                "currentOnlineId", profile["profile"]["onlineId"]
            )
        elif self.account_id is not None:
            profile = self.profile()
            self.online_id = profile["onlineId"]

    @property
    def prev_online_id(self) -> str:
        """Gets the previous online ID of the user.

        Note: Playstation allows you to look up a user using old online id as long as it
        is not taken by another player. This might be same as ``online_id`` depending on
        user.

        .. note::

            If you are initializing User Object using Account ID then the previous
            online id will be same as online id. This is just the limitation of API.

        :returns: onlineID
        :rtype: str

        .. code-block:: Python

            user_example = psnawp.user(online_id='VaultTec_Trading')
            print(user_example.prev_online_id)

        """
        profile = self._online_id_to_account_id(prev_online_id=self._prev_online_id)[
            "profile"
        ]
        prev_online_id: str = profile.get("onlineId")
        return prev_online_id

    def _online_id_to_account_id(
        self, prev_online_id: Optional[str] = None
    ) -> dict[str, Any]:
        """Converts user online ID and returns their account id. This is an internal function and not meant to be called directly.

        :returns: dict: PSN ID and Account ID of the user in search query
        :rtype: dict[str, Any]

        :raises: ``PSNAWPNotFound`` If the user is not valid/found.

        """

        online_id = self.online_id
        if prev_online_id is not None:
            online_id = prev_online_id

        try:
            query = {"fields": "accountId,onlineId,currentOnlineId"}
            response: dict[str, Any] = self._request_builder.get(
                url=f"{BASE_PATH['legacy_profile_uri']}{API_PATH['legacy_profile'].format(online_id=online_id)}",
                params=query,
            ).json()
            return response
        except PSNAWPNotFound as not_found:
            raise PSNAWPNotFound(
                f"Online ID {self.online_id} does not exist."
            ) from not_found

    def profile(self) -> dict[str, Any]:
        """Gets the profile of the user such as about me, avatars, languages etc...

        :returns: A dict containing info similar to what is shown below:
        :rtype: dict[str, Any]

            .. literalinclude:: examples/user/profile.json
                :language: json


        :raises: ``PSNAWPNotFound`` If the user is not valid/found.

        .. code-block:: Python

            user_example = psnawp.user(online_id='VaultTec_Trading')
            print(user_example.profile())

        """

        try:
            response: dict[str, Any] = self._request_builder.get(
                url=f"{BASE_PATH['profile_uri']}{API_PATH['profiles'].format(account_id=self.account_id)}"
            ).json()
            return response
        except PSNAWPBadRequest as bad_request:
            raise PSNAWPNotFound(
                f"Account ID {self.account_id} does not exist."
            ) from bad_request

    def get_presence(self) -> dict[str, Any]:
        """Gets the presences of a user. If the profile is private

        :returns: A dict containing info similar to what is shown below:
        :rtype: dict[str, Any]

            .. literalinclude:: examples/user/get_presence.json
                :language: json


        :raises: ``PSNAWPForbidden`` When the user's profile is private, and you don't
            have permission to view their online status.

        .. code-block:: Python

            user_example = psnawp.user(online_id='VaultTec_Trading')
            print(user_example.get_presence())

        """
        try:
            params = {"type": "primary"}
            response: dict[str, Any] = self._request_builder.get(
                url=f"{BASE_PATH['profile_uri']}/{self.account_id}{API_PATH['basic_presences']}",
                params=params,
            ).json()
            return response
        except PSNAWPForbidden as forbidden:
            raise PSNAWPForbidden(
                f"You are not allowed to check the presence of user {self.online_id}"
            ) from forbidden

    def friendship(self) -> dict[str, Any]:
        """Gets the friendship status and stats of the user

        :returns: A dict containing info similar to what is shown below
        :rtype: dict[str, Any]

            .. literalinclude:: examples/user/friendship.json
                :language: json


        .. code-block:: Python

            user_example = psnawp.user(online_id='VaultTec_Trading')
            print(user_example.friendship())

        """
        response: dict[Any, Any] = self._request_builder.get(
            url=f"{BASE_PATH['profile_uri']}{API_PATH['friends_summary'].format(account_id=self.account_id)}"
        ).json()
        return response

    def is_blocked(self) -> bool:
        """Checks if the user is blocked by you

        :returns: True if the user is blocked otherwise False
        :rtype: bool

        .. code-block:: Python

            user_example = psnawp.user(online_id='VaultTec_Trading')
            print(user_example.is_blocked())

        """
        response = self._request_builder.get(
            url=f"{BASE_PATH['profile_uri']}{API_PATH['blocked_users']}"
        ).json()
        return self.account_id in response["blockList"]

    def trophy_summary(self) -> TrophySummary:
        """Retrieve an overall summary of the number of trophies earned for a user broken down by

        - type
        - overall trophy level
        - progress towards the next level
        - current tier

        :returns: Trophy Summary Object containing all information
        :rtype: TrophySummary

        :raises: ``PSNAWPForbidden`` If the user's profile is private

        .. code-block:: Python

            user_example = psnawp.user(online_id="VaultTec_Trading")
            print(user_example.trophy_summary())

        """
        assert (
            self.account_id is not None
        )  # This is for mypy, self.account_id is always defined, but it cannot pick it up.
        return TrophySummary(self._request_builder, self.account_id)

    def trophy_titles(self, limit: Optional[int]) -> Iterator[TitleTrophySummary]:
        """Retrieve all game titles associated with an account, and a summary of trophies earned from them.

        :param limit: Limit of titles returned, None means to return all trophy titles.
        :type limit: Optional[int]

        :returns: Generator object with TitleTrophySummary objects
        :rtype: Iterator[TitleTrophySummary]

        :raises: ``PSNAWPForbidden`` If the user's profile is private

        .. code-block:: Python

            user_example = psnawp.user(online_id="VaultTec_Trading")
            for trophy_title in user_example.trophy_titles(limit=None):
                print(trophy_title)

        """
        assert (
            self.account_id is not None
        )  # This is for mypy, self.account_id is always defined, but it cannot pick it up.
        return TrophyTitles(self._request_builder, self.account_id).get_title_trophies(
            limit
        )

    def __repr__(self) -> str:
        return f"<User online_id:{self.online_id} account_id:{self.account_id}>"

    def __str__(self) -> str:
        return f"Online ID: {self.online_id} Account ID: {self.account_id}"
