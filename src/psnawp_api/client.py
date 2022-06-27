from psnawp_api.base import PSNAWPBase
from psnawp_api.endpoints import BASE_PATH, API_PATH
from typing import Any


class Client(PSNAWPBase):
    """The Client class provides the information and methods for the currently authenticated user."""

    def __init__(self, psnawp):
        """Initialize a Client instance. This class is intended to be interfaced with through PSNAWP.

        :param psnawp: The instance of caller. Used to make HTTPRequests.

        """
        super().__init__(psnawp)

    def get_online_id(self) -> str:
        """Gets the online ID of the client logged in the api.

        :returns: onlineID

        """
        response = self._psnawp.request_builder.get(
            url=f"{BASE_PATH['profile_uri']}/{self.get_account_id()}/profiles"
        )
        online_id: str = response["onlineId"]
        return online_id

    def get_account_id(self) -> str:
        """Gets the account ID of the client logged in the api.

        :returns: accountID

        """
        response = self._psnawp.request_builder.get(
            url=f"{BASE_PATH['account_uri']}/v1/devices/accounts/me"
        )
        account_id: str = response["accountId"]
        return account_id

    def get_account_devices(self) -> list[dict[str, Any]]:
        """Gets the list of devices the client is logged into.

        :returns: accountDevices: List of devices the user is logged in and their
            information.

        """
        response = self._psnawp.request_builder.get(
            url=f"{BASE_PATH['account_uri']}/v1/devices/accounts/me"
        )
        devices: list[dict[str, Any]] = response["accountDevices"]
        return devices

    def friends_list(self, limit: int = 1000) -> list[str]:
        """Gets the friends list and return their account ids.

        :param limit: The number of items from input max is 1000.

        :returns: Account ID of all friends in your friends list.

        """
        limit = min(1000, limit)

        params = {"limit": limit}
        response = self._psnawp.request_builder.get(
            url=f"{BASE_PATH['profile_uri']}{API_PATH['friends_list']}", params=params
        )
        friends_list: list[str] = response["friends"]
        return friends_list

    def blocked_list(self) -> list[str]:
        """Gets the blocked list and return their account ids.

        :returns: Account ID of all blocked users on your block list.

        """
        response = self._psnawp.request_builder.get(
            url=f"{BASE_PATH['profile_uri']}{API_PATH['blocked_users']}"
        )
        blocked_list: list[str] = response["blockList"]
        return blocked_list

    def __repr__(self):
        return "<User online_id:{} account_id:{}>".format("me", self.get_account_id())

    def __str__(self):
        return "Online ID: {} Account ID: {}".format("me", self.get_account_id())
