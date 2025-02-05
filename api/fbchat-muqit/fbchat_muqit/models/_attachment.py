from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List
from .. import _util


@dataclass(eq=False)
class Attachment:
    """Represents a Facebook attachment."""
    #: The attachment ID
    uid: Optional[int] = field(default=None)

@dataclass(eq=False)
class UnsentMessage(Attachment):
    """Represents an unsent message attachment."""


@dataclass(eq=False)
class ShareAttachment(Attachment):
    """Represents a shared item (e.g. URL) attachment."""

    #: ID of the author of the shared post
    author: Optional[str] = field(default=None)
    #: Target URL
    url: Optional[str] = field(default=None)
    #: Original URL if Facebook redirects the URL
    original_url: Optional[str] = field(default=None)
    #: Title of the attachment
    title: Optional[str] = field(default=None)
    #: Description of the attachment
    description: Optional[str] = field(default=None)
    #: Name of the source
    source: Optional[str] = field(default=None)
    #: URL of the attachment image
    image_url: Optional[str] = field(default=None)
    #: URL of the original image if Facebook uses ``safe_image``
    original_image_url: Optional[str] = field(default=None)
    #: Width of the image
    image_width: Optional[int] = field(default=None)
    #: Height of the image
    image_height: Optional[int] = field(default=None)
    #: List of additional attachments
    attachments: List = field(default_factory=list)

    # Put here for backwards compatibility, so that the init argument order is preservd
    uid: Optional[int] = field(default=None)

    def __post_init__(self):
        if self.attachments is None:
            self.attachments = []



    @classmethod
    def _from_graphql(cls, data)-> ShareAttachment:
        from . import _file

        url = data.get("url")
        rtn = cls(
            uid=data.get("deduplication_key"),
            author=data["target"]["actors"][0]["id"]
            if data["target"].get("actors")
            else None,
            url=url,
            original_url=_util.get_url_parameter(url, "u")
            if "/l.php?u=" in url
            else url,
            title=data["title_with_entities"].get("text"),
            description=data["description"].get("text")
            if data.get("description")
            else None,
            source=data["source"].get("text") if data.get("source") else None,
            attachments=[
                _file.graphql_to_subattachment(attachment)
                for attachment in data.get("subattachments")
            ],
        )
        media = data.get("media")
        if media and media.get("image"):
            image = media["image"]
            rtn.image_url = image.get("uri")
            rtn.original_image_url = (
                _util.get_url_parameter(rtn.image_url, "url")
                if "/safe_image.php" in rtn.image_url #type: ignore
                else rtn.image_url
            )
            rtn.image_width = image.get("width")
            rtn.image_height = image.get("height")
        return rtn
