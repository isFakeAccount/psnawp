from enum import Enum

import attr


class TrophyType(Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


@attr.s(slots=True)
class Trophy:
    trophy_id: int
    "Unique ID for this trophy"
    trophy_hidden: bool
    "True if this is a secret trophy (Only for client)"
    trophy_type: TrophyType
    "Type of the trophy"
    trophy_name: str
    "Name of trophy"
    trophy_detail: str
    "Description of the trophy"
    trophy_icon_url: str
    "URL for the graphic associated with the trophy"
    trophy_group_id: str
    "ID of the trophy group this trophy belongs to"
    trophy_Progress_value: int
    "Trophy progress towards it being unlocked (PS5 Only)"
    trophy_reward_name: str
    "Name of the reward earning the trophy grants (PS5 Only)"
    trophy_reward_img_url: str
    "URL for the graphic associated with the reward (PS5 Only)"
