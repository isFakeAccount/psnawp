from __future__ import annotations

from typing import Any, Iterable

from psnawp_api.models.group import Group
from psnawp_api.models.user import User
from psnawp_api.utils.endpoints import BASE_PATH, API_PATH
from psnawp_api.utils.request_builder import RequestBuilder


class Client:
    """The Client class provides the information and methods for the currently authenticated user."""

    def __init__(self, request_builder: RequestBuilder):
        """Initialize a Client instance.

        .. note::

            This class is intended to be interfaced with through PSNAWP.

        :param request_builder: The instance of RequestBuilder. Used to make
            HTTPRequests.
        :type request_builder: RequestBuilder

        """
        self._request_builder = request_builder

    @property
    def online_id(self) -> str:
        """Gets the online ID of the client logged in the api.

        :returns: onlineID
        :rtype: str

        .. code-block:: Python

            client = psnawp.me()
            print(client.online_id)

        """
        response = self._request_builder.get(
            url=f"{BASE_PATH['profile_uri']}{API_PATH['profiles'].format(account_id=self.account_id)}"
        ).json()
        online_id: str = response["onlineId"]
        return online_id

    @property
    def account_id(self) -> str:
        """Gets the account ID of the client logged in the api.

        :returns: accountID
        :rtype: str

        .. code-block:: Python

            client = psnawp.me()
            print(client.account_id)

        """
        response = self._request_builder.get(
            url=f"{BASE_PATH['account_uri']}{API_PATH['my_account']}"
        ).json()
        account_id: str = response["accountId"]
        return account_id

    def get_profile_legacy(self) -> dict[str, Any]:
        """Gets the profile info from legacy api endpoint. Useful for legacy console (PS3, PS4) presence.

        :returns: A dict containing info similar to what is shown below:
        :rtype: dict[str, Any]

            .. code-block:: json

                {
                    "profile": {
                        "onlineId": "VaultTec_Trading",
                        "accountId": "8520698476712646544",
                        "npId": "VmF1bHRUZWNfVHJhZGluZ0BiNi51cw==",
                        "avatarUrls": [
                            {
                                "size": "l",
                                "avatarUrl": "[Redacted]"
                            }
                        ],
                        "plus": 0,
                        "aboutMe": "r/Fallout76Marketplace Moderator",
                        "languagesUsed": [
                            "en"
                        ],
                        "trophySummary": {
                            "level": 1,
                            "progress": 0,
                            "earnedTrophies": {
                                "platinum": 0,
                                "gold": 0,
                                "silver": 0,
                                "bronze": 0
                            }
                        },
                        "isOfficiallyVerified": false,
                        "personalDetail": {
                            "firstName": "VaultTec",
                            "lastName": "TradingCo",
                            "profilePictureUrls": [
                                {
                                    "size": "xl",
                                    "profilePictureUrl": "[Redacted]"
                                }
                            ]
                        },
                        "personalDetailSharing": "no",
                        "personalDetailSharingRequestMessageFlag": false,
                        "primaryOnlineStatus": "offline",
                        "presences": [
                            {
                                "onlineStatus": "offline",
                                "hasBroadcastData": false,
                                "lastOnlineDate": "2021-02-05T20:14:45Z"
                            }
                        ],
                        "friendRelation": "no",
                        "requestMessageFlag": false,
                        "blocking": false,
                        "following": false,
                        "consoleAvailability": {
                            "availabilityStatus": "offline"
                        }
                    }
                }


        .. code-block:: Python

            client = psnawp.me()
            print(client.get_profile_legacy())

        """
        params = {
            "fields": "npId,onlineId,accountId,avatarUrls,plus,aboutMe,languagesUsed,trophySummary(@default,level,progress,earnedTrophies),"
            "isOfficiallyVerified,personalDetail(@default,profilePictureUrls),personalDetailSharing,personalDetailSharingRequestMessageFlag,"
            "primaryOnlineStatus,presences(@default,@titleInfo,platform,lastOnlineDate,hasBroadcastData),requestMessageFlag,blocking,friendRelation,"
            "following,consoleAvailability"
        }

        response: dict[str, Any] = self._request_builder.get(
            url=f"{BASE_PATH['legacy_profile_uri']}{API_PATH['legacy_profile'].format(online_id=self.online_id)}",
            params=params,
        ).json()

        return response

    def get_account_devices(self) -> list[dict[str, Any]]:
        """Gets the list of devices the client is logged into.

        :returns: A dict containing info similar to what is shown below:
        :rtype: list[dict[str, Any]]

            .. code-block:: json

                [
                    {
                        "deviceId": "[Redacted]",
                        "deviceType": "PS4",
                        "activationType": "PSN_GAME_V3",
                        "activationDate": "2021-02-05T20:11:27.815Z",
                        "accountDeviceVector": "[Redacted]"
                    }
                ]


        .. code-block:: Python

            client = psnawp.me()
            print(client.get_account_devices())

        """
        params = {
            "includeFields": "device,systemData",
            "platform": "PS5,PS4,PS3,PSVita",
        }
        response = self._request_builder.get(
            url=f"{BASE_PATH['account_uri']}{API_PATH['my_account']}", params=params
        ).json()

        # Just so mypy doesn't complain
        account_devices: list[dict[str, Any]] = response.get("accountDevices", [])
        return account_devices

    def friends_list(self, limit: int = 1000) -> Iterable[User]:
        """Gets the friends list and return their account ids.

        :param limit: The number of items from input max is 1000.
        :type limit: int

        :returns: All friends in your friends list.
        :rtype: Iterable[User]

        .. code-block:: Python

            client = psnawp.me()
            friends_list = client.friends_list()

            for friend in friends_list:
                ...

        """
        limit = min(1000, limit)

        params = {"limit": limit}
        response = self._request_builder.get(
            url=f"{BASE_PATH['profile_uri']}{API_PATH['friends_list']}", params=params
        ).json()
        return (
            User(
                request_builder=self._request_builder,
                account_id=account_id,
                online_id=None,
            )
            for account_id in response["friends"]
        )

    def available_to_play(self) -> Iterable[User]:
        """Gets the list of users on your "Notify when available" subscription list.

        :returns: Iterable of user objects.
        :rtype: Iterable[User]

        .. code-block:: Python

            client = psnawp.me()
            available_to_play = client.available_to_play()

            for user in available_to_play:
                ...

        """
        response = self._request_builder.get(
            url=f"{BASE_PATH['profile_uri']}{API_PATH['available_to_play']}"
        ).json()
        return (
            User(
                request_builder=self._request_builder,
                account_id=account_id_dict["accountId"],
                online_id=None,
            )
            for account_id_dict in response["settings"]
        )

    def blocked_list(self) -> Iterable[User]:
        """Gets the blocked list and return their account ids.

        :returns: Al blocked users on your block list.
        :rtype: Iterable[User]

        .. code-block:: Python

            client = psnawp.me()
            blocked_list = client.blocked_list()

            for blocked_users in blocked_list:
                ...

        """
        response = self._request_builder.get(
            url=f"{BASE_PATH['profile_uri']}{API_PATH['blocked_users']}"
        ).json()
        return (
            User(
                request_builder=self._request_builder,
                account_id=account_id,
                online_id=None,
            )
            for account_id in response["blockList"]
        )

    def get_groups(self, limit: int = 200, offset: int = 0) -> Iterable[Group]:
        """Gets all the groups you have participated in.

        :param limit: The number of groups to receive.
        :type limit: int
        :param offset: Lets you exclude first N items groups. Offset = 10 lets you skip
            the first 10 groups.
        :type offset: int

        :returns: Iterable of Group Objects.
        :rtype: Iterable[Group]

        """
        param = {"includeFields": "members", "limit": limit, "offset": offset}

        response = self._request_builder.get(
            url=f"{BASE_PATH['gaming_lounge']}{API_PATH['my_groups']}", params=param
        ).json()

        return (
            Group(
                request_builder=self._request_builder,
                group_id=group_info["groupId"],
                users=None,
            )
            for group_info in response["groups"]
        )

    def __repr__(self):
        return f"<User online_id:{self.online_id} account_id:{self.account_id}>"

    def __str__(self):
        return f"Online ID: {self.online_id} Account ID: {self.account_id}"
