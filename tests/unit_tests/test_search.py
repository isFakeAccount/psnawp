import inspect

import pytest

from psnawp_api.core.psnawp_exceptions import PSNAWPNotFound
from tests.unit_tests import my_vcr


@pytest.mark.vcr()
def test_search__universal_search(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        search = psnawp_fixture.search()
        search.universal_search(search_query="GTA", limit=1)


@pytest.mark.vcr()
def test_search__get_title_id(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        search = psnawp_fixture.search()
        assert search.get_title_id("Minecraft") == ("Minecraft", "CUSA00744_00")
        assert search.get_title_id("Grand Theft Auto V") == ("Grand Theft Auto V: Premium Edition", "CUSA00419_00")
        assert search.get_title_id("Fallout 76") == ("Fallout 76", "CUSA12057_00")


@pytest.mark.vcr()
def test_search__get_title_id_wrong_title(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        with pytest.raises(PSNAWPNotFound):
            search = psnawp_fixture.search()
            search.get_title_id("dsfasdfadsf")
