import inspect

import pytest

from tests.unit_tests import my_vcr


@pytest.mark.vcr()
def test_search__universal_search(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        search = psnawp_fixture.search()
        search.universal_search(search_query="GTA", limit=1)


def test_search__get_title_details(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        search = psnawp_fixture.search()
        title_details = search.get_title_details(title_id="PPSA03420_00")
        assert title_details[0].get("name") == "Grand Theft Auto V (PlayStation®5)"
