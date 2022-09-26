import inspect
import os
import re

import pytest

import psnawp_api
from psnawp_api.core.psnawp_exceptions import PSNAWPIllegalArgumentError
from tests.unit_tests import my_vcr


@pytest.mark.vcr()
def test_client__authentication():
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        psnawp_api.psnawp.PSNAWP(os.getenv("NPSSO_CODE"))


@pytest.mark.vcr()
def test_client__incorrect_npsso():
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        with pytest.raises(PSNAWPIllegalArgumentError):
            psnawp_api.psnawp.PSNAWP("dsjfhsdkjfhskjdhlf")


@pytest.mark.vcr()
def test_client__online_id(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        client = psnawp_fixture.me()
        assert client.online_id == os.getenv("USER_NAME")


@pytest.mark.vcr()
def test_client__account_id(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        client = psnawp_fixture.me()
        assert re.match(r"\d{19}", client.account_id)


@pytest.mark.vcr()
def test_client__get_profile_legacy(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        client = psnawp_fixture.me()
        client.get_profile_legacy()


@pytest.mark.vcr()
def test_client__account_devices(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        client = psnawp_fixture.me()
        client.get_account_devices()


@pytest.mark.vcr()
def test_client__get_friends(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        client = psnawp_fixture.me()
        list(client.friends_list())


@pytest.mark.vcr()
def test_client__get_groups(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        client = psnawp_fixture.me()
        list(client.get_groups(limit=10))


@pytest.mark.vcr()
def test_client__available_to_play(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        client = psnawp_fixture.me()
        list(client.available_to_play())


@pytest.mark.vcr()
def test_client__blocked_list(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        client = psnawp_fixture.me()
        client.blocked_list()


@pytest.mark.vcr()
def test_client__repr_and_str(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        client = psnawp_fixture.me()
        repr(client)
        str(client)
