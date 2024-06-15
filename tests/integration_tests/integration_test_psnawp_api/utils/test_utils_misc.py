from datetime import timedelta

from psnawp_api.models.title_stats import play_duration_to_timedelta


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
