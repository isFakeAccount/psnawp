import inspect
import json
import os
from pathlib import Path
from time import time

import pytest

from psnawp_api import PSNAWP
from psnawp_api.core import PSNAWPAuthenticationError
from tests.integration_tests.integration_test_psnawp_api import my_vcr

token_response_path = Path(__file__).parent / "token_response.json"


@pytest.mark.integration
@pytest.mark.vcr
def test_authenticator__authentication() -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml", record_mode="all"):
        psnawp = PSNAWP(os.getenv("NPSSO_CODE", "NPSSO_CODE"))
        assert psnawp.me().online_id == os.getenv("USER_NAME")

        with token_response_path.open("w") as f:
            json.dump(psnawp.authenticator.token_response, f, indent=4)


@pytest.mark.integration
@pytest.mark.vcr
def test_authenticator__access_token_from_refresh_token():
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        psnawp = PSNAWP(os.getenv("NPSSO_CODE", "NPSSO_CODE"))
        client = psnawp.me()
        assert client.online_id == os.getenv("USER_NAME")

        if psnawp.authenticator.token_response is not None:
            # Force expire accesss_token so Authenticator class fetches new refresh_token
            psnawp.authenticator.token_response["access_token_expires_at"] = time() - 3600

        client = psnawp.me()
        assert client.online_id == os.getenv("USER_NAME")


@pytest.mark.integration
@pytest.mark.vcr
def test_authenticator__token_response() -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        with token_response_path.open("r") as f:
            token_response = json.load(f)

        psnawp = PSNAWP(npsso_cookie=None, token_response=token_response)
        assert psnawp.me().online_id == os.getenv("USER_NAME")


@pytest.mark.integration
@pytest.mark.vcr
def test_authenticator__incorrect_npsso() -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        psnawp = PSNAWP("dsjfhsdkjfhskjdhlf")
        with pytest.raises(PSNAWPAuthenticationError):
            assert psnawp.me().online_id == os.getenv("USER_NAME")
