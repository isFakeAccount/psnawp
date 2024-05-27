import os

import pytest
from dotenv import load_dotenv
from psnawp_api import PSNAWP

load_dotenv()


@pytest.fixture(scope="session")
def psnawp_fixture():
    """Creates PSNAWP Instance Fixture for running all the units tests.

    :returns: PSNAWP Instance
    :rtype: PSNAWP

    """
    return PSNAWP(os.getenv("NPSSO_CODE", "NPSSO_CODE"))
