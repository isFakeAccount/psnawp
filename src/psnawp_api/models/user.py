from typing import Optional

from psnawp_api.core import psnawp_exceptions


# Class User
# This class will contain the information about the PSN ID you passed in when creating object
class User:
    base_uri = "https://m.np.playstation.net/api/userProfile/v1/internal/users"

    def __init__(
        self, request_builder, online_id: Optional[str], account_id: Optional[str]
    ):
        """Constructor of Class User. Creates user object using online id or account id.

        :param request_builder: Used to call http requests.
        :param online_id: Online ID (GamerTag) of the user.
        :param account_id: Account ID of the user.

        """
        self.request_builder = request_builder
        self.online_id = online_id
        self.account_id = account_id
        self.prev_online_id = None

        # If online ID is given search by online ID otherwise by account ID
        if self.online_id is not None:
            profile = self.online_id_to_account_id(online_id)["profile"]
            if profile["currentOnlineId"] == profile["accountId"]:
                self.account_id = profile["accountId"]
                self.prev_online_id = profile["onlineId"]
            else:
                self.account_id = profile["accountId"]
                self.online_id = profile["currentOnlineId"]
                self.prev_online_id = profile["onlineId"]
        elif self.account_id is not None:
            profile = self.profile()
            self.online_id = profile["onlineId"]

    def online_id_to_account_id(self, online_id):
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
        """Gets the profile of the user

        :returns: Information about profile such as about me, avatars, languages etc...

        :raises: If the user is not valid/found

        """
        query = {"fields": "accountId,onlineId,currentOnlineId"}
        response = self.request_builder.get(
            url="{}/{}/profiles".format(User.base_uri, self.account_id), param=query
        )
        return response

    def get_presence(self):
        """Gets the presences of a user. If the profile is private

        :returns: dict availability, lastAvailableDate, and primaryPlatformInfo

        """
        params = {"type": "primary"}
        response = self.request_builder.get(
            url="{}/{}/basicPresences".format(User.base_uri, self.account_id),
            params=params,
        )
        if "basicPresence" in response.keys():
            return response["basicPresence"]
        else:
            return response

    def friendship(self):
        """Gets the friendship status and stats of the user

        :returns: dict: friendship stats

        """
        response = self.request_builder.get(
            url="{}/me/friends/{}/summary".format(User.base_uri, self.account_id)
        )
        return response

    def is_available_to_play(self):
        """TODO I am not sure what this endpoint returns I'll update the documentation later :returns:"""
        response = self.request_builder.get(
            url="{}/me/friends/subscribing/availableToPlay".format(User.base_uri)
        )
        return response

    def is_blocked(self):
        """Checks if the user is blocked by you

        :returns: boolean: True if the user is blocked otherwise False

        """
        response = self.request_builder.get(url="{}/me/blocks".format(User.base_uri))
        if self.account_id in response["blockList"]:
            return True
        else:
            return False

    def __repr__(self):
        return "<User online_id:{} account_id:{}>".format(
            self.online_id, self.account_id
        )

    def __str__(self):
        return "Online ID: {} Account ID: {}".format(self.online_id, self.account_id)
