from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional
from ._core import CustomEnum
from . import _plan
from ._thread import Thread, ThreadType


GENDERS = {
    # For standard requests
    0: "unknown",
    1: "female_singular",
    2: "male_singular",
    3: "female_singular_guess",
    4: "male_singular_guess",
    5: "mixed",
    6: "neuter_singular",
    7: "unknown_singular",
    8: "female_plural",
    9: "male_plural",
    10: "neuter_plural",
    11: "unknown_plural",
    # For graphql requests
    "UNKNOWN": "unknown",
    "FEMALE": "female_singular",
    "MALE": "male_singular",
    # '': 'female_singular_guess',
    # '': 'male_singular_guess',
    # '': 'mixed',
    "NEUTER": "neuter_singular",
    # '': 'unknown_singular',
    # '': 'female_plural',
    # '': 'male_plural',
    # '': 'neuter_plural',
    # '': 'unknown_plural',
}


class TypingStatus(CustomEnum):
    """Used to specify whether the user is typing or has stopped typing."""

    STOPPED = 0
    TYPING = 1


@dataclass(eq=False)
class User(Thread):
    """Represents a Facebook user. Inherits `Thread`."""

    #: The profile URL
    url: Optional[str] = None
    #: The users first name
    first_name: Optional[str] = None
    #: The users last name
    last_name: Optional[str] = None
    #: Whether the user and the client are friends
    is_friend: Optional[bool] = None
    #: The user's gender
    gender: Optional[str] = None
    #: From 0 to 1. How close the client is to the user
    affinity: Optional[int] = None
    #: The user's nickname
    nickname: Optional[str] = None
    #: The clients nickname, as seen by the user
    own_nickname: Optional[str] = None
    #: A :class:`ThreadColor`. The message color
    color: Any = None
    #: The default emoji
    emoji: Any = None


    def __post_init__(self):
        self.type = ThreadType.USER
    @classmethod
    def _from_graphql(cls, data)-> User:
        if data.get("profile_picture") is None:
            data["profile_picture"] = {}
        c_info = cls._parse_customization_info(data)
        plan = None
        if data.get("event_reminders") and data["event_reminders"].get("nodes"):
            plan = _plan.Plan._from_graphql(data["event_reminders"]["nodes"][0])

        return cls(
            data["id"],
            url=data.get("url"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            is_friend=data.get("is_viewer_friend"),
            gender=GENDERS.get(data.get("gender")),
            affinity=data.get("affinity"),
            nickname=c_info.get("nickname"),
            color=c_info.get("color"),
            emoji=c_info.get("emoji"),
            own_nickname=c_info.get("own_nickname"),
            photo=data["profile_picture"].get("uri"),
            name=data.get("name"),
            message_count=data.get("messages_count"),
            plan=plan,
        )

    @classmethod
    def _from_thread_fetch(cls, data)-> User:
        if data.get("big_image_src") is None:
            data["big_image_src"] = {}
        c_info = cls._parse_customization_info(data)
        participants = [
            node["messaging_actor"] for node in data["all_participants"]["nodes"]
        ]
        user = next(
            p for p in participants if p["id"] == data["thread_key"]["other_user_id"]
        )
        last_message_timestamp = None
        if "last_message" in data:
            last_message_timestamp = data["last_message"]["nodes"][0][
                "timestamp_precise"
            ]

        first_name = user.get("short_name")
        if first_name is None:
            last_name = None
        else:
            last_name = user.get("name").split(first_name, 1).pop().strip()

        plan = None
        if data.get("event_reminders") and data["event_reminders"].get("nodes"):
            plan = _plan.Plan._from_graphql(data["event_reminders"]["nodes"][0])

        return cls(
            user["id"],
            url=user.get("url"),
            name=user.get("name"),
            first_name=first_name,
            last_name=last_name,
            is_friend=user.get("is_viewer_friend"),
            gender=GENDERS.get(user.get("gender")),
            affinity=user.get("affinity"),
            nickname=c_info.get("nickname"),
            color=c_info.get("color"),
            emoji=c_info.get("emoji"),
            own_nickname=c_info.get("own_nickname"),
            photo=user["big_image_src"].get("uri"),
            message_count=data.get("messages_count"),
            last_message_timestamp=last_message_timestamp,
            plan=plan,
        )

    @classmethod
    def _from_all_fetch(cls, data)-> User:
        return cls(
            data["id"],
            first_name=data.get("firstName"),
            url=data.get("uri"),
            photo=data.get("thumbSrc"),
            name=data.get("name"),
            is_friend=data.get("is_friend"),
            gender=GENDERS.get(data.get("gender")),
        )


@dataclass(eq=False)
class ActiveStatus:
    """Represents Facebook Active Status"""
    #: Whether the user is active now
    active: bool
    #: Timestamp when the user was last active
    last_active: Optional[int] = None
    #: Whether the user is playing Messenger game now
    in_game: Optional[bool] = None

    @classmethod
    def _from_orca_presence(cls, data)-> ActiveStatus:
        # TODO: Handle `c` and `vc` keys (Probably some binary data)
        return cls(active=data["p"] in [2, 3], last_active=data.get("l"), in_game=None)
