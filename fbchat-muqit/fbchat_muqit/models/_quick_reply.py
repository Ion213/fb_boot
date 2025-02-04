from dataclasses import dataclass, field
from typing import Any, Dict, Optional

@dataclass(eq=False)
class QuickReply:
    """Represents a quick reply."""

    #: Payload of the quick reply
    payload: Optional[Dict] = field(default=None)
    #: External payload for responses
    external_payload: Optional[Dict] = field(default=None, init=False)
    #: Additional data
    data: Any = field(default=None)
    #: Whether it's a response for a quick reply
    is_response: bool = field(default=False)


@dataclass(eq=False, init=False)
class QuickReplyText(QuickReply):
    """Represents a text quick reply."""

    #: Title of the quick reply
    title: Optional[str] = field(default=None)
    #: URL of the quick reply image (optional)
    image_url: Optional[str] = field(default=None)
    #: Type of the quick reply
    _type = "text"

    def __init__(self, title=None, image_url=None, **kwargs):
        super(QuickReplyText, self).__init__(**kwargs)
        self.title = title
        self.image_url = image_url


@dataclass(eq=False, init=False)
class QuickReplyLocation(QuickReply):
    """Represents a location quick reply (Doesn't work on mobile)."""

    #: Type of the quick reply
    _type = "location"

    def __init__(self, **kwargs):
        super(QuickReplyLocation, self).__init__(**kwargs)
        self.is_response = False


@dataclass(eq=False, init=False)
class QuickReplyPhoneNumber(QuickReply):
    """Represents a phone number quick reply (Doesn't work on mobile)."""

    #: URL of the quick reply image (optional)
    image_url: Optional[str] = field(default=None)
    #: Type of the quick reply
    _type = "user_phone_number"

    def __init__(self, image_url=None, **kwargs):
        super(QuickReplyPhoneNumber, self).__init__(**kwargs)
        self.image_url = image_url


@dataclass(eq=False, init=False)
class QuickReplyEmail(QuickReply):
    """Represents an email quick reply (Doesn't work on mobile)."""

    #: URL of the quick reply image (optional)
    image_url: Optional[str] = field(default=None)
    #: Type of the quick reply
    _type = "user_email"

    def __init__(self, image_url=None, **kwargs):
        super(QuickReplyEmail, self).__init__(**kwargs)
        self.image_url = image_url


def graphql_to_quick_reply(q, is_response: bool = False):
    data = dict()
    _type = q.get("content_type").lower()
    if q.get("payload"):
        data["payload"] = q["payload"]
    if q.get("data"):
        data["data"] = q["data"]
    if q.get("image_url") and _type is not QuickReplyLocation._type:
        data["image_url"] = q["image_url"]
    data["is_response"] = is_response

    if _type == QuickReplyText._type:
        if q.get("title") is not None:
            data["title"] = q["title"]
        return QuickReplyText(**data)
    elif _type == QuickReplyLocation._type:
        return QuickReplyLocation(**data)
    elif _type == QuickReplyPhoneNumber._type:
        return QuickReplyPhoneNumber(**data)
    elif _type == QuickReplyEmail._type:
        return QuickReplyEmail(**data)
    
