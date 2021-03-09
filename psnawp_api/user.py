from psnawp_api import message_thread
from psnawp_api import psnawp_exceptions


# Class User
# This class will contain the information about the PSN ID you passed in when creating object
class User:
    base_uri = 'https://m.np.playstation.net/api/userProfile/v1/internal/users'

    def __init__(self, request_builder, client, online_id, account_id):
        """
        Constructor of Class User. Creates user object using online id or account id
        :param request_builder: Used to call http requests
        :param client: The user who is logged in. Used to create message threads
        :param online_id:
        :param account_id:
        """
        self.request_builder = request_builder
        self.client = client
        self.online_id = online_id
        self.account_id = account_id
        # If online ID is given search by online ID otherwise by account ID
        if self.online_id is not None:
            profile = self.online_id_to_account_id(online_id)
            self.account_id = profile['profile']['accountId']
        elif self.account_id is not None:
            profile = self.profile()
            self.online_id = profile['onlineId']
        self.msg_thread = None

    def online_id_to_account_id(self, online_id):
        """
        Converts user online ID and returns their account id. This is an internal function and not meant to be called
        directly.

        :param online_id: online id of user you want to search
        :type online_id: str
        :returns: dict: PSN ID and Account ID of the user in search query
        :raises PSNAWPIllegalArgumentError: If the search query is empty
        :raises requests.exception.HTTPError: If the user is not valid/found
        """
        # If user tries to do empty search
        if len(online_id) <= 0:
            raise psnawp_exceptions.PSNAWPIllegalArgumentError('online_id must contain a value.')
        base_uri = "https://us-prof.np.community.playstation.net/userProfile/v1/users"
        param = {'fields': 'accountId,onlineId,currentOnlineId'}
        response = self.request_builder.get(url="{}/{}/profile2".format(base_uri, online_id), params=param)
        return response

    def profile(self):
        """
        Gets the profile of the user

        :returns: Information about profile such as about me, avatars, languages etc...
        :raises requests.exception.HTTPError: If the user is not valid/found
        """
        response = self.request_builder.get(url='{}/{}/profiles'.format(User.base_uri, self.account_id))
        return response

    def get_presence(self):
        """
        Gets the presences of a user. If the profile is private

        :returns: dict availability, lastAvailableDate, and primaryPlatformInfo
        """
        params = {'type': 'primary'}
        response = self.request_builder.get(url='{}/{}/basicPresences'.format(User.base_uri, self.account_id),
                                            params=params)
        if 'basicPresence' in response.keys():
            return response['basicPresence']
        else:
            return response

    def friendship(self):
        """
        Gets the friendship status and stats of the user

        :returns: dict: friendship stats
        """
        response = self.request_builder.get(url='{}/me/friends/{}/summary'.format(User.base_uri, self.account_id))
        return response

    def is_available_to_play(self):
        """
        TODO I am not sure what this endpoint returns I'll update the documentation later
        :returns:
        """
        response = self.request_builder.get(url='{}/me/friends/subscribing/availableToPlay'.format(User.base_uri))
        return response

    def is_blocked(self):
        """
        Checks if the user is blocked by you

        :returns: boolean: True if the user is blocked otherwise False
        """
        response = self.request_builder.get(url='{}/me/blocks'.format(User.base_uri))
        if self.account_id in response['blockList']:
            return True
        else:
            return False

    def send_private_message(self, message):
        """
        Send a private message to the user. Due to endpoint limitation. This will only work if the message group
        already exists.

        :param message: body of message
        :type message: str
        """
        if self.msg_thread is None:
            self.msg_thread = message_thread.MessageThread(self.request_builder, self.client, self.online_id)
        self.msg_thread.send_message(message)

    def get_messages_in_conversation(self, message_count=1):
        """
        Gets all the messages in send and received in the message group (Max limit is 200)
        The most recent message will be and the start of list


        :param message_count: The number of messages you want to get
        :type message_count: int
        :returns: message events list containing all messages
        """
        if self.msg_thread is None:
            self.msg_thread = message_thread.MessageThread(self.request_builder, self.client, self.online_id)

        msg_history = self.msg_thread.get_messages(min(message_count, 200))
        return msg_history

    def leave_private_message_group(self):
        """
        If you want to leave the message group
        """
        if self.msg_thread is not None:
            self.msg_thread.leave()

    def __repr__(self):
        return "<User online_id:{} account_id:{}>".format(self.online_id, self.account_id)

    def __str__(self):
        return "Online ID: {} Account ID: {}".format(self.online_id, self.account_id)
