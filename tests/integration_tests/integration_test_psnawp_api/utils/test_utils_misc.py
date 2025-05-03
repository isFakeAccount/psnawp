from datetime import timedelta

import pytest
from pycountry import countries

from psnawp_api.core.psnawp_exceptions import PSNAWPInvalidTokenError
from psnawp_api.models.title_stats import play_duration_to_timedelta
from psnawp_api.utils.misc import extract_region_from_npid, legacy_title_icon_url, parse_npsso_token


def test_play_duration_to_timedelta_valid_inputs():
    hh_mm_ss_raw = "PT90H23M22S"
    assert play_duration_to_timedelta(hh_mm_ss_raw) == timedelta(hours=90, minutes=23, seconds=22)
    hh_ss_raw = "PT18H22S"
    assert play_duration_to_timedelta(hh_ss_raw) == timedelta(hours=18, seconds=22)
    mm_ss_raw = "PT22M38S"
    assert play_duration_to_timedelta(mm_ss_raw) == timedelta(minutes=22, seconds=38)
    ss_raw = "PT38S"
    assert play_duration_to_timedelta(ss_raw) == timedelta(seconds=38)
    ss_raw = "PT18H20S"
    assert play_duration_to_timedelta(ss_raw) == timedelta(hours=18, seconds=20)


def test_play_duration_to_timedelta_invalid_inputs():
    assert play_duration_to_timedelta(None) == timedelta(hours=0, minutes=0, seconds=0)
    assert play_duration_to_timedelta("PTH23M22S23MS") == timedelta(hours=0, minutes=0, seconds=0)


def test_extract_region_from_npid() -> None:
    assert extract_region_from_npid("") is None
    assert extract_region_from_npid("VaultTec-Co@b7.us") is None
    assert extract_region_from_npid("VmF1bHRUZWMtQ29AYjcudXM=") == countries.get(alpha_2="US")
    assert extract_region_from_npid("ZGF2MWRfMTIzQGIxLmNh") == countries.get(alpha_2="CA")
    assert extract_region_from_npid("Z2lua283NjVAYTUucGw=") == countries.get(alpha_2="PL")
    assert extract_region_from_npid("THVjYXNEaWFzQ0BkMi5icg==") == countries.get(alpha_2="BR")


def test_extract_npsso_input() -> None:
    assert parse_npsso_token('{"npsso":"token"}') == "token"  # Valid npsso json
    assert parse_npsso_token("token") == "token"  # User supplied just the npsso token


def test_extract_npsso_invalid_json() -> None:
    with pytest.raises(PSNAWPInvalidTokenError) as ex_info:
        parse_npsso_token('"npsso":"token"}')  # Invalid npsso json -> Raise exception


def test_extract_npsso_invalid_json_key() -> None:
    with pytest.raises(PSNAWPInvalidTokenError) as ex_info:
        parse_npsso_token('{"missing_key":"token"}')  # valid json but missing npsso key -> Raise exception

def test_legacy_title_icon_url() -> None:
    assert legacy_title_icon_url("NPEB00571_00") == "https://tmdb.np.dl.playstation.net/tmdb/NPEB00571_00_1EB03AE017B54F8797D8D96BBBA3F5DACFEF3584/ICON0.PNG"
