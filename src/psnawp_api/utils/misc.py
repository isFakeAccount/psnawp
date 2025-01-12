from __future__ import annotations

import base64
import binascii
from datetime import datetime
from typing import Optional, cast

from pycountry import countries
from pycountry.db import Country


def iso_format_to_datetime(iso_format: Optional[str]) -> Optional[datetime]:
    return datetime.fromisoformat(iso_format.replace("Z", "+00:00")) if iso_format is not None else None


def extract_region_from_npid(npid: str) -> Optional[Country]:
    try:
        decoded_npid = base64.b64decode(npid).decode("utf-8")
    except (binascii.Error, UnicodeDecodeError):
        return None

    # Assuming a valid decoded npid format (e.g. VaultTec-Co@b7.us), extract the region (e.g. "US")
    if "@" in decoded_npid and "." in decoded_npid:
        region_candidate = decoded_npid.split(".")[-1]
        if len(region_candidate) == 2 and region_candidate.isalpha():
            return cast(Country, countries.get(alpha_2=region_candidate))

    return None
