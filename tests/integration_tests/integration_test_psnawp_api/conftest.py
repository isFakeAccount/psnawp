from os import getenv
from pathlib import Path

import pytest
from dotenv import load_dotenv
from pyrate_limiter.abstracts.rate import Duration, Rate

from psnawp_api import PSNAWP
from psnawp_api.models.user import User

load_dotenv()

FRIEND_USER_NAME = getenv("FRIEND_USER_NAME", default="FRIEND_USER_NAME")
BLOCKED_USER_NAME = getenv("BLOCKED_USER_NAME", "BLOCKED_USER_NAME")
assert FRIEND_USER_NAME != "FRIEND_USER_NAME", "FRIEND_USER_NAME is not set. Please set it in .env file along with NPSSO."
assert BLOCKED_USER_NAME != "BLOCKED_USER_NAME", "BLOCKED_USER_NAME is not set. Please set it in .env file along with NPSSO."


def config_rate_limit() -> Rate:
    """Deternintes rate limit based on presence of cassette files.

    If we have cassette files then the rate limit doesn't need to be as throttled since requests aren't hitting the
    server. Otherwise, throttle the requests to avoid bombarding playstation servers with requests.

    :returns: The rate limit based on whether tests are in playback mode or not.

    """
    cassettes_dir = Path(__file__).parent / "cassettes"
    cassettes_files = cassettes_dir.glob("*.json")

    if len(list(cassettes_files)) > 0:
        return Rate(1, Duration.SECOND * 0.25)

    return Rate(1, Duration.SECOND * 3)


@pytest.fixture(scope="session")
def psnawp_fixture() -> PSNAWP:
    """Creates PSNAWP Instance Fixture for running all the units tests.

    :returns: PSNAWP Instance
    :rtype: PSNAWP

    """
    new_rate_limit = config_rate_limit()
    return PSNAWP(getenv("NPSSO_CODE", "NPSSO_CODE"), rate_limit=new_rate_limit)


@pytest.fixture(scope="session")
def friend_user() -> User:
    psnawp = PSNAWP(getenv("NPSSO_CODE", "NPSSO_CODE"))
    return psnawp.user(online_id=FRIEND_USER_NAME)


@pytest.fixture(scope="session")
def blocked_user() -> User:
    psnawp = PSNAWP(getenv("NPSSO_CODE", "NPSSO_CODE"))
    return psnawp.user(online_id=BLOCKED_USER_NAME)
