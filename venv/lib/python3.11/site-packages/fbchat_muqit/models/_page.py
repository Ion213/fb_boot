from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
from . import _plan
from ._thread import ThreadType, Thread


@dataclass(eq=False)
class Page(Thread):
    """Represents a Facebook page. Inherits `Thread`."""

    #: The page's custom URL
    url: Optional[str] = None
    #: The name of the page's location city
    city: Optional[str] = None
    #: Amount of likes the page has
    likes: Optional[int] = None
    #: Some extra information about the page
    sub_title: Optional[str] = None
    #: The page's category
    category: Optional[List] = None

    def __post_init__(self):
        self.type = ThreadType.PAGE

    @classmethod
    def _from_graphql(cls, data)-> Page:
        if data.get("profile_picture") is None:
            data["profile_picture"] = {}
        if data.get("city") is None:
            data["city"] = {}
        plan = None
        if data.get("event_reminders") and data["event_reminders"].get("nodes"):
            plan = _plan.Plan._from_graphql(data["event_reminders"]["nodes"][0])

        return cls(
            data["id"],
            url=data.get("url"),
            city=data.get("city").get("name"),
            category=data.get("category_type"),
            photo=data["profile_picture"].get("uri"),
            name=data.get("name"),
            message_count=data.get("messages_count"),
            plan=plan,
        )
