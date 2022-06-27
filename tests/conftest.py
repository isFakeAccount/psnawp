import os

import pytest

import psnawp_api


@pytest.fixture(scope="session")
def psnawp_fixture():
    return psnawp_api.psnawp.PSNAWP(os.getenv("NPSSO_CODE"))
