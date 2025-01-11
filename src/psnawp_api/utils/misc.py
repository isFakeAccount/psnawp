from __future__ import annotations

import base64
import binascii
from datetime import datetime
from typing import Optional

from pycountry import countries as pycounties


def iso_format_to_datetime(iso_format: Optional[str]) -> Optional[datetime]:
    return datetime.fromisoformat(iso_format.replace("Z", "+00:00")) if iso_format is not None else None


def extract_region_from_npid(npid: Optional[str], return_full_ctry_name: Optional[bool] = True) -> Optional[str]:
    if not npid:
        return None

    try:
        decoded_npid = base64.b64decode(npid).decode("utf-8")
    except (binascii.Error, UnicodeDecodeError):
        return None

    # Assuming a valid decoded npid format (e.g. VaultTec-Co@b7.us), extract the region (e.g. "US")
    if "@" in decoded_npid and "." in decoded_npid:
        region_candidate = decoded_npid.split(".")[-1]
        if len(region_candidate) == 2 and region_candidate.isalpha():
            return get_country_name_from_code(region_candidate) if return_full_ctry_name else region_candidate.upper()

    return None


def get_country_name_from_code(code: str) -> Optional[str]:
    country = pycounties.get(alpha_2=code)
    return country.name if country else None
