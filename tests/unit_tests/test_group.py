import inspect

import pytest

from psnawp_api.core.psnawp_exceptions import (
    PSNAWPIllegalArgumentError,
    PSNAWPNotFound,
    PSNAWPNotAllowed,
)
from tests.unit_tests import my_vcr


@pytest.mark.vcr()
def test_client__group_incorrect_args(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        with pytest.raises(PSNAWPIllegalArgumentError):
            psnawp_fixture.group(
                group_id="~25C4C5406FD6D50E.763F9A1EB6AB5790", users_list=["Help"]
            )


@pytest.mark.vcr()
def test_client__group_with_id(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        group = psnawp_fixture.group(group_id="~25C4C5406FD6D50E.763F9A1EB6AB5790")
        group.send_message("Hello World")


@pytest.mark.vcr()
def test_client__group_with_wrong_id(psnawp_fixture):
    with pytest.raises(PSNAWPNotFound):
        with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
            psnawp_fixture.group(group_id="~25C4C5406FD6D50E.763F9A1EB6AB5791")


@pytest.mark.vcr()
def test_client__group_with_users(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        example_user = psnawp_fixture.user(online_id="VaultTec-Co")
        group = psnawp_fixture.group(users_list=[example_user])
        message_info = group.send_message("Hello World")

        messages = group.get_conversation(1).get("messages")
        assert message_info.get("messageUid") == messages[0].get("messageUid")


@pytest.mark.vcr()
def test_client__change_name(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        group = psnawp_fixture.group(
            group_id="38335156987791a6750a33ae452ec8666177b65e-103"
        )
        group.change_name("Testing API")


@pytest.mark.vcr()
def test_client__change_name_dm(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        with pytest.raises(PSNAWPNotAllowed):
            group = psnawp_fixture.group(group_id="~25C4C5406FD6D50E.763F9A1EB6AB5790")
            group.change_name("Testing API")


@pytest.mark.vcr()
def test_client__leave_group(psnawp_fixture):
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.yaml"):
        group = next(psnawp_fixture.me().get_groups(limit=1))
        group.leave_group()
