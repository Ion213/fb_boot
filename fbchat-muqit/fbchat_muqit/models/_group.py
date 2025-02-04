from __future__ import annotations
from dataclasses import dataclass, field
from . import _plan
from ._thread import ThreadType, Thread
from typing import Any, Dict, Set, Optional


@dataclass(eq=False)
class Group(Thread):
    """Represents a Facebook group. Inherits `Thread`."""

    #: Set of the group thread's participant user IDs
    participants: Set[str] = field(default_factory=set)
    #: A dictionary, containing user nicknames mapped to their IDs
    nicknames: Optional[Dict[str, str]] = field(default_factory=dict)
    #: A :class:`ThreadColor`. The groups's message color
    color: Optional[str] = None
    #: The groups's default emoji
    emoji: Optional[str] = None
    #: Set containing user IDs of thread admins
    admins: Optional[Set[str]] = field(default_factory=set)
    #: True if users need approval to join
    approval_mode: Optional[bool] = None
    #: Set containing user IDs requesting to join
    approval_requests: Optional[Set[str]] = field(default_factory=set)
    #: Link for joining group
    join_link: Optional[str] = None

    def __post_init__(self):
        self.type = ThreadType.GROUP
        self.participants = set() if self.participants is None else self.participants
        self.nicknames = {} if self.nicknames is None else self.nicknames
        self.admins = set() if self.admins is None else self.admins
        self.approval_requests = set() if self.approval_requests is None else self.approval_requests



    @classmethod
    def _from_graphql(cls, data: Dict[str, Any])-> Group:
        if data.get("image") is None:
            data["image"] = {}
        c_info = cls._parse_customization_info(data)
        last_message_timestamp = None
        if "last_message" in data:
            last_message_timestamp = data["last_message"]["nodes"][0][
                "timestamp_precise"
            ]
        plan = None
        if data.get("event_reminders") and data["event_reminders"].get("nodes"):
            plan = _plan.Plan._from_graphql(data["event_reminders"]["nodes"][0])

        return cls(
            data["thread_key"]["thread_fbid"],
            participants=set(
                [
                    node["messaging_actor"]["id"]
                    for node in data["all_participants"]["nodes"]
                ]
            ),
            nicknames=c_info.get("nicknames"),
            color=c_info.get("color"),
            emoji=c_info.get("emoji"),
            admins=set([node.get("id") for node in data.get("thread_admins")]), #type: ignore
            approval_mode=bool(data.get("approval_mode"))
            if data.get("approval_mode") is not None
            else None,
            approval_requests=set(
                node["requester"]["id"]
                for node in data["group_approval_queue"]["nodes"]
            )
            if data.get("group_approval_queue")
            else None,
            join_link=data["joinable_mode"].get("link"),
            photo=data["image"].get("uri"),
            name=data["name"],
            message_count=data.get("messages_count"),
            last_message_timestamp=last_message_timestamp,
            plan=plan,
        )

    def _to_send_data(self)-> Dict[str, str]:
        return {"thread_fbid": self.uid}


@dataclass(eq=False)
class Room(Group):
    """Deprecated. Use `Group` instead."""
    #: True is room is not discoverable
    privacy_mode: Optional[bool] = None

    def __post_init__(self):
        self.type = ThreadType.ROOM
