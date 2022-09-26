import json
from typing import Optional, Iterable

from psnawp_api.core.psnawp_exceptions import (
    PSNAWPIllegalArgumentError,
    PSNAWPNotFound,
    PSNAWPNotAllowed,
    PSNAWPBadRequest,
)
from psnawp_api.models.user import User
from psnawp_api.utils.endpoints import BASE_PATH, API_PATH
from psnawp_api.utils.request_builder import RequestBuilder


class Group:
    def __init__(
        self,
        request_builder: RequestBuilder,
        group_id: Optional[str],
        users: Optional[Iterable[User]],
    ):
        """Constructor of Group. Responsible for managing messages groups and sending messages.

        .. note::

            This class is intended to be interfaced with through PSNAWP.

        :param request_builder: The instance of RequestBuilder. Used to make
            HTTPRequests.
        :type request_builder: RequestBuilder
        :param group_id: The Group ID of a group.
        :type group_id: Optional[str]
        :param users: A list of users of the members in the group.
        :type users: Optional[Iterable[User]]

        """

        self._request_builder = request_builder
        self.group_id = group_id
        self.users = users

        if self.group_id is not None:
            self.get_group_information()
        elif self.users is not None:
            self._create_group()

    def _create_group(self):
        """Creates a new group if it doesn't exist. Doesn't work if user's privacy settings block invites."""
        if self.users is None:
            # mypy complains if this check is not there.
            raise PSNAWPIllegalArgumentError("Can't create users from empty user list.")

        invitees = [{"accountId": user.account_id} for user in self.users]
        data = {"invitees": invitees}

        response = self._request_builder.post(
            url=f"{BASE_PATH['gaming_lounge']}{API_PATH['create_group']}",
            data=json.dumps(data),
        ).json()

        self.group_id = response["groupId"]

    def change_name(self, group_name: str) -> None:
        """Changes the group name to one specified in arguments.

        .. note::

            You cannot change the name of DM groups. i.e. Groups with only two people
            (including you).

        :param group_name: The name of the group that will be set.
        :type group_name: str

        :returns: None

        """

        data = {"groupName": {"value": group_name}}
        try:
            self._request_builder.patch(
                url=f"{BASE_PATH['gaming_lounge']}{API_PATH['group_settings'].format(group_id=self.group_id)}",
                data=json.dumps(data),
            )
        except PSNAWPBadRequest as bad_req:
            raise PSNAWPNotAllowed(
                f"The group name of Group ID {self.group_id} does cannot be changed. Most likely it is a DM and their names can't be changed."
            ) from bad_req

    def get_group_information(self):
        """Gets the group chat information such as about me, avatars, languages etc...

        :returns: A dict containing info similar to what is shown below:
        :rtype: dict[str, Any]

        :raises: ``PSNAWPNotFound`` If group id does not exist or is invalid.

        .. code-block:: json

            {
                "groupId": "~25C4C5406FD6D50E.763F9A1EB6AB5790",
                "groupType": 0,
                "modifiedTimestamp": "1663911908531",
                "groupName": {
                    "value": "",
                    "status": 0
                },
                "groupIcon": {
                    "status": 0
                },
                "joinedTimestamp": "1616356026000",
                "isFavorite": false,
                "existsNewArrival": false,
                "mainThread": {
                    "threadId": "~25C4C5406FD6D50E.763F9A1EB6AB5790",
                    "modifiedTimestamp": "1663911908531",
                    "latestMessage": {
                        "messageUid": "1#425961448584099",
                        "messageType": 1,
                        "alternativeMessageType": 1,
                        "body": "Hello World",
                        "createdTimestamp": "1663911908531",
                        "sender": {
                            "accountId": "8520698476712646544",
                            "onlineId": "VaultTec_Trading"
                        }
                    },
                    "readMessageUid": "1#425961448584099"
                },
                "members": [
                    {
                        "accountId": "2721516955383551246",
                        "onlineId": "VaultTec-Co"
                    },
                    {
                        "accountId": "8520698476712646544",
                        "onlineId": "VaultTec_Trading"
                    }
                ],
                "partySessions": [],
                "notificationSetting": {
                    "isMute": false
                }
            }

        """

        param = {
            "includeFields": "groupName,groupIcon,members,mainThread,joinedTimestamp,modifiedTimestamp,isFavorite,existsNewArrival,partySessions,"
            "notificationSetting"
        }

        try:
            response = self._request_builder.get(
                url=f"{BASE_PATH['gaming_lounge']}{API_PATH['group_members'].format(group_id=self.group_id)}",
                params=param,
            ).json()

            return response
        except PSNAWPNotFound as not_found:
            raise PSNAWPNotFound(
                f"Group ID {self.group_id} does not exist."
            ) from not_found

    def send_message(self, message: str) -> dict[str, str]:
        """Sends a message in the group.

        .. note::

            For now only text based messaging is supported.

        :param message: Message Body

        :returns: A dict containing info similar to what is shown below:
        :rtype: dict[str, str]

        .. code-block:: json

            {
                "messageUid": "1#425961448584099",
                "createdTimestamp": "1663911908531"
            }

        """

        data = {"messageType": 1, "body": message}

        response: dict[str, str] = self._request_builder.post(
            url=f"{BASE_PATH['gaming_lounge']}{API_PATH['send_group_message'].format(group_id=self.group_id)}",
            data=json.dumps(data),
        ).json()

        return response

    def get_conversation(self, limit: int = 20):
        """Gets the conversations in a group.

        :param limit: The number of conversations to receive.
        :type limit: int

        :returns: A dict containing info similar to what is shown below:
        :rtype: dict[str, Any]

            .. code-block::

                {
                    "messages": [
                        {
                            "messageUid": "1#425961448584099",
                            "messageType": 1,
                            "alternativeMessageType": 1,
                            "body": "Hello World",
                            "createdTimestamp": "1663911908531",
                            "sender": {
                                "accountId": "8520698476712646544",
                                "onlineId": "VaultTec_Trading"
                            }
                        }
                    ],
                    "previous": "1#425961448584099",
                    "next": "1#425961448584099",
                    "reachedEndOfPage": false,
                    "messageCount": 1
                }

        """

        param = {"limit": limit}

        response = self._request_builder.get(
            url=f"{BASE_PATH['gaming_lounge']}{API_PATH['conversation'].format(group_id=self.group_id)}",
            params=param,
        ).json()

        return response

    def leave_group(self) -> None:
        """Leave the current group

        :raises: ``PSNAWPNotFound`` If you are not part of the group.

        """

        self._request_builder.delete(
            url=f"{BASE_PATH['gaming_lounge']}{API_PATH['leave_group'].format(group_id=self.group_id)}"
        )
