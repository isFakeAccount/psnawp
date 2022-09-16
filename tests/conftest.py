import os

import pytest

from psnawp_api import PSNAWP


@pytest.fixture(scope="session")
def psnawp_fixture():
    return PSNAWP(os.getenv("NPSSO_CODE"))
