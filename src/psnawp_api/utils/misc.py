from __future__ import annotations

from datetime import datetime
from typing import Optional


def iso_format_to_datetime(iso_format: Optional[str]) -> Optional[datetime]:
    return datetime.fromisoformat(iso_format.replace("Z", "+00:00")) if iso_format is not None else None
