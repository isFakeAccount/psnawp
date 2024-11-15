from __future__ import annotations

import base64
import binascii
import re
from datetime import datetime
from typing import Optional

DECODED_NPID_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"


def iso_format_to_datetime(iso_format: Optional[str]) -> Optional[datetime]:
    return datetime.fromisoformat(iso_format.replace("Z", "+00:00")) if iso_format is not None else None


def extract_region_from_npid(npid: Optional[str]) -> Optional[str]:
    if not npid:
        return None

    try:
        decoded_npid = base64.b64decode(npid).decode("utf-8")
    except (binascii.Error, UnicodeDecodeError):
        return None

    if re.match(DECODED_NPID_PATTERN, decoded_npid):
        match = re.search(r"\.([a-zA-Z]{2})$", decoded_npid)
        # Parse the region from the decoded npId (e.g. User@a1.us -> "US")
        return match.group(1).upper() if match and match.group(1) else None

    return None
