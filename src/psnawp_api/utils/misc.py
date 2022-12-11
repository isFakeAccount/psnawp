from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Optional
import re

from psnawp_api import psnawp


def create_logger(module_name: str) -> logging.Logger:
    """Creates logger and returns an instance of logging object.

    :param module_name: Logger name that will appear in text.
    :type module_name: str

    :returns: Logging Object.
    :rtype: logging.Logger

    """
    # Setting up the root logger
    logger = logging.getLogger(module_name)
    logger.setLevel(logging.DEBUG)

    log_stream = logging.StreamHandler()
    log_stream.setLevel(psnawp.logging_level)
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s")
    log_stream.setFormatter(formatter)
    logger.addHandler(log_stream)
    logger.propagate = False
    return logger


def iso_format_to_datetime(iso_format: Optional[str]) -> Optional[datetime]:
    return datetime.fromisoformat(iso_format.replace("Z", "+00:00")) if iso_format is not None else None


def play_duration_to_timedelta(play_duration: Optional[str]) -> timedelta:
    """Provides a timedelta object for the play duration PSN sends

    :param play_duration: String from API
    :type play_duration: Optional[str]

    :returns: String parsed into a timedelta object
    :rtype: timedelta

    .. note::

        PSN API returns the duration in this format: PT243H18M48S. The maximum time Unit is Hours, it does not extend to Days or Months.

    """
    hours = 0
    minutes = 0
    seconds = 0

    if play_duration is not None:
        # Strip everything and split into list of numbers separated by alphabets
        digits_list = [int(s) for s in re.findall(r"\d+", play_duration)]
        length = len(digits_list)

        # Example: PT243H18M48S = 243 hours, 18 minutes, 48 seconds
        if length == 3:
            hours = digits_list[0]
            minutes = digits_list[1]
            seconds = digits_list[2]
        # Example: PT21M18S = 21 minutes, 18 seconds
        elif length == 2:
            minutes = digits_list[0]
            seconds = digits_list[1]
        # Example: PT39S = 39 seconds
        elif length == 1:
            seconds = digits_list[0]

    # If for some reason the string is malformed or None, timedelta will return 0
    return timedelta(hours=hours, minutes=minutes, seconds=seconds)
