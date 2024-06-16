import inspect

import pytest
from psnawp_api import PSNAWP
from psnawp_api.core import PSNAWPBadRequest, PSNAWPForbidden, PSNAWPIllegalArgumentError, PSNAWPNotFound
from psnawp_api.models import User

from tests.integration_tests.integration_test_psnawp_api import my_vcr


@pytest.mark.vcr()
def test_group__group_incorrect_args(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        with pytest.raises(PSNAWPIllegalArgumentError):
            psnawp_fixture.group(group_id="~25C4C5406FD6D50E.763F9A1EB6AB5790", users_list=["Help"])


@pytest.mark.vcr()
def test_group__group_with_wrong_id(psnawp_fixture: PSNAWP) -> None:
    with pytest.raises(PSNAWPNotFound):
        with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
            group = psnawp_fixture.group(group_id="~25C4C5406FD6D50E.763F9A1EB6AB5791")
            group.send_message("Hi")


@pytest.mark.vcr()
def test_group__group_with_users(psnawp_fixture: PSNAWP, friend_user: User):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        group = psnawp_fixture.group(users_list=[friend_user])
        message_info = group.send_message("Hello World")

        messages = group.get_conversation(1).get("messages")
        assert message_info.get("messageUid") == messages[0].get("messageUid")


@pytest.mark.vcr()
def test_group__group_with_id(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        last_group = next(psnawp_fixture.me().get_groups(limit=1))
        assert last_group.group_id is not None
        group = psnawp_fixture.group(group_id=last_group.group_id)
        group.send_message("Hello World!")


@pytest.mark.vcr()
def test_group__repr_and_str(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        last_group = next(psnawp_fixture.me().get_groups(limit=1))
        repr(last_group)
        str(last_group)


@pytest.mark.vcr()
def test_group__change_name_dm(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        with pytest.raises(PSNAWPBadRequest):
            last_group = next(psnawp_fixture.me().get_groups(limit=1))
            assert last_group.group_id is not None
            group = psnawp_fixture.group(group_id=last_group.group_id)
            group.change_name("Testing API")


@pytest.mark.vcr()
def test_group__dming_blocked_user(psnawp_fixture: PSNAWP, blocked_user: User) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        with pytest.raises(PSNAWPForbidden):
            group = psnawp_fixture.group(users_list=[blocked_user])
            group.send_message("Hello!")


@pytest.mark.vcr()
def test_group__change_name(psnawp_fixture: PSNAWP, friend_user: User, blocked_user: User) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        group = psnawp_fixture.group(users_list=[friend_user, blocked_user])
        group.change_name("Testing API")


@pytest.mark.vcr()
def test_group__leave_group(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        group = next(psnawp_fixture.me().get_groups(limit=1))
        group.leave_group()
