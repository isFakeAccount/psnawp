import inspect
import os
import re

import pytest

import psnawp_api
from tests.unit_tests import my_vcr


def test__online_id():
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        psnawp = psnawp_api.psnawp.PSNAWP(os.getenv("NPSSO_CODE"))
        client = psnawp.me()
        assert client.get_online_id() == os.getenv("USER_NAME")


def test__account_id():
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        psnawp = psnawp_api.psnawp.PSNAWP(os.getenv("NPSSO_CODE"))
        client = psnawp.me()
        assert re.match(r"\d{19}", client.get_account_id())


@pytest.mark.skip(reason="Not implemented yet")
def test__account_devices():
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        psnawp = psnawp_api.psnawp.PSNAWP(os.getenv("NPSSO_CODE"))
        client = psnawp.me()
        client.get_account_devices()


def test__get_friends():
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        psnawp = psnawp_api.psnawp.PSNAWP(os.getenv("NPSSO_CODE"))
        client = psnawp.me()
        client.friends_list()


def test__blocked_list():
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        psnawp = psnawp_api.psnawp.PSNAWP(os.getenv("NPSSO_CODE"))
        client = psnawp.me()
        client.blocked_list()
