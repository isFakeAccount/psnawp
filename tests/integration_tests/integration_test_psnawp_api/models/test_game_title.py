import inspect

import pytest

from psnawp_api import PSNAWP
from psnawp_api.core import PSNAWPNotFoundError
from psnawp_api.core.psnawp_exceptions import PSNAWPIllegalArgumentError
from psnawp_api.models.trophies import PlatformType
from tests.integration_tests.integration_test_psnawp_api import my_vcr


@pytest.mark.vcr
def test_game_title__np_communication_id(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        game_title = psnawp_fixture.game_title(title_id="PPSA03420_00", platform=PlatformType.PS5)
        assert game_title.np_communication_id == "NPWR21647_00"


@pytest.mark.vcr
def test_game_title__ps3(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        game_title = psnawp_fixture.game_title(title_id="NPEB00571_00", platform=PlatformType.PS3, np_communication_id="NPWR00845_00")
        assert game_title.np_communication_id == "NPWR00845_00"


@pytest.mark.vcr
def test_game_title__ps3_illegal_arguments(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        with pytest.raises(expected_exception=PSNAWPIllegalArgumentError):
            psnawp_fixture.game_title(title_id="NPEB00571_00", platform=PlatformType.PS3)


@pytest.mark.vcr
def test_game_title__wrong_title_id(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        with pytest.raises(PSNAWPNotFoundError):
            psnawp_fixture.game_title(title_id="SSSA01325_00", platform=PlatformType.PS5)


@pytest.mark.vcr
def test_game_title__get_title_details(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        game_title = psnawp_fixture.game_title(title_id="PPSA03420_00", platform=PlatformType.PS5)
        title_details = game_title.get_details()
        assert title_details[0].get("name") == "Grand Theft Auto V (PlayStation®5)"


@pytest.mark.vcr
def test_game_title__get_localized_title_details(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        game_title = psnawp_fixture.game_title(title_id="PPSA02432_00", platform=PlatformType.PS5)
        title_details = game_title.get_details(country="FR", language="fr")
        assert title_details[0].get("name") == "Crash Bandicoot™ 4: It’s About Time"
        assert title_details[0].get("country") == "FR"
        assert title_details[0].get("language") == "fr"


@pytest.mark.vcr
def test_game_title__trophies(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        game_title = psnawp_fixture.game_title(title_id="PPSA03420_00", platform=PlatformType.PS5)
        actual_count = 0
        trophy_iter = game_title.trophies(trophy_group_id="all")
        for trophy in trophy_iter:
            actual_count += 1
            assert trophy.trophy_id is not None
            assert trophy.trophy_hidden is not None
            assert trophy.trophy_type is not None
            assert trophy.trophy_name is not None
            assert trophy.trophy_detail is not None
            assert trophy.trophy_icon_url is not None
            assert trophy.trophy_group_id is not None
        assert actual_count == len(trophy_iter)


@pytest.mark.vcr
def test_game_title__trophy_groups_summary(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        game_title = psnawp_fixture.game_title(title_id="PPSA01325_00", platform=PlatformType.PS5)
        trophy_groups_summary = game_title.trophy_groups_summary()
        assert trophy_groups_summary.trophy_set_version is not None
        assert trophy_groups_summary.trophy_title_name is not None
        assert trophy_groups_summary.trophy_title_icon_url is not None
        assert trophy_groups_summary.trophy_title_platform is not None
        assert trophy_groups_summary.defined_trophies is not None

        for trophy_group_summary in trophy_groups_summary.trophy_groups:
            assert trophy_group_summary.trophy_group_id is not None
            assert trophy_group_summary.trophy_group_name is not None
            assert trophy_group_summary.trophy_group_icon_url is not None
            assert trophy_group_summary.defined_trophies is not None


@pytest.mark.vcr
def test_game_title__trophies_game_not_owned_by_user(psnawp_fixture: PSNAWP) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        with pytest.raises(PSNAWPNotFoundError):
            psnawp_fixture.game_title(title_id="PPSA03420_00", account_id="me", platform=PlatformType.PS5)


@pytest.mark.vcr
def test_game_title__trophy_groups_summary_game_not_owned_by_user(
    psnawp_fixture: PSNAWP,
) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        with pytest.raises(PSNAWPNotFoundError):
            psnawp_fixture.game_title(title_id="PPSA01325_00", account_id="me", platform=PlatformType.PS5)


@pytest.mark.vcr
def test_game_title__trophies_invalid_np_communication_id(
    psnawp_fixture: PSNAWP,
) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        with pytest.raises(PSNAWPNotFoundError):
            game_title = psnawp_fixture.game_title(title_id="PPSA03420_00", account_id="me", np_communication_id="SSSA01325_00", platform=PlatformType.PS5)
            for trophy in game_title.trophies(trophy_group_id="all"):
                print(trophy)


@pytest.mark.vcr
def test_game_title__trophy_groups_summary_invalid_np_communication_id(
    psnawp_fixture: PSNAWP,
) -> None:
    with my_vcr.use_cassette(f"{inspect.currentframe().f_code.co_name}.json"):
        with pytest.raises(PSNAWPNotFoundError):
            game_title = psnawp_fixture.game_title(title_id="PPSA01325_00", account_id="me", np_communication_id="SSSA01325_00", platform=PlatformType.PS5)
            trophy_groups_summary = game_title.trophy_groups_summary()
            for trophy_group_summary in trophy_groups_summary.trophy_groups:
                print(trophy_group_summary)
