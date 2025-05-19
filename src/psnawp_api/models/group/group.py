"""Provides Group class for creating message groups and interacting with message groups."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from typing_extensions import Self

from psnawp_api.core import (
    PSNAWPBadRequestError,
    PSNAWPForbiddenError,
    PSNAWPNotFoundError,
)
from psnawp_api.utils import API_PATH, BASE_PATH

if TYPE_CHECKING:
    from collections.abc import Iterable

    from psnawp_api.core import Authenticator
    from psnawp_api.models.group.group_datatypes import GroupDetails, MessageResponse
    from psnawp_api.models.user import User


class Group:
    """The Group class manages PSN group endpoints related to messages (Group and Direct Messages).

    :var Authenticator authenticator: An instance of :py:class:`~psnawp_api.core.authenticator.Authenticator` used to
        authenticate and make HTTPS requests.
    :var str group_id: Unique ID representing a specific PSN group or direct message thread.

    .. note::

        This class is intended to be used via PSNAWP. See :py:meth:`psnawp_api.psnawp.PSNAWP.group` or
        :py:meth:`psnawp_api.client.Client.get_groups`

    """

    def __init__(
        self,
        authenticator: Authenticator,
        group_id: str,
    ) -> None:
        """Constructor of Group.

        :param authenticator: The Authenticator instance used for making authenticated requests to the API.
        :param group_id: The Group ID of a group.

        :raises PSNAWPNotFoundError: If group id does not exist or is invalid.
        :raises PSNAWPForbiddenError: If you are sending message a user who has blocked you.

        The canonical way to create instance of this class is to the class method :py:meth:`Group.create_from_group_id`
        and :py:meth:`Group.create_from_users`.

        """
        self.authenticator = authenticator
        self.group_id = group_id

    @classmethod
    def create_from_group_id(cls, authenticator: Authenticator, group_id: str) -> Self:
        """Create :py:class:`Group` instance with group id.

        :param authenticator: The Authenticator instance used for making authenticated requests to the API.
        :param group_id: The Group ID of a group.

        :returns: Instance of :py:class:`Group`

        """
        return cls(authenticator, group_id)

    @classmethod
    def create_from_users(
        cls,
        authenticator: Authenticator,
        users: Iterable[User],
    ) -> Self:
        """Creates a new message :py:class:`Group` from the provide list of Users.

        :raises PSNAWPForbiddenError: If you are sending message a user who has blocked you.

        """
        account_ids = [{"accountId": user.account_id} for user in users]
        invitees = {"invitees": account_ids}

        try:
            response = authenticator.post(
                url=f"{BASE_PATH['gaming_lounge']}{API_PATH['create_group']}",
                json=invitees,
            ).json()
            return cls(authenticator, response["groupId"])
        except PSNAWPForbiddenError as forbidden:
            raise PSNAWPForbiddenError(
                "Can't create group because of the users' privacy settings.",
            ) from forbidden

    def change_name(self, group_name: str) -> None:
        """Changes the group name to one specified in arguments.

        :param group_name: The name of the group that will be set.

        :returns: None

        :raises PSNAWPBadRequestError: If you are not part of group or the group is a DM.

        .. note::

            You cannot change the name of DM groups. i.e. Groups with only two people (including you).

        """
        data = {"groupName": {"value": group_name}}
        try:
            self.authenticator.patch(
                url=f"{BASE_PATH['gaming_lounge']}{API_PATH['group_settings'].format(group_id=self.group_id)}",
                json=data,
            )
        except PSNAWPBadRequestError as bad_req:
            raise PSNAWPBadRequestError(
                f"The group name of Group ID {self.group_id} does cannot be changed. Group is either a dm or does not exist.",
            ) from bad_req

    def get_group_information(self) -> GroupDetails:
        """Gets the group chat information such as about me, avatars, languages etc...

        :returns: A dict containing info similar to what is shown below:

        :raises PSNAWPNotFoundError: If group id does not exist or is invalid.

        .. literalinclude:: ../examples/group/group_information.json
            :language: json

        """
        param = {
            "includeFields": "groupName,groupIcon,members,mainThread,joinedTimestamp,modifiedTimestamp,isFavorite,existsNewArrival,notificationSetting",
        }

        try:
            response: GroupDetails = self.authenticator.get(
                url=f"{BASE_PATH['gaming_lounge']}{API_PATH['group_members'].format(group_id=self.group_id)}",
                params=param,
            ).json()
        except PSNAWPNotFoundError as not_found:
            raise PSNAWPNotFoundError(
                f"Group ID {self.group_id} does not exist.",
            ) from not_found
        else:
            return response

    def send_message(self, message: str) -> MessageResponse:
        """Sends a message in the group.

        .. note::

            For now only text based messaging is supported.

        :param message: Message Body

        :returns: A dict containing info similar to what is shown below:

        .. code-block:: json

            {
                "messageUid": "1#425961448584099",
                "createdTimestamp": "1663911908531"
            }

        """
        data = {"messageType": 1, "body": message}

        response: MessageResponse = self.authenticator.post(
            url=f"{BASE_PATH['gaming_lounge']}{API_PATH['send_group_message'].format(group_id=self.group_id)}",
            json=data,
        ).json()

        return response

    def get_conversation(self, limit: int = 20) -> dict[str, Any]:
        """Gets the conversations in a group.

        :param limit: The number of conversations to receive.

        :returns: A dict containing info similar to what is shown below:

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

        response: dict[str, Any] = self.authenticator.get(
            url=f"{BASE_PATH['gaming_lounge']}{API_PATH['conversation'].format(group_id=self.group_id)}",
            params=param,
        ).json()

        return response

    def leave_group(self) -> None:
        """Leave the current group.

        :raises PSNAWPNotFoundError: If you are not part of the group.

        """
        self.authenticator.delete(
            url=f"{BASE_PATH['gaming_lounge']}{API_PATH['leave_group'].format(group_id=self.group_id)}",
        )

    def invite_members(self, users: Iterable[User]) -> None:
        """Invite users to join the group.

        If all users in the invite list have blocked you, a PSNAWPForbidden exception is raised. Users who have blocked
        you are skipped, and the remaining users are invited.

        :param Iterable[User] users: An iterable of User objects to be invited.

        :raises PSNAWPForbiddenError: If all users in the invite list have blocked you.

        """
        account_ids = [{"accountId": user.account_id} for user in users]
        invitees = {"invitees": account_ids}

        try:
            self.authenticator.post(
                url=f"{BASE_PATH['gaming_lounge']}{API_PATH['create_group']}",
                json=invitees,
            ).json()
        except PSNAWPForbiddenError as forbidden:
            raise PSNAWPForbiddenError(
                "Can't add users to group because of the users' privacy settings.",
            ) from forbidden

    def kick_member(self, user: User) -> None:
        """Remove a user from the group.

        :param user: The User object representing the member to be removed.

        :raises PSNAWPNotFoundError: If the user is not in the group.

        """
        try:
            self.authenticator.delete(
                url=f"{BASE_PATH['gaming_lounge']}{API_PATH['kick_member'].format(group_id=self.group_id, account_id=user.account_id)}",
            )
        except PSNAWPNotFoundError as not_found:
            raise PSNAWPNotFoundError(
                f'User "{user.online_id}" is not a member of the group.',
            ) from not_found

    def __repr__(self) -> str:
        """Returns a detailed string representation of the object for debugging."""
        return f"<Group group_id:{self.group_id}>"

    def __str__(self) -> str:
        """Returns Group ID."""
        return f"Group ID: {self.group_id}"
