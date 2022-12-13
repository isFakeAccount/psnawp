import os

import pytest
from dotenv import load_dotenv

from psnawp_api import PSNAWP

load_dotenv()


@pytest.fixture(scope="session")
def psnawp_fixture():
    return PSNAWP(os.getenv("NPSSO_CODE"))
