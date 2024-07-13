import inspect
from os import getenv

import jsonschema
import pytest
from psnawp_api import PSNAWP
from psnawp_api.core import (
    PSNAWPForbidden,
    PSNAWPIllegalArgumentError,
    PSNAWPNotFound,
)
from psnawp_api.models import User
from psnawp_api.models.trophies import PlatformType

from tests.integration_tests.integration_test_psnawp_api import my_vcr

FRIEND_USER_NAME = getenv("FRIEND_USER_NAME", default="FRIEND_USER_NAME")
assert FRIEND_USER_NAME != "FRIEND_USER_NAME", "FRIEND_USER_NAME is not set. Please set it in .env file along with NPSSO."


@pytest.mark.vcr()
def test_user__user(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        user_example = psnawp_fixture.user(online_id=FRIEND_USER_NAME)
        assert user_example.online_id == FRIEND_USER_NAME


@pytest.mark.vcr()
def test_user__user_account_id(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        user_example = psnawp_fixture.user(account_id="8520698476712646544")
        assert user_example.online_id == "VaultTec_Trading"


@pytest.mark.vcr()
def test_user__user_no_argument(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        with pytest.raises(PSNAWPIllegalArgumentError):
            psnawp_fixture.user()


@pytest.mark.vcr()
def test_user__user_wrong_acc_id(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        with pytest.raises(PSNAWPNotFound):
            psnawp_fixture.user(account_id="VaultTec-Co")


@pytest.mark.vcr()
def test_user__prev_online_id(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        user_example = psnawp_fixture.user(online_id="EvangelionKills")
        assert user_example.online_id == "kerksten"


@pytest.mark.vcr()
def test_user__user_not_found(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        with pytest.raises(PSNAWPNotFound):
            psnawp_fixture.user(online_id="dfhlidsahfdszh")


@pytest.mark.vcr()
def test_user__user_acct_id_not_found(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        with pytest.raises(PSNAWPNotFound):
            psnawp_fixture.user(account_id="0000000000000000000")


@pytest.mark.vcr()
def test_user__get_profile(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        profile = psnawp_fixture.user(online_id="VaultTec_Trading").profile()
        assert profile.get("onlineId") == "VaultTec_Trading"
        assert profile.get("aboutMe") == "r/Fallout76Marketplace Moderator"
        assert profile.get("languages") == ["en-US"]
        assert profile.get("isPlus") is False
        assert profile.get("isOfficiallyVerified") is False


@pytest.mark.vcr()
def test_user__get_presence(friend_user: User) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        friend_user.get_presence()


@pytest.mark.vcr()
def test_user__get_presence_forbidden(blocked_user: User) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        with pytest.raises(PSNAWPForbidden):
            blocked_user.get_presence()


@pytest.mark.vcr()
def test_user__friendship(friend_user: User) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        response = friend_user.friendship()

        expected_schema = {
            "type": "object",
            "properties": {
                "friendRelation": {"type": "string"},
                "personalDetailSharing": {"type": "string"},
                "friendsCount": {"type": "integer"},
                "mutualFriendsCount": {"type": "integer"},
            },
            "required": ["friendRelation", "personalDetailSharing", "friendsCount", "mutualFriendsCount"],
        }

        # Validate the JSON structure against the schema
        try:
            jsonschema.validate(instance=response, schema=expected_schema)
        except jsonschema.ValidationError as e:
            pytest.fail(f"JSON structure validation failed: {e.message}")


@pytest.mark.vcr()
def test_user__accept_friend_request(friend_user: User) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        friend_user.accept_friend_request()


@pytest.mark.vcr()
def test_user__remove_friend(friend_user: User) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        friend_user.remove_friend()


@pytest.mark.vcr()
def test_user__get_friends(friend_user: User) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        list(friend_user.friends_list())


@pytest.mark.vcr()
def test_user__get_friends_forbidden(blocked_user: User) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        with pytest.raises(PSNAWPForbidden):
            list(blocked_user.friends_list())


@pytest.mark.vcr()
def test_user__is_blocked(friend_user: User) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        assert not friend_user.is_blocked()


@pytest.mark.vcr()
def test_user__trophy_summary(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
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
def test_user__trophy_summary_forbidden(blocked_user: User) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        with pytest.raises(PSNAWPForbidden):
            blocked_user.trophy_summary()


@pytest.mark.vcr()
def test_user__trophy_titles(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        user = psnawp_fixture.user(online_id="ikemenzi")
        actual_count = 0
        for trophy_title in user.trophy_titles(limit=100):
            actual_count += 1

            if trophy_title.np_service_name == "trophy2":
                assert PlatformType.PS5 in trophy_title.title_platform
            else:
                assert PlatformType.PS5 not in trophy_title.title_platform
                assert bool(trophy_title.title_platform & {PlatformType.PS4, PlatformType.PS3, PlatformType.PS_VITA})

        assert actual_count == 100


@pytest.mark.vcr()
def test_user__trophy_titles_forbidden(blocked_user: User) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        with pytest.raises(PSNAWPForbidden):
            for trophy_title in blocked_user.trophy_titles(limit=100):
                print(trophy_title)


@pytest.mark.vcr()
def test_user__trophy_titles_pagination_test(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        trophy_iter = psnawp_fixture.user(online_id="Ali_chabuk190").trophy_titles()
        actual_count = 0
        for trophy_title in trophy_iter:
            actual_count += 1

            if trophy_title.np_service_name == "trophy2":
                assert PlatformType.PS5 in trophy_title.title_platform
            else:
                assert PlatformType.PS5 not in trophy_title.title_platform
                assert bool(trophy_title.title_platform & {PlatformType.PS4, PlatformType.PS3, PlatformType.PS_VITA})

        assert len(trophy_iter) == actual_count


@pytest.mark.vcr()
def test_user__trophy_titles_for_title(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        for trophy_title in psnawp_fixture.user(online_id="jeranther").trophy_titles_for_title(title_ids=["PPSA01506_00", "CUSA12057_00", "CUSA00419_00"]):
            assert {PlatformType.UNKNOWN} == trophy_title.title_platform
            if trophy_title.title_name == "Fallout 76":
                assert trophy_title.np_communication_id == "NPWR15509_00"
                assert trophy_title.np_service_name == "trophy"
                assert trophy_title.np_title_id == "CUSA12057_00"
            elif trophy_title.title_name == "Immortals Fenyx Rising ™":
                assert trophy_title.np_communication_id == "NPWR21237_00"
                assert trophy_title.np_service_name == "trophy2"
                assert trophy_title.np_title_id == "PPSA01506_00"
            elif trophy_title.title_name == "Grand Theft Auto V":
                assert trophy_title.np_communication_id == "NPWR06221_00"
                assert trophy_title.np_service_name == "trophy"
                assert trophy_title.np_title_id == "CUSA00419_00"


@pytest.mark.vcr()
def test_user__trophy_titles_for_title_forbidden(blocked_user: User) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        with pytest.raises(PSNAWPForbidden):
            for trophy_title in blocked_user.trophy_titles_for_title(title_ids=["CUSA12057_00"]):
                print(trophy_title)


@pytest.mark.vcr()
def test_user__trophies(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        user = psnawp_fixture.user(online_id="jeranther")
        earned_status = list(user.trophies("NPWR15509_00", PlatformType.PS4, limit=10))
        earned_status_with_metadata = list(user.trophies("NPWR15509_00", PlatformType.PS4, limit=10, include_progress=True))
        for zipped_data in zip(earned_status, earned_status_with_metadata):
            assert zipped_data[0].trophy_id == zipped_data[1].trophy_id
            assert zipped_data[0].trophy_hidden == zipped_data[1].trophy_hidden
            assert zipped_data[0].trophy_type == zipped_data[1].trophy_type

        assert len(earned_status) == 10
        assert len(earned_status) == len(earned_status_with_metadata)


@pytest.mark.vcr()
def test_user__trophies_with_progress_forbidden(blocked_user: User) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        with pytest.raises(PSNAWPForbidden):
            list(blocked_user.trophies("NPWR15509_00", PlatformType.PS4, limit=10, include_progress=True))


@pytest.mark.vcr()
def test_user__trophies_pagination_test(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        user = psnawp_fixture.user(online_id="ikemenzi")
        earned_status = list(user.trophies("NPWR08964_00", PlatformType.PS4))
        earned_status_with_metadata = list(user.trophies("NPWR08964_00", PlatformType.PS4, include_progress=True))
        for zipped_data in zip(earned_status, earned_status_with_metadata):
            assert zipped_data[0].trophy_id == zipped_data[1].trophy_id
            assert zipped_data[0].trophy_hidden == zipped_data[1].trophy_hidden
            assert zipped_data[0].trophy_type == zipped_data[1].trophy_type

        assert len(earned_status) == len(earned_status_with_metadata)


@pytest.mark.vcr()
def test_user__trophy_groups_summary(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        user = psnawp_fixture.user(online_id="jeranther")
        earned_status = user.trophy_groups_summary("NPWR15509_00", PlatformType.PS4)
        earned_status_with_metadata = user.trophy_groups_summary("NPWR15509_00", PlatformType.PS4, include_progress=True)

        for zipped_data in zip(earned_status.trophy_groups, earned_status_with_metadata.trophy_groups):
            assert zipped_data[0].defined_trophies == zipped_data[1].defined_trophies
            assert zipped_data[0].trophy_group_detail == zipped_data[1].trophy_group_detail
            assert zipped_data[0].trophy_group_icon_url == zipped_data[1].trophy_group_icon_url
            assert zipped_data[0].trophy_group_id == zipped_data[1].trophy_group_id
            assert zipped_data[0].trophy_group_name == zipped_data[1].trophy_group_name


@pytest.mark.vcr()
def test_user__trophy_groups_summary_forbidden(blocked_user: User) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        with pytest.raises(PSNAWPForbidden):
            blocked_user.trophy_groups_summary("NPWR15509_00", PlatformType.PS4, include_progress=True)


@pytest.mark.vcr()
def test_user__title_stats(friend_user: User) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        total_count = 0
        title_stat_iter = friend_user.title_stats()
        for _ in title_stat_iter:
            total_count += 1
        assert total_count == len(title_stat_iter)


@pytest.mark.vcr()
def test_user__title_stats_with_limit(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        limit = 1050
        titles = psnawp_fixture.user(online_id="ikemenzi").title_stats(limit=limit)
        title_count = len(list(titles))
        assert title_count == limit


@pytest.mark.vcr()
def test_user__title_stats_with_jump(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        limit = 10
        titles = list(psnawp_fixture.user(online_id="ikemenzi").title_stats(limit=limit))
        tenth_title = next(psnawp_fixture.user(online_id="ikemenzi").title_stats(limit=limit, offset=9))
        assert titles[9] == tenth_title


@pytest.mark.vcr()
def test_user__repr_and_str(friend_user: User) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        repr(friend_user)
        str(friend_user)
