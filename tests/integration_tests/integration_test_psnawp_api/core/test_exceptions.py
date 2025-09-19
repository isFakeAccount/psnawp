import inspect

import pytest

from psnawp_api import PSNAWP
from psnawp_api.core import (
    PSNAWPBadRequestError,
)
from tests.integration_tests.integration_test_psnawp_api import my_vcr


@pytest.mark.vcr
def test_exception__exception_parsing(psnawp_fixture: PSNAWP) -> None:
    BAD_REQUEST_ERR_CODE = 2281473

    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        with pytest.raises(PSNAWPBadRequestError) as exec_info:
            user = psnawp_fixture.user(online_id="jeranther")
            user.friends_list(-1)

        assert exec_info.value.message == "Bad Request (query: limit)"
        assert exec_info.value.code == BAD_REQUEST_ERR_CODE
        assert isinstance(exec_info.value.reference_id, str)
