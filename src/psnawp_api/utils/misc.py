"""Miscellaneous functions that are used throughout the psnawp module."""

from __future__ import annotations

import base64
import binascii
from datetime import datetime
from typing import TYPE_CHECKING, cast

from pycountry import countries

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
