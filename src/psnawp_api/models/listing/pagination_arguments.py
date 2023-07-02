from __future__ import annotations

from typing import Optional

from attrs import define


@define(kw_only=True)
class PaginationArguments:
    total_limit: Optional[int]
    page_size: int
    offset: int
    limit: int = 0

    def __attrs_post_init__(self) -> None:
        if self.total_limit is not None:
            self.limit = min(self.total_limit, self.page_size)
        else:
            self.limit = self.page_size

    def get_params_dict(self) -> dict[str, int]:
        return {"limit": self.limit, "offset": self.offset}
