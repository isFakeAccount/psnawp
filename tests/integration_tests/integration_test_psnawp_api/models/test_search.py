import inspect

import pytest

from psnawp_api import PSNAWP
from psnawp_api.models.search import SearchDomain
from tests.integration_tests.integration_test_psnawp_api import my_vcr


@pytest.mark.vcr
def test_search__universal_search(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        search = psnawp_fixture.search(search_query="GTA", search_domain=SearchDomain.FULL_GAMES, limit=1)
        actual_count = 0
        for _ in search:
            actual_count += 1
        assert actual_count == 1


@pytest.mark.vcr
def test_search__get_game_content_id(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        search = psnawp_fixture.search(search_query="GTA", search_domain=SearchDomain.FULL_GAMES, limit=1)
        for result in search:
            assert result["result"]["invariantName"] == "Grand Theft Auto V (PlayStation®5)"
            assert result["result"]["defaultProduct"]["id"] == "UP1004-PPSA03420_00-GTAOSTANDALONE01"
            break


@pytest.mark.vcr
def test_search__get_game_content_pagination_test(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        item_limit = 25
        search = psnawp_fixture.search(search_query="GTA", search_domain=SearchDomain.FULL_GAMES, limit=item_limit)
        count = 0
        for _ in search:
            count += 1
        assert count == item_limit


@pytest.mark.vcr
def test_search__get_addon_content_id(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        search = psnawp_fixture.search(search_query="GTA", search_domain=SearchDomain.ADD_ONS, limit=1)
        for result in search:
            assert result["result"]["invariantName"] == "GTA Online: Great White Shark Cash Card (PS5™)"
            assert result["result"]["id"] == "UP1004-PPSA03420_00-GTAVPS5CASHPACK4"
            break


@pytest.mark.vcr
def test_search__get_get_addon_pagination_test(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        item_limit = 15
        search = psnawp_fixture.search(search_query="GTA", search_domain=SearchDomain.ADD_ONS, page_size=5, limit=item_limit)
        count = 0
        for _ in search:
            count += 1
        assert count == item_limit


@pytest.mark.vcr
def test_search__get_user_id(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        search = psnawp_fixture.search(search_query="test", search_domain=SearchDomain.USERS, limit=1)
        for result in search:
            assert result["__typename"] == "SearchResultItem"
            assert result["id"] == "JGFwcjEkYXNka2ZqYWwkWkZIQlA3anZLVW9rQ0pQRk5wVlp0MA=="
            break


@pytest.mark.vcr
def test_search__get_user_pagination_test(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        search = psnawp_fixture.search(search_query="test", search_domain=SearchDomain.USERS, limit=None)
        count = 0
        for _ in search:
            count += 1
        assert count > 0


@pytest.mark.vcr
def test_search__get_user_pagination__limit_test(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        item_limit = 25
        search = psnawp_fixture.search(search_query="test", search_domain=SearchDomain.USERS, limit=item_limit)
        count = 0
        for _ in search:
            count += 1
        assert count == item_limit
