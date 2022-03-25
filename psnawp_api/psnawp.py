from psnawp_api import authenticator, psnawp_exceptions
from psnawp_api import client
from psnawp_api import request_builder
from psnawp_api import search
from psnawp_api import user
from psnawp_api import group


# PlayStation Network API Wrapper Python (PSNAWP)
# Retrieve User Information, Trophies, Game and Store data from the PlayStation Network
# Author: isFakeAccount
class PSNAWP:
    def __init__(self, npsso):
        self.authenticator = authenticator.Authenticator(npsso_token=npsso)
        self.request_builder = request_builder.RequestBuilder(
            self.authenticator)
        self.client = client.Client(self.request_builder)

    def me(self):
        """
        Creates a new client object (your account)

        :returns: Client Object
        """
        return self.client

    def user(self, **kwargs):
        """
        Creates a new user object

        :param kwargs: online_id: PSN ID of the user or account_id: Account ID of the user
        :type kwargs: str
        :returns: User Object
        :raises requests.exception.HTTPError: If the user is not valid/found
        """
        online_id = None
        if 'online_id' in kwargs.keys():
            online_id = kwargs['online_id']

        account_id = None
        if 'account_id' in kwargs.keys():
            account_id = kwargs['account_id']

        if online_id is None and account_id is None:
            raise psnawp_exceptions.PSNAWPIllegalArgumentError(
                'You must provide either online ID or account ID')

        return user.User(self.request_builder, self.client, online_id, account_id)

    def group(self, **kwargs):
        """Creates a new group object using a groupId or a list of accountId

        kwargs:
            group_id (str): the groupId of a group usually retrieved with the get_groups() method

            account_ids (List[str]) a list of accountId of the members in the group
        Raises:
            psnawp_exceptions.PSNAWPIllegalArgumentError: If the group is not valid/found

        Returns:
            Group: the group object
        """
        group_id = None
        if 'group_id' in kwargs.keys():
            group_id = kwargs['group_id']

        account_ids = None
        if 'account_ids' in kwargs.keys():
            account_ids = kwargs['account_ids']

        if group_id:
            return group.Group(self.request_builder, self.client, group_id)

        elif account_ids:
            return group.Group(self.request_builder, self.client, account_ids=account_ids)

        else:
            raise psnawp_exceptions.PSNAWPIllegalArgumentError(
                'You must provide a group id or a list of user accountIds')

    def search(self):
        """
        Creates a new search object

        :returns: Search Object
        """
        return search.Search(self.request_builder)
