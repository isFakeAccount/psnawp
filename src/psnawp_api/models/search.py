from __future__ import annotations

import json
from typing import Any

from psnawp_api.core.psnawp_exceptions import PSNAWPNotFound
from psnawp_api.utils.endpoints import BASE_PATH
from psnawp_api.utils.request_builder import RequestBuilder


class Search:
    def __init__(self, request_builder: RequestBuilder):
        """The Search class provides the information and methods for searching resources on playstation network.

        .. note::

            This class is intended to be interfaced with through PSNAWP.

        :param request_builder: The instance of RequestBuilder. Used to make HTTPRequests.
        :type request_builder: RequestBuilder

        """
        self._request_builder = request_builder

    def universal_search(self, search_query: str, limit: int = 20) -> dict[str, Any]:
        """Searches the Playstation Website. Note: It does not work as of now and the endpoints returns whole html page.

        .. note::

            Pagination not yet supported. The max number of results returned will be 20.

        :param search_query: search query
        :type search_query: str
        :param limit: Limit of number of results
        :type limit: int

        :returns: A dict containing info similar to what is shown below (Not all values are shown because of space limitations):
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
        response: dict[str, Any] = self._request_builder.post(url=f"{BASE_PATH['universal_search']}", data=json.dumps(data)).json()
        return response

    def get_title_id(self, title_name: str) -> tuple[str, str]:
        """Gets the title id from title name using universal search endpoint.

        .. warning::

            Make sure to use the official full name of the video game otherwise the returned results may not be accurate. For example: GTA V returns the GTA
            Vice City since the Vice City shows up above GTA V. However, Grand Theft Auto V returns the correct results.

        :param title_name: Video Game title name
        :type title_name: str

        :returns: A tuple containing English Title Name and Title ID
        :rtype: tuple[str, str]

        """
        data = {
            "searchTerm": title_name,
            "domainRequests": [
                {
                    "domain": "ConceptGameMobileApp",
                    "pagination": {"cursor": "", "pageSize": 1},
                    "featureFlags": {"isSpartacusEnabled": True},
                }
            ],
            "countryCode": "us",
            "languageCode": "en",
            "age": 99,
        }
        response: dict[str, Any] = self._request_builder.post(url=f"{BASE_PATH['universal_search']}", data=json.dumps(data)).json()
        result = response["domainResponses"][0]["results"]
        if len(result) >= 1:
            t: tuple[str, str] = (
                result[0]["conceptProductMetadata"]["nameEn"],
                result[0]["conceptProductMetadata"]["titleId"],
            )
            title_name, title_id = t
        else:
            raise PSNAWPNotFound("Could not find Game by the that title name.")
        return title_name, title_id
