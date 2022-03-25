import json
from typing import List


# Class Group
# This class will contain the information about the groups instantiated and
# is responsible for managing messages groups and sending messages.
class Group:
    base_uri = "https://m.np.playstation.com/api/gamingLoungeGroups/v1"

    def __init__(self, request_builder, client, group_id=None, account_ids: List[str] = None):
        """Constructor, used to get/retrieve already created groups.
            Or create a new one when called from a user object.

        Args:
            request_builder (RequestBuilder): Used to call http requests
            client (Client): The user who is logged in. Used to create message threads
            group_id (str, optional): groupId of the group to instantiate. Defaults to None.
            account_ids (List[str], optional): account_ids of the users to create a group with. Defaults to None.
        """

        self.request_builder = request_builder
        self.client = client

        # if groupId is passed retrieve a group using it
        if group_id:
            self.group_id = group_id
            info = self.get_by_group_id()
            self.members = info["members"]

        # if account_ids of the members is passed retrieve a group using it
        if account_ids:

            if self.client.account_id not in account_ids:
                account_ids.append(self.client.account_id)

            info = self.get_by_account_ids(account_ids)

            if info:
                self.group_id = info["groupId"]
                self.members = info["members"]

            # if no group with that user exists create it using account_ids of users to invite in
            else:
                newGroup = Group.group_by_account_ids(
                    self.request_builder, self.client, account_ids=account_ids)
                self.group_id = newGroup.group_id
                self.members = newGroup.members

    def get_by_group_id(self):
        """
        Gets the get_specifics of the group

        :returns: Information about profile such as about me, avatars, languages etc...
        :raises requests.exception.HTTPError: If the group is not valid/found
        """

        param = {
            "includeFields": "groupName,groupIcon,members,mainThread,joinedTimestamp,modifiedTimestamp,isFavorite,existsNewArrival,partySessions,notificationSetting"}

        response = self.request_builder.get(
            url=f"{Group.base_uri}/members/me/groups/{self.group_id}", params=param)

        return response

    def get_by_account_ids(self, account_ids):
        """
        Get group with account ids as members. This method will only be used for sending a message to a specific user like:
        user.send_message()

        Args:
            account_ids (list): list of users' account ids

        Returns: 
            str: thread_id of the thread
        """

        print(account_ids)
        param = {"includeFields": "members,mainThread"}
        response = self.request_builder.get(
            url=f'{Group.base_uri}/members/me/groups', params=param)

        for group in response["groups"]:
            group_members = group["members"]

            # what this do is checking if ALL of the account_ids are presents in the group_members list
            # and if they are the same number
            if all(account_id in account_ids for account_id in [member["accountId"] for member in group_members]):
                self.group_id = group["groupId"]
                return self.get_by_group_id()

        return None

    def send_message(self, message: str):

        data = {
            "messageType": 1,
            "body": message
        }

        response = self.request_builder.post(
            url=f"{Group.base_uri}/groups/{self.group_id}/threads/{self.group_id}/messages", data=json.dumps(data),
                headers={"Content-Type": "application/json"})

        return response

    def get_conversation(self, limit=20):

        param = {"limit": limit}

        response = self.request_builder.get(
            url=f"{Group.base_uri}/members/me/groups/{self.group_id}/threads/{self.group_id}/messages", params=param)

        return response

    def get_group_information(self):
        """get the group information

        Returns:
            dict: Group info such as members, name, last activity etc...
        """
        if self.group_id is None:
            return

        params = {'includeFields': 'groupName,groupIcon,members,mainThread,joinedTimestamp,modifiedTimestamp,'
                  'isFavorite,existsNewArrival,partySessions,notificationSetting'}

        response = self.request_builder.get(url=f'{Group.base_uri}/members/me/groups/{self.group_id}',
                                            params=params)

        return response

    def leave_group(self):
        """
        Leave the current group
        """

        print(self.group_id)
        self.request_builder.delete(
            url=f'{Group.base_uri}/groups/{self.group_id}/members/me')

    @classmethod
    def group_by_account_ids(cls, request_builder, client, account_ids: List):
        """create a new group if it doesn't exist. Doesn't work if user's privacy settings block invites.

        Args:
            account_ids (List[str]): list with onlineId of the users to invite in the group.
            Can be only 1 to invite a single user or many to create a party.
            You do not need to invite the client, so the method automatically removes it from the list

        Returns:
            Group: the newly created group
        """
        invitees = []

        for account_id in account_ids:
            if account_id != client.account_id:
                invitees.append({"accountId": account_id})

        data = {
            "invitees": invitees
        }

        print(data)

        response = request_builder.post(
            url=f"{Group.base_uri}/groups", data=json.dumps(data), headers={"Content-Type": "Application/json"})

        return cls(request_builder, client, group_id=response["groupId"])
