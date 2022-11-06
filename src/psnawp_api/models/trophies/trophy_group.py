from enum import Enum

import attr

from psnawp_api.models.trophies.trophy_set import TrophySet


class PlatformType(Enum):
    PS_VITA = "PS Vita"
    PS3 = "PS3"
    PS4 = "PS4"
    PS5 = "PS5"


@attr.define(slots=True)
class TrophyGroup:
    trophy_group_id: str
    "ID for the trophy group (all titles have default, additional groups are 001 incrementing)"
    trophy_group_name: str
    "Trophy group name"
    trophy_group_detail: str
    "Trophy group description PS3, PS4 and PS Vita titles only"
    trophy_group_icon_url: str
    "URL of the icon for the trophy group"
    defined_trophies: TrophySet
    "Number of trophies for the trophy group by type"


@attr.define(slots=True)
class TrophyGroupSummary:
    trophy_set_version: str
    "The current version of the trophy set"
    trophy_title_name: str
    "Title name"
    trophy_title_detail: str
    "Title description"
    trophy_title_icon_url: str
    "URL of the icon for the trophy title"
    trophy_title_platform: PlatformType
    "The platform this title belongs to"
    defined_trophies: TrophySet
    "Total number of trophies for the title by type"
    trophy_groups: list[TrophyGroup]
    "Individual object for each trophy group returned"
