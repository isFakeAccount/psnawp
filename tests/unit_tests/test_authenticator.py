import inspect
import os
import time

import pytest

import psnawp_api
from tests.unit_tests import my_vcr


@pytest.mark.vcr()
def test_authenticator__access_token_from_refresh_token():
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        psnawp = psnawp_api.psnawp.PSNAWP(os.getenv("NPSSO_CODE"))
        psnawp._request_builder.authenticator._auth_properties["access_token_expires_at"] = time.time() - 3600
        client = psnawp.me()
        assert client.online_id == os.getenv("USER_NAME")
