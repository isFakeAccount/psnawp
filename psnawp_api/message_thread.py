# Class MessageThread
# Responsible for managing messages groups and sending messages
# For internal use only do not call directly. See class Users
class MessageThread:
    base_uri = 'https://us-gmsg.np.community.playstation.net/groupMessaging/v1'

    def __init__(self, request_builder, client, online_ids):
        """
        Constructor of MessageThread. Responsible for managing messages groups and sending messages

        :param request_builder: Used to call http requests
        :param client: The user who is logged in. Used to create message threads
        :param online_ids: The user we want to chat with
        """
        self.request_builder = request_builder
        self.client = client
        self.online_ids = online_ids
        self.thread_id = self.threads_with_online_ids(self.online_ids)
        if self.thread_id is None:
            self.thread_id = self.create_new_thread()

    def create_new_thread(self):
        """
        Creates new thread if the thread does not exits. Note: This endpoint does not work I added in because
        sony might fix it in future

        :returns: thread id
        """
        thread_members = [{'onlineId': self.client.online_id}]
        online_ids_split = self.online_ids.split(',')
        for online_id in online_ids_split:
            thread_members.append({'onlineId': online_id})
        data = {'name': 'threadDetail',
                'contents': {'threadDetail': {'threadMembers': thread_members}}}
        response = self.request_builder.multipart_post(url='{}/threads'.format(MessageThread.base_uri),
                                                       name='threadDetail', data=data)
        return response['threadId']

    def threads_with_online_ids(self, online_ids):
        """
        Get thread with online ids as members

        :param online_ids: online ids of users, can input muliple csv values
        :returns: thread_id of the thread
        """
        response = self.request_builder.get(url='{}/users/me/threadIds'.format(MessageThread.base_uri),
                                            params={'withOnlineIds': online_ids})
        for thread_id in response['threadIds']:
            thread_info = self.get_thread_information(thread_id=thread_id['threadId'])
            if len(thread_info['threadMembers']) == 2:
                return thread_id['threadId']
        return None

    def get_thread_information(self, count=1, thread_id=None):
        """
        Gets the thread information

        :param thread_id: ID of thread
        :returns: Message thread info such as members, name, last activity etc...
        """
        if thread_id is None:
            thread_id = self.thread_id
        params = {'fields': 'threadMembers,threadNameDetail,threadThumbnailDetail,threadProperty,'
                            'latestTakedownEventDetail,newArrivalEventDetail,threadEvents', 'count': count}
        response = self.request_builder.get(url='{}/threads/{}'.format(MessageThread.base_uri, thread_id),
                                            params=params)
        return response

    def get_messages(self, message_count):
        """
        Gets all the messages in the message thread. Note: 200 is the max limit

        :returns: message events list containing all messages
        """
        return self.get_thread_information(count=message_count)['threadEvents']

    def leave_thread(self):
        """
        Leave the current message thread
        """
        self.request_builder.delete(url='{}/threads/{}/users/me'.format(MessageThread.base_uri, self.thread_id))

    def send_message(self, message):
        """
        Sends message to the thread id in the instance variable

        :param message: body of message
        :returns: thread information if message was successfully sent
        """
        data = {'messageEventDetail': {'eventCategoryCode': 1, 'messageDetail': {'body': message}}}
        self.request_builder.multipart_post(url='{}/threads/{}/messages'.format(MessageThread.base_uri, self.thread_id),
                                            name='messageEventDetail', data=data)
