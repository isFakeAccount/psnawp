import json

from psnawp_api.utils.endpoints import BASE_PATH, API_PATH
from psnawp_api.utils.request_builder import RequestBuilder


class Search:
    def __init__(self, request_builder: RequestBuilder):
        """The Search class provides the information and methods for searching resources on playstation network.

        .. note::

            This class is intended to be interfaced with through PSNAWP.

        :param request_builder: The instance of RequestBuilder. Used to make
            HTTPRequests.
        :type request_builder: RequestBuilder

        """
        self._request_builder = request_builder

    def universal_search(self, search_query: str, limit: int = 20):
        """Searches the Playstation Website. Note: It does not work as of now and the endpoints returns whole html page.

        .. note::

            Pagination not yet supported. The max number of results returned will be 20.

        :param search_query: search query
        :type search_query: str
        :param limit: Limit of number of results
        :type limit: int

        :returns: A dict containing info similar to what is shown below (Not all values
            are shown because of space limitations):
        :rtype: dict[str, Any]

            .. code-block:: json

                {
                    "prefix": "GTA",
                    "suggestions": [],
                    "domainResponses": [
                        {
                            "domain": "ConceptGameMobileApp",
                            "domainTitle": "Results for ConceptGameMobileApp with search term GTA",
                            "domainTitleMessageId": "msgid_null",
                            "domainTitleHighlight": [
                                "Results for ConceptGameMobileApp with search term GTA"
                            ],
                            "zeroState": false,
                            "univexId": "search.no_experiment.non.0.non_",
                            "facetOptions": [],
                            "next": "",
                            "totalResultCount": 33,
                            "results": [
                                {
                                    "id": "201930:UP1004-CUSA00419_00-GTAVDIGITALDOWNL",
                                    "type": "conceptProduct",
                                    "univexId": "search.no_experiment.non.0.non_",
                                    "score": 234.40508,
                                    "conceptProductMetadata": {}
                                }
                            ]
                        }
                    ],
                    "fallbackQueried": false
                }

        """

        data = {
            "searchTerm": search_query,
            "domainRequests": [
                {
                    "domain": "ConceptGameMobileApp",
                    "pagination": {"cursor": "", "pageSize": limit},
                    "featureFlags": {"isSpartacusEnabled": True},
                }
            ],
            "countryCode": "us",
            "languageCode": "en",
            "age": 99,
        }
        response = self._request_builder.post(
            url=f"{BASE_PATH['universal_search']}", data=json.dumps(data)
        ).json()
        return response

    def get_title_details(self, title_id: str):
        """get a title details using its code (eg. CUSA05486_00) as source.

        :param title_id: unique id of game.
        :type title_id: str

        :returns: A dict containing info similar to what is shown below (Not all values
            are shown because of space limitations):
        :rtype: dict[str, Any]

            .. code-block:: json

                [
                    {
                        "id": 201930,
                        "name": "Grand Theft Auto V (PlayStation®5)",
                        "nameEn": "Grand Theft Auto V (PlayStation®5)",
                        "publisherName": "Rockstar Games",
                        "media": {
                        },
                        "descriptions": [],
                        "categorizedProducts": [],
                        "titleIds": [],
                        "country": "US",
                        "language": "en",
                        "type": "GAME",
                        "localizedName": {},
                        "localizedDescriptions": {},
                        "localizedPublisherName": {},
                        "defaultProduct": {},
                        "genres": [],
                        "localizedGenres": [],
                        "subGenres": [],
                        "localizedSubGenres": [],
                        "minimumAge": 17,
                        "releaseDate": {},
                        "isRecommendableOnStore": true,
                        "isSearchableOnStore": true,
                        "storeFronts": [],
                        "supportedStoreFronts": [],
                        "marketingStories": [],
                        "compatibilityNotices": [],
                        "localizedMedia": {},
                        "revisionIds": {},
                        "contentRating": {}
                    }
                ]

        """

        param = {"age": 99, "country": "US", "language": "en-US"}

        response = self._request_builder.get(
            url=f"{BASE_PATH['game_titles']}{API_PATH['title_concept'].format(title_id=title_id)}",
            params=param,
        ).json()

        return response
