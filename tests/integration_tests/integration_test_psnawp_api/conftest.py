from os import getenv

import pytest
from dotenv import load_dotenv

from psnawp_api import PSNAWP
from psnawp_api.models.user import User

load_dotenv()

FRIEND_USER_NAME = getenv("FRIEND_USER_NAME", default="FRIEND_USER_NAME")
BLOCKED_USER_NAME = getenv("BLOCKED_USER_NAME", "BLOCKED_USER_NAME")
assert FRIEND_USER_NAME != "FRIEND_USER_NAME", "FRIEND_USER_NAME is not set. Please set it in .env file along with NPSSO."
assert BLOCKED_USER_NAME != "BLOCKED_USER_NAME", "BLOCKED_USER_NAME is not set. Please set it in .env file along with NPSSO."


@pytest.fixture(scope="session")
def psnawp_fixture() -> PSNAWP:
    """
    Creates PSNAWP Instance Fixture for running all the units tests.

    :returns: PSNAWP Instance
    :rtype: PSNAWP

    """
    return PSNAWP(getenv("NPSSO_CODE", "NPSSO_CODE"))


@pytest.fixture(scope="session")
def friend_user() -> User:
    psnawp = PSNAWP(getenv("NPSSO_CODE", "NPSSO_CODE"))
    return psnawp.user(online_id=FRIEND_USER_NAME)


@pytest.fixture(scope="session")
def blocked_user() -> User:
    psnawp = PSNAWP(getenv("NPSSO_CODE", "NPSSO_CODE"))
    return psnawp.user(online_id=BLOCKED_USER_NAME)
