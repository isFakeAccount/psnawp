import inspect
import os
import re

import pytest

import psnawp_api
from psnawp_api.core.psnawp_exceptions import PSNAWPAuthenticationError, PSNAWPNotFound
from tests.unit_tests import my_vcr


@pytest.mark.vcr()
def test_client__authentication():
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        psnawp_api.psnawp.PSNAWP(os.getenv("NPSSO_CODE"))


@pytest.mark.vcr()
def test_client__incorrect_npsso():
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        with pytest.raises(PSNAWPAuthenticationError):
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
        assert re.match(r"\d+", client.account_id)


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
def test_client__trophy_summary(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        summary = psnawp_fixture.me().trophy_summary()
        assert summary.account_id == "me"
        assert summary.earned_trophies.bronze == 0
        assert summary.earned_trophies.silver == 0
        assert summary.earned_trophies.gold == 0
        assert summary.earned_trophies.platinum == 0
        assert summary.progress == 0
        assert summary.tier == 1
        assert summary.trophy_level == 1


@pytest.mark.vcr()
def test_client__trophy_titles(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        for trophy_title in psnawp_fixture.me().trophy_titles():
            print(trophy_title)


@pytest.mark.vcr()
def test_client__trophy_titles_for_title(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        for trophy_title in psnawp_fixture.me().trophy_titles_for_title(title_ids=["CUSA12057_00"]):
            print(trophy_title)


@pytest.mark.vcr()
def test_client__trophies(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        with pytest.raises(PSNAWPNotFound):
            for trophy in psnawp_fixture.me().trophies("NPWR15179_00", "PS4"):
                print(trophy)

        with pytest.raises(PSNAWPNotFound):
            for trophy in psnawp_fixture.me().trophies("NPWR15179_00", "PS4", include_metadata=True):
                print(trophy)


@pytest.mark.vcr()
def test_client__trophy_groups_summary(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        with pytest.raises(PSNAWPNotFound):
            psnawp_fixture.me().trophy_groups_summary("NPWR15179_00", "PS4", include_metadata=False)

        with pytest.raises(PSNAWPNotFound):
            psnawp_fixture.me().trophy_groups_summary("NPWR15179_00", "PS4", include_metadata=True)


@pytest.mark.vcr()
def test_client__title_stats(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        for title in psnawp_fixture.me().title_stats():
            print(title)


@pytest.mark.vcr()
def test_client__repr_and_str(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        client = psnawp_fixture.me()
        repr(client)
        str(client)
