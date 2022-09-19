from __future__ import annotations

import logging
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
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"
    )
    log_stream.setFormatter(formatter)
    logger.addHandler(log_stream)
    logger.propagate = False
    return logger
