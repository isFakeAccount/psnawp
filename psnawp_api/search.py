# Class Search
# Used to search for users from their PSN ID and get their Online ID
class Search:
    base_uri = 'https://www.playstation.com'

    def __init__(self, request_builder):
        self.request_builder = request_builder

    def universal_search(self, search_query):
        """
        Searches the Playstation Website. Note: It does not work as of now and the endpoints returns whole html page

        :param search_query: search query
        :return: search result
        """
        params = {'q': search_query, 'smcid': 'web:psn:primary nav:search:{}'.format(search_query)}
        response = self.request_builder.get(url='{}/en-us/search'.format(Search.base_uri), params=params)
        print(response)
