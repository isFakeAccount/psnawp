"""Contains datatypes for group messaging endpoint."""

from __future__ import annotations

from enum import Enum
from typing import TypedDict


class MessageType(Enum):
    """Enumeration of possible message types in a PSN group."""

    AUDIO = 1011
    IMAGE = 3
    STICKER = 1013
    TEXT = 1
    VIDEO = 210
    UNKNOWN = -1

    @classmethod
    def _missing_(cls, value: object) -> MessageType:
        _ = value
        return cls.UNKNOWN


class MessageResponse(TypedDict):
    """Represents the response metadata for a sent message."""

    messageUid: str
    createdTimestamp: str


class ResourceResponse(TypedDict):
    """Represents the response metadata for a sent resource."""

    resourceId: str


class NotificationSetting(TypedDict):
    """User-specific notification settings for a group."""

    isMute: bool


class GroupName(TypedDict):
    """Details about the group's name and its status."""

    status: int
    value: str


class GroupIcon(TypedDict):
    """Status information related to the group's icon."""

    status: int


class Member(TypedDict):
    """Represents a member of a group, including their ID and role."""

    accountId: str
    onlineId: str
    role: str


class Sender(TypedDict):
    """Details about the sender of a message."""

    accountId: str
    onlineId: str


class LatestMessage(TypedDict):
    """Metadata and content for the most recent message in a group."""

    alternativeMessageType: int
    body: str
    createdTimestamp: str
    messageType: MessageType
    messageUid: str
    sender: Sender


class MainThread(TypedDict):
    """Information about the primary message thread in a group."""

    latestMessage: LatestMessage
    modifiedTimestamp: str
    readMessageUid: str
    threadId: str


class GroupDetails(TypedDict):
    """Complete metadata describing a PSN group and its current state."""

    existsNewArrival: bool
    groupIcon: GroupIcon
    groupId: str
    groupName: GroupName
    groupType: int
    isFavorite: bool
    joinedTimestamp: str
    mainThread: MainThread
    members: list[Member]
    modifiedTimestamp: str
    notificationSetting: NotificationSetting
