"""Miscellaneous functions that are used throughout the psnawp module."""

from __future__ import annotations

import base64
import binascii
import json
import os
import re
from datetime import datetime
from pathlib import Path
from tempfile import gettempdir
from typing import TYPE_CHECKING, cast

from pycountry import countries

from psnawp_api.core.psnawp_exceptions import PSNAWPInvalidTokenError

if TYPE_CHECKING:
    from pycountry.db import Country

ISO_3166_1_ALPHA_2_LEN = 2


def iso_format_to_datetime(iso_format: str | None) -> datetime | None:
    """Converts an ISO 8601 formatted string to a :py:class:`~datetime.datetime` object.

    :param iso_format: The ISO 8601 formatted string (e.g., "2025-02-26T12:00:00Z").

    :returns: The corresponding :py:class:`~datetime.datetime` object, or ``None`` if input is ``None``.

    """
    return datetime.fromisoformat(iso_format.replace("Z", "+00:00")) if iso_format is not None else None


def extract_region_from_npid(npid: str) -> Country | None:
    """Extracts the region code from a base64-encoded NPID string and converts it to a full country.

    The function decodes the NPID, extracts the last two characters representing the ISO 3166-1 alpha-2 region code, and
    uses the `pycountry` library to map it to a full country.

    :param npid: The base64-encoded NPID string, which is decoded to extract the region code.

    :returns: The region as a :py:class:`~pycountry.db.Country` object, or ``None`` if extraction fails or region is
        invalid.

    This function assumes a valid NPID format (e.g., `"VaultTec-Co@b7.us"`). It splits the string to get the region code
    (e.g., "US"), which is then matched to the full country using the `pycountry` library.

    """
    try:
        decoded_npid = base64.b64decode(npid).decode("utf-8")
    except (binascii.Error, UnicodeDecodeError):
        return None

    # Assuming a valid decoded npid format (e.g. VaultTec-Co@b7.us), extract the region (e.g. "US")
    if "@" in decoded_npid and "." in decoded_npid:
        region_candidate = decoded_npid.split(".")[-1]
        if len(region_candidate) == ISO_3166_1_ALPHA_2_LEN and region_candidate.isalpha():
            return cast("Country", countries.get(alpha_2=region_candidate))

    return None


def parse_npsso_token(npsso_input: str) -> str:
    """Accept string from the user that may contain either a valid npsso token or a json string with key "npsso" and value of the npsso token.

    This function either succeeds at extracting the npsso token from the provided input (meaning a valid npsso json
    string was provided) or it returns the original input.

    :param npsso_input: User provided input for npsso token.

    :returns: Extracted npsso token from user input or the original string.

    :raises PSNAWPInvalidTokenError: If malformed npsso JSON is supplied

    """
    pattern = r"\{|\}"
    if re.search(pattern, npsso_input):
        try:
            npsso_dict: dict[str, str] = json.loads(npsso_input)
            return npsso_dict["npsso"]
        except json.JSONDecodeError as exp:
            raise PSNAWPInvalidTokenError("Malformed JSON passed as input.") from exp
        except KeyError as exp:
            raise PSNAWPInvalidTokenError('Input JSON is missing the "npsso" key') from exp
    return npsso_input


def get_temp_db_path(filename: str = "psnawp_limiter.sqlite") -> Path:
    """Create a writable temporary directory and database file.

    :param filename: Name of the SQLite database file.

    :returns: Path to the writable SQLite database.

    """
    temp_dir = Path(gettempdir()) / f"psnawp-{os.getpid()}"
    temp_dir.mkdir(parents=True, exist_ok=True)

    db_path = temp_dir / filename
    db_path.touch(exist_ok=True)

    return db_path
