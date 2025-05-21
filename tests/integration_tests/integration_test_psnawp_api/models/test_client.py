from __future__ import annotations

import inspect
import json
import os
import re
from pathlib import Path

import pytest
from jsonschema import ValidationError, validate
from pycountry.db import Country

from psnawp_api import PSNAWP
from psnawp_api.core import PSNAWPNotFoundError
from psnawp_api.models.trophies import PlatformType
from tests.integration_tests.integration_test_psnawp_api import my_vcr


@pytest.mark.vcr
def test_client__online_id(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        client = psnawp_fixture.me()
        assert client.online_id == os.getenv("USER_NAME")


@pytest.mark.vcr
def test_client__account_id(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        client = psnawp_fixture.me()
        assert re.match(r"\d+", client.account_id)


@pytest.mark.vcr
def test_client__get_profile_legacy(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        client = psnawp_fixture.me()
        client.get_profile_legacy()


@pytest.mark.vcr
def test_client__account_devices(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        client = psnawp_fixture.me()
        client.get_account_devices()


@pytest.mark.vcr
def test_client__get_friends(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        client = psnawp_fixture.me()
        list(client.friends_list())


@pytest.mark.vcr
def test_client__friend_requests(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        client = psnawp_fixture.me()
        assert len(list(client.friend_requests())) > 0


@pytest.mark.vcr
def test_client__friend_requests(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        client = psnawp_fixture.me()
        assert len(list(client.friend_requests())) > 0


@pytest.mark.vcr
def test_client__get_presences(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        client = psnawp_fixture.me()
        friends_list = [user.account_id for user in client.friends_list()]
        presences = client.get_presences(friends_list)

        with Path("tests/integration_tests/integration_test_psnawp_api/json_schema/models/client/get_presences.json").open("r") as schema_file:
            schema = json.load(schema_file)

        try:
            validate(instance=presences, schema=schema)
        except ValidationError as e:
            pytest.fail(f"Validation failed: {e.message}")


@pytest.mark.vcr
def test_client__get_groups(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        client = psnawp_fixture.me()
        list(client.get_groups(limit=10))


@pytest.mark.vcr
def test_client__available_to_play(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        client = psnawp_fixture.me()
        list(client.available_to_play())


@pytest.mark.vcr
def test_client__blocked_list(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        client = psnawp_fixture.me()
        client.blocked_list()


@pytest.mark.vcr
def test_client__get_shareable_profile_link(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        client = psnawp_fixture.me()
        client.get_shareable_profile_link()


@pytest.mark.vcr
def test_client__trophy_summary(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        summary = psnawp_fixture.me().trophy_summary()
        assert summary.account_id == "me"
        assert summary.earned_trophies.bronze == 0
        assert summary.earned_trophies.silver == 0
        assert summary.earned_trophies.gold == 0
        assert summary.earned_trophies.platinum == 0
        assert summary.progress == 0
        assert summary.tier == 1
        assert summary.trophy_level == 1


@pytest.mark.vcr
def test_client__trophy_titles(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        for trophy_title in psnawp_fixture.me().trophy_titles():
            print(trophy_title)


@pytest.mark.vcr
def test_client__trophy_titles_for_title(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        for trophy_title in psnawp_fixture.me().trophy_titles_for_title(title_ids=["CUSA12057_00"]):
            print(trophy_title)


@pytest.mark.vcr
def test_client__trophies(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        for trophy in psnawp_fixture.me().trophies("NPWR15179_00", PlatformType.PS4):
            print(trophy)


@pytest.mark.vcr
def test_client__trophies_with_progress(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        with pytest.raises(PSNAWPNotFoundError):
            for trophy in psnawp_fixture.me().trophies(
                np_communication_id="NPWR15179_00",
                platform=PlatformType.PS4,
                include_progress=True,
            ):
                print(trophy)


@pytest.mark.vcr
def test_client__trophy_groups_summary(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        psnawp_fixture.me().trophy_groups_summary(
            np_communication_id="NPWR15179_00",
            platform=PlatformType.PS4,
            include_progress=False,
        )


@pytest.mark.vcr
def test_client__trophy_groups_summary_with_progress(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        with pytest.raises(PSNAWPNotFoundError):
            psnawp_fixture.me().trophy_groups_summary(
                np_communication_id="NPWR15179_00",
                platform=PlatformType.PS4,
                include_progress=True,
            )


@pytest.mark.vcr
def test_client__title_stats(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        for title in psnawp_fixture.me().title_stats():
            print(title)


@pytest.mark.vcr
def test_client__game_entitlements_with_limit(psnawp_fixture: PSNAWP) -> None:
    limit = 25
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        count = 0
        for _ in psnawp_fixture.me().game_entitlements(limit=limit, page_size=5):
            count += 1
        assert limit == count


@pytest.mark.vcr
def test_client__game_entitlements(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        count = 0
        entitlement_iter = psnawp_fixture.me().game_entitlements(page_size=5)
        for game_entitlement in entitlement_iter:
            count += 1
        assert entitlement_iter._total_item_count == count


@pytest.mark.vcr
def test_client__repr_and_str(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        client = psnawp_fixture.me()
        repr(client)
        str(client)


@pytest.mark.vcr
def test_client__get_region(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        client = psnawp_fixture.me()
        assert isinstance(client.get_region(), Country)
