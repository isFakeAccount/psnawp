import inspect
import os
from time import time

import pytest

from psnawp_api import PSNAWP
from psnawp_api.core import PSNAWPAuthenticationError
from tests.integration_tests.integration_test_psnawp_api import my_vcr


@pytest.mark.vcr
def test_authenticator__authentication() -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        psnawp = PSNAWP(os.getenv("NPSSO_CODE", "NPSSO_CODE"))
        psnawp.me().online_id


@pytest.mark.vcr
def test_authenticator__access_token_from_refresh_token():
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        psnawp = PSNAWP(os.getenv("NPSSO_CODE", "NPSSO_CODE"))
        client = psnawp.me()
        assert client.online_id == os.getenv("USER_NAME")

        if psnawp.authenticator.token_response is not None:
            # Force expire accesss_token so Authenticator class fetches new refresh_token
            psnawp.authenticator.token_response["access_token_expires_at"] = time() - 3600

        client = psnawp.me()
        assert client.online_id == os.getenv("USER_NAME")


@pytest.mark.vcr
def test_authenticator__incorrect_npsso() -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        with pytest.raises(PSNAWPAuthenticationError):
            psnawp = PSNAWP("dsjfhsdkjfhskjdhlf")
            psnawp.me().online_id
