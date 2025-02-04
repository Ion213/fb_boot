from __future__ import annotations

from typing import Dict, Optional
from dataclasses import dataclass, field

from ._plan import Plan
from ._core import CustomEnum


class ThreadType(CustomEnum):
    """Used to specify what type of Facebook thread is being used.

    See :ref:`intro_threads` for more info.
    """

    USER = 1
    GROUP = 2
    ROOM = 2
    PAGE = 3

    def _to_class(self):
        """Convert this enum value to the corresponding class."""
        from . import _user, _group, _page

        return {
            ThreadType.USER: _user.User,
            ThreadType.GROUP: _group.Group,
            ThreadType.ROOM: _group.Room,
            ThreadType.PAGE: _page.Page,
        }[self]


class ThreadLocation(CustomEnum):
    """Used to specify where a thread is located (inbox, pending, archived, other)."""

    INBOX = "INBOX"
    PENDING = "PENDING"
    ARCHIVED = "ARCHIVED"
    OTHER = "OTHER"


class ThreadColor(CustomEnum):
    """Used to specify a thread colors."""

    MESSENGER_BLUE = "#0084ff"
    VIKING = "#44bec7"
    GOLDEN_POPPY = "#ffc300"
    RADICAL_RED = "#fa3c4c"
    SHOCKING = "#d696bb"
    PICTON_BLUE = "#6699cc"
    FREE_SPEECH_GREEN = "#13cf13"
    PUMPKIN = "#ff7e29"
    LIGHT_CORAL = "#e68585"
    MEDIUM_SLATE_BLUE = "#7646ff"
    DEEP_SKY_BLUE = "#20cef5"
    FERN = "#67b868"
    CAMEO = "#d4a88c"
    BRILLIANT_ROSE = "#ff5ca1"
    BILOBA_FLOWER = "#a695c7"
    TICKLE_ME_PINK = "#ff7ca8"
    MALACHITE = "#1adb5b"
    RUBY = "#f01d6a"
    DARK_TANGERINE = "#ff9c19"
    BRIGHT_TURQUOISE = "#0edcde"

    @classmethod
    def _from_graphql(cls, color)-> Optional[ThreadColor]:
        if color is None:
            return None
        if not color:
            return cls.MESSENGER_BLUE
        color = color[2:]  # Strip the alpha value
        value = "#{}".format(color.lower())
        return cls._extend_if_invalid(value)


@dataclass(eq=False, init=False)
class Thread:
    """Represents a Facebook thread."""

    #: The unique identifier of the thread. Can be used a ``thread_id``. See :ref:`intro_threads` for more info
    uid: str = field()
    #: Specifies the type of thread. Can be used a ``thread_type``. See :ref:`intro_threads` for more info
    type: Optional[ThreadType] = None
    #: A URL to the thread's picture
    photo: Optional[str] = None
    #: The name of the thread
    name: Optional[str] = None
    #: Timestamp of last message
    last_message_timestamp: Optional[int] = None
    #: Number of messages in the thread
    message_count: Optional[int] = None
    #: Set :class:`Plan`
    plan: Optional[Plan] = None
    

    def __post_init__(self):
        self.uid = str(self.uid)

    @staticmethod
    def _parse_customization_info(data)-> Dict:
        if data is None or data.get("customization_info") is None:
            return {}
        info = data["customization_info"]

        rtn = {
            "emoji": info.get("emoji"),
            "color": ThreadColor._from_graphql(info.get("outgoing_bubble_color")),
        }
        if (
            data.get("thread_type") == "GROUP"
            or data.get("is_group_thread")
            or data.get("thread_key", {}).get("thread_fbid")
        ):
            rtn["nicknames"] = {}
            for k in info.get("participant_customizations", []):
                rtn["nicknames"][k["participant_id"]] = k.get("nickname")
        elif info.get("participant_customizations"):
            uid = data.get("thread_key", {}).get("other_user_id") or data.get("id")
            pc = info["participant_customizations"]
            if len(pc) > 0:
                if pc[0].get("participant_id") == uid:
                    rtn["nickname"] = pc[0].get("nickname")
                else:
                    rtn["own_nickname"] = pc[0].get("nickname")
            if len(pc) > 1:
                if pc[1].get("participant_id") == uid:
                    rtn["nickname"] = pc[1].get("nickname")
                else:
                    rtn["own_nickname"] = pc[1].get("nickname")
        return rtn

    def _to_send_data(self)-> Dict[str, str]:
        # TODO: Only implement this in subclasses
        return {"other_user_fbid": self.uid}
