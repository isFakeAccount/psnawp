from typing import Optional, Any

from psnawp_api.core import psnawp_exceptions
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

        :param request_builder: Used to call http requests.
        :type request_builder: RequestBuilder
        :param online_id: Online ID (GamerTag) of the user.
        :type online_id: str
        :param account_id: Account ID of the user.
        :type account_id: str

        """
        self.request_builder = request_builder
        self._online_id = online_id
        self._account_id = account_id
        self._prev_online_id = online_id

    @property
    def online_id(self) -> str:
        """Gets the current online ID of the client logged in the api.

        Note: This might be different from the online id because playstation allows you
        to look up a user using old online id as long as it is not taken by another
        player.

        :returns: onlineID
        :rtype: str

        """
        current_online_id: str = self.profile()["currentOnlineId"]
        return current_online_id

    @property
    def account_id(self) -> str:
        """Gets the account ID of the client logged in the api.

        :returns: accountID
        :rtype: str

        """
        if self._account_id is not None:
            return self._account_id
        else:
            profile = self._online_id_to_account_id(self._online_id)["profile"]
            account_id: str = profile["accountId"]
            self._online_id = profile["currentOnlineId"]
            self._prev_online_id = profile["onlineId"]
            return account_id

    def _online_id_to_account_id(self, online_id):
        """Converts user online ID and returns their account id. This is an internal function and not meant to be called directly.

        :param online_id: online id of user you want to search
        :type online_id: str

        :returns: dict: PSN ID and Account ID of the user in search query

        :raises: If the search query is empty

        :raises: If the user is not valid/found

        """
        # If user tries to do empty search
        if len(online_id) <= 0:
            raise psnawp_exceptions.PSNAWPIllegalArgumentError(
                "online_id must contain a value."
            )
        base_uri = "https://us-prof.np.community.playstation.net/userProfile/v1/users"
        query = {"fields": "accountId,onlineId,currentOnlineId"}
        response = self.request_builder.get(
            url="{}/{}/profile2".format(base_uri, online_id), params=query
        )
        return response

    def profile(self):
        """Gets the profile of the user such as about me, avatars, languages etc...

        :returns: dict of user profile
        :rtype: dict

        :raises: If the user is not valid/found

        """
        query = {"fields": "accountId,onlineId,currentOnlineId"}
        response = self.request_builder.get(
            url=f"{BASE_PATH['profile_uri']}/{self.account_id}{API_PATH['profiles']}",
            param=query,
        )
        return response

    def get_presence(self) -> dict[Any, Any]:
        """Gets the presences of a user. If the profile is private

        :returns: Presence stats about the user, such as availability,
            lastAvailableDate, and primaryPlatformInfo
        :rtype: dict

        """
        params = {"type": "primary"}
        response = self.request_builder.get(
            url=f"{BASE_PATH['profile_uri']}/{self.account_id}{API_PATH['basic_presences']}",
            params=params,
        )
        presence: dict[Any, Any] = response.get("basicPresence", response)
        return presence

    def friendship(self) -> dict[Any, Any]:
        """Gets the friendship status and stats of the user

        :returns: Friendship stats in dictionary
        :rtype: dict

        """
        response = self.request_builder.get(
            url=f"{BASE_PATH['profile_uri']}{API_PATH['friends_summary'].replace('{account_id}', self.account_id)}"
        )
        friendship_stats: dict[Any, Any] = response
        return friendship_stats

    def is_blocked(self) -> bool:
        """Checks if the user is blocked by you

        :returns: True if the user is blocked otherwise False
        :rtype: bool

        """
        response = self.request_builder.get(
            url=f"{BASE_PATH['profile_uri']}{API_PATH['blocked_users']}"
        )
        return self.account_id in response["blockList"]

    def __repr__(self):
        return f"<User online_id:{self.online_id} account_id:{self.account_id}>"

    def __str__(self):
        return f"Online ID: {self.online_id} Account ID: {self.account_id}"
