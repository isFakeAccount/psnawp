import attr


@attr.s(slots=True)
class TrophySet:
    bronze: int = attr.ib(default=0)
    silver: int = attr.ib(default=0)
    gold: int = attr.ib(default=0)
    platinum: int = attr.ib(default=0)
