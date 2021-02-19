import platform

import requests


class Search:
    def __init__(self, authenticator):
        self.authenticator = authenticator
        self.default_headers = {'Accept-Language': 'en-US',
                                'User-Agent': platform.platform()}

    def search_user(self, search_query):
        # TODO: Figure out the endpoints of search
        pass
