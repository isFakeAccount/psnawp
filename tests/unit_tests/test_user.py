import inspect

import pytest

from psnawp_api.core.psnawp_exceptions import (
    PSNAWPIllegalArgumentError,
    PSNAWPNotFound,
    PSNAWPForbidden,
)
from tests.unit_tests import my_vcr


@pytest.mark.vcr()
def test_user__user(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        user_example = psnawp_fixture.user(online_id="VaultTec-Co")
        assert user_example.online_id == "VaultTec-Co"


@pytest.mark.vcr()
def test_user__user_account_id(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        user_example = psnawp_fixture.user(account_id="2721516955383551246")
        assert user_example.online_id == "VaultTec-Co"


@pytest.mark.vcr()
def test_user__user_no_argument(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        with pytest.raises(PSNAWPIllegalArgumentError):
            psnawp_fixture.user()


@pytest.mark.vcr()
def test_user__user_wrong_acc_id(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        with pytest.raises(PSNAWPIllegalArgumentError):
            psnawp_fixture.user(account_id="VaultTec-Co")


def test_user__prev_online_id(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        user_example = psnawp_fixture.user(online_id="EvangelionKills")
        assert user_example.prev_online_id == "EvangelionKills"
        assert user_example.online_id == "kerksten"


def test_user__user_not_found(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        with pytest.raises(PSNAWPNotFound):
            psnawp_fixture.user(online_id="dfhlidsahfdszh")


def test_user__user_acct_id_not_found(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        with pytest.raises(PSNAWPNotFound):
            psnawp_fixture.user(account_id="0000000000000000000")


@pytest.mark.vcr()
def test_user__get_presence(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        psnawp_fixture.user(online_id="VaultTec-Co").get_presence()


@pytest.mark.vcr()
def test_user__get_presence_forbidden(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        with pytest.raises(PSNAWPForbidden):
            psnawp_fixture.user(online_id="kerksten").get_presence()


@pytest.mark.vcr()
def test_user__friendship(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        psnawp_fixture.user(online_id="jeranther").friendship()


@pytest.mark.vcr()
def test_user__is_blocked(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        assert not psnawp_fixture.user(online_id="jeranther").is_blocked()


@pytest.mark.vcr()
def test_user__repr_and_str(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        user_example = psnawp_fixture.user(online_id="VaultTec-Co")
        repr(user_example)
        str(user_example)
