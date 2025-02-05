from __future__ import annotations
import json
from typing import Dict, Optional
from ._core import CustomEnum
from dataclasses import dataclass, field

class GuestStatus(CustomEnum):
    INVITED = 1
    GOING = 2
    DECLINED = 3


@dataclass(eq=False)
class Plan:
    """Represents a plan."""

    #: ID of the plan
    uid: Optional[str] = field(default=None, init=False)
    #: Plan time (timestamp), only precise down to the minute
    time: Optional[int]
    #: Plan title
    title: str
    #: Plan location name
    location: Optional[str] = None
    #: Plan location ID
    location_id: Optional[str] = None
    #: ID of the plan creator
    author_id: Optional[str] = field(default=None, init=False)
    #: Dictionary of `User` IDs mapped to their `GuestStatus`
    guests: Optional[Dict[str, GuestStatus]] = field(default=None, init=False)

    def __post_init__(self):
        if self.time:
            self.time = int(self.time)
        self.location = self.location or ""
        self.location_id = self.location_id or ""

    @property
    def going(self):
        """List of the `User` IDs who will take part in the plan."""
        return [
            id_
            for id_, status in (self.guests or {}).items()
            if status is GuestStatus.GOING
        ]

    @property
    def declined(self):
        """List of the `User` IDs who won't take part in the plan."""
        return [
            id_
            for id_, status in (self.guests or {}).items()
            if status is GuestStatus.DECLINED
        ]

    @property
    def invited(self):
        """List of the `User` IDs who are invited to the plan."""
        return [
            id_
            for id_, status in (self.guests or {}).items()
            if status is GuestStatus.INVITED
        ]

    @classmethod
    def _from_pull(cls, data)->Plan:
        rtn = cls(
            time=data.get("event_time"),
            title=data.get("event_title"),
            location=data.get("event_location_name"),
            location_id=data.get("event_location_id"),
        )
        rtn.uid = data.get("event_id")
        rtn.author_id = data.get("event_creator_id")
        rtn.guests = {
            x["node"]["id"]: GuestStatus[x["guest_list_state"]]
            for x in json.loads(data["guest_state_list"])
        }
        return rtn

    @classmethod
    def _from_fetch(cls, data)-> Plan:
        rtn = cls(
            time=data.get("event_time"),
            title=data.get("title"),
            location=data.get("location_name"),
            location_id=str(data["location_id"]) if data.get("location_id") else None,
        )
        rtn.uid = data.get("oid")
        rtn.author_id = data.get("creator_id")
        rtn.guests = {id_: GuestStatus[s] for id_, s in data["event_members"].items()}
        return rtn

    @classmethod
    def _from_graphql(cls, data)-> Plan:
        rtn = cls(
            time=data.get("time"),
            title=data.get("event_title"),
            location=data.get("location_name"),
        )
        rtn.uid = data.get("id")
        rtn.author_id = data["lightweight_event_creator"].get("id")
        rtn.guests = {
            x["node"]["id"]: GuestStatus[x["guest_list_state"]]
            for x in data["event_reminder_members"]["edges"]
        }
        return rtn
