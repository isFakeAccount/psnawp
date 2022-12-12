import inspect

import pytest

from psnawp_api.core.psnawp_exceptions import (
    PSNAWPIllegalArgumentError,
    PSNAWPNotFound,
    PSNAWPForbidden,
)
from psnawp_api.models.trophies.trophy_constants import PlatformType
from tests.unit_tests import my_vcr


@pytest.mark.vcr()
def test_user__user(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        user_example = psnawp_fixture.user(online_id="VaultTec_Trading")
        assert user_example.online_id == "VaultTec_Trading"


@pytest.mark.vcr()
def test_user__user_account_id(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        user_example = psnawp_fixture.user(account_id="8520698476712646544")
        assert user_example.online_id == "VaultTec_Trading"


@pytest.mark.vcr()
def test_user__user_no_argument(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        with pytest.raises(PSNAWPIllegalArgumentError):
            psnawp_fixture.user()


@pytest.mark.vcr()
def test_user__user_wrong_acc_id(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        with pytest.raises(PSNAWPNotFound):
            psnawp_fixture.user(account_id="VaultTec-Co")


@pytest.mark.vcr()
def test_user__prev_online_id(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        user_example = psnawp_fixture.user(online_id="EvangelionKills")
        assert user_example.online_id == "kerksten"


@pytest.mark.vcr()
def test_user__user_not_found(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        with pytest.raises(PSNAWPNotFound):
            psnawp_fixture.user(online_id="dfhlidsahfdszh")


@pytest.mark.vcr()
def test_user__user_acct_id_not_found(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        with pytest.raises(PSNAWPNotFound):
            psnawp_fixture.user(account_id="0000000000000000000")


@pytest.mark.vcr()
def test_user__get_profile(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        profile = psnawp_fixture.user(online_id="VaultTec_Trading").profile()
        assert profile.get("onlineId") == "VaultTec_Trading"
        assert profile.get("aboutMe") == "r/Fallout76Marketplace Moderator"
        assert profile.get("languages") == ["en-US"]
        assert profile.get("isPlus") is False
        assert profile.get("isOfficiallyVerified") is False


@pytest.mark.vcr()
def test_user__get_presence(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        psnawp_fixture.user(online_id="VaultTec_Trading").get_presence()


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
def test_user__trophy_summary(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        summary = psnawp_fixture.user(online_id="VaultTec_Trading").trophy_summary()
        assert summary.account_id == "8520698476712646544"
        assert summary.earned_trophies.bronze == 0
        assert summary.earned_trophies.silver == 0
        assert summary.earned_trophies.gold == 0
        assert summary.earned_trophies.platinum == 0
        assert summary.progress == 0
        assert summary.tier == 1
        assert summary.trophy_level == 1


@pytest.mark.vcr()
def test_user__trophy_summary_forbidden(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        with pytest.raises(PSNAWPForbidden):
            psnawp_fixture.user(online_id="kerksten").trophy_summary()


@pytest.mark.vcr()
def test_user__trophy_titles(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        actual_count = 0
        for trophy_title in psnawp_fixture.user(online_id="jeranther").trophy_titles(limit=100):
            actual_count += 1

            if trophy_title.np_service_name == "trophy2":
                assert PlatformType.PS5 in trophy_title.title_platform
            else:
                assert PlatformType.PS5 not in trophy_title.title_platform
                assert bool(trophy_title.title_platform & {PlatformType.PS4, PlatformType.PS3, PlatformType.PS_VITA})

        assert actual_count == 100


@pytest.mark.vcr()
def test_user__trophy_titles_forbidden(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        with pytest.raises(PSNAWPForbidden):
            for trophy_title in psnawp_fixture.user(online_id="kerksten").trophy_titles(limit=100):
                print(trophy_title)


@pytest.mark.vcr()
def test_user__trophy_titles_pagination_test(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        total_count = 0
        actual_count = 0
        for trophy_title in psnawp_fixture.user(online_id="Ali_chabuk190").trophy_titles():
            total_count = trophy_title.total_items_count
            actual_count += 1

            if trophy_title.np_service_name == "trophy2":
                assert PlatformType.PS5 in trophy_title.title_platform
            else:
                assert PlatformType.PS5 not in trophy_title.title_platform
                assert bool(trophy_title.title_platform & {PlatformType.PS4, PlatformType.PS3, PlatformType.PS_VITA})

        assert total_count == actual_count


@pytest.mark.vcr()
def test_user__trophy_titles_for_title(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        for trophy_title in psnawp_fixture.user(online_id="jeranther").trophy_titles_for_title(title_ids=["PPSA01506_00", "CUSA12057_00", "CUSA00419_00"]):
            assert {PlatformType.UNKNOWN} == trophy_title.title_platform
            if trophy_title.title_name == "Fallout 76":
                assert trophy_title.np_communication_id == "NPWR15509_00"
                assert trophy_title.np_service_name == "trophy"
            elif trophy_title.title_name == "Immortals Fenyx Rising ™":
                assert trophy_title.np_communication_id == "NPWR21237_00"
                assert trophy_title.np_service_name == "trophy2"
            elif trophy_title.title_name == "Grand Theft Auto V":
                assert trophy_title.np_communication_id == "NPWR06221_00"
                assert trophy_title.np_service_name == "trophy"


@pytest.mark.vcr()
def test_user__trophy_titles_for_title_forbidden(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        with pytest.raises(PSNAWPForbidden):
            for trophy_title in psnawp_fixture.user(online_id="kerksten").trophy_titles_for_title(title_ids=["CUSA12057_00"]):
                print(trophy_title)


@pytest.mark.vcr()
def test_user__trophies(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        earned_status = list(psnawp_fixture.user(online_id="jeranther").trophies("NPWR15509_00", "PS4", limit=10))
        earned_status_with_metadata = list(psnawp_fixture.user(online_id="jeranther").trophies("NPWR15509_00", "PS4", limit=10, include_metadata=True))
        assert earned_status[0].total_items_count == earned_status_with_metadata[0].total_items_count
        for zipped_data in zip(earned_status, earned_status_with_metadata):
            assert zipped_data[0].trophy_id == zipped_data[1].trophy_id
            assert zipped_data[0].trophy_hidden == zipped_data[1].trophy_hidden
            assert zipped_data[0].earned == zipped_data[1].earned
            assert zipped_data[0].progress == zipped_data[1].progress
            assert zipped_data[0].progress_rate == zipped_data[1].progress_rate
            assert zipped_data[0].progressed_date_time == zipped_data[1].progressed_date_time
            assert zipped_data[0].earned_date_time == zipped_data[1].earned_date_time
            assert zipped_data[0].trophy_type == zipped_data[1].trophy_type
            assert zipped_data[0].trophy_rarity == zipped_data[1].trophy_rarity
            assert zipped_data[0].trophy_earn_rate == zipped_data[1].trophy_earn_rate


@pytest.mark.vcr()
def test_user__trophies_forbidden(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        with pytest.raises(PSNAWPForbidden):
            list(psnawp_fixture.user(online_id="kerksten").trophies("NPWR15509_00", "PS4", limit=10))

        with pytest.raises(PSNAWPForbidden):
            list(psnawp_fixture.user(online_id="kerksten").trophies("NPWR15509_00", "PS4", limit=10, include_metadata=True))


@pytest.mark.vcr()
def test_user__trophies_pagination_test(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        earned_status = list(psnawp_fixture.user(online_id="ikemenzi").trophies("NPWR08964_00", "PS4"))
        earned_status_with_metadata = list(psnawp_fixture.user(online_id="ikemenzi").trophies("NPWR08964_00", "PS4", include_metadata=True))
        assert earned_status[0].total_items_count == earned_status_with_metadata[0].total_items_count
        for zipped_data in zip(earned_status, earned_status_with_metadata):
            assert zipped_data[0].trophy_id == zipped_data[1].trophy_id
            assert zipped_data[0].trophy_hidden == zipped_data[1].trophy_hidden
            assert zipped_data[0].earned == zipped_data[1].earned
            assert zipped_data[0].progress == zipped_data[1].progress
            assert zipped_data[0].progress_rate == zipped_data[1].progress_rate
            assert zipped_data[0].progressed_date_time == zipped_data[1].progressed_date_time
            assert zipped_data[0].earned_date_time == zipped_data[1].earned_date_time
            assert zipped_data[0].trophy_type == zipped_data[1].trophy_type
            assert zipped_data[0].trophy_rarity == zipped_data[1].trophy_rarity
            assert zipped_data[0].trophy_earn_rate == zipped_data[1].trophy_earn_rate


@pytest.mark.vcr()
def test_user__trophy_groups_summary(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        earned_status = psnawp_fixture.user(online_id="jeranther").trophy_groups_summary("NPWR15509_00", "PS4")
        earned_status_with_metadata = psnawp_fixture.user(online_id="jeranther").trophy_groups_summary("NPWR15509_00", "PS4", include_metadata=True)

        assert earned_status.trophy_set_version == earned_status_with_metadata.trophy_set_version
        assert earned_status.hidden_flag == earned_status_with_metadata.hidden_flag
        assert earned_status.progress == earned_status_with_metadata.progress
        assert earned_status.earned_trophies == earned_status_with_metadata.earned_trophies
        assert earned_status.last_updated_date_time == earned_status_with_metadata.last_updated_date_time

        for zipped_data in zip(earned_status.trophy_groups, earned_status_with_metadata.trophy_groups):
            assert zipped_data[0].trophy_group_id == zipped_data[1].trophy_group_id
            assert zipped_data[0].progress == zipped_data[1].progress
            assert zipped_data[0].earned_trophies == zipped_data[1].earned_trophies
            assert zipped_data[0].last_updated_datetime == zipped_data[1].last_updated_datetime


@pytest.mark.vcr()
def test_user__trophy_groups_summary_forbidden(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        with pytest.raises(PSNAWPForbidden):
            psnawp_fixture.user(online_id="kerksten").trophy_groups_summary("NPWR15509_00", "PS4")

        with pytest.raises(PSNAWPForbidden):
            psnawp_fixture.user(online_id="kerksten").trophy_groups_summary("NPWR15509_00", "PS4", include_metadata=True)


@pytest.mark.vcr()
def test_user__title_stats(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        total_count = 0
        for title in psnawp_fixture.user(online_id="omzzz90").title_stats():
            total_count += 1
            assert len(title.title_id) > 0
        assert total_count > 0


@pytest.mark.vcr()
def test_user__repr_and_str(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        user_example = psnawp_fixture.user(online_id="VaultTec-Co")
        repr(user_example)
        str(user_example)
