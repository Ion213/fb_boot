from __future__ import annotations

from ._attachment import Attachment
from dataclasses import dataclass
from typing import Optional

@dataclass(eq=False, init=False)
class Sticker(Attachment):
    """
    Represents a Facebook sticker that has been sent to a thread as an attachment.
    """

    #: The sticker-pack's ID
    pack: Optional[str] = None
    #: Whether the sticker is animated
    is_animated: bool = False

    # If the sticker is animated, the following should be present
    #: URL to a medium spritemap
    medium_sprite_image: Optional[str] = None
    #: URL to a large spritemap
    large_sprite_image: Optional[str] = None
    #: The amount of frames present in the spritemap pr. row
    frames_per_row: Optional[int] = None
    #: The amount of frames present in the spritemap pr. column
    frames_per_col: Optional[int] = None
    #: The frame rate the spritemap is intended to be played in
    frame_rate: Optional[float] = None

    #: URL to the sticker's image
    url: Optional[str] = None
    #: Width of the sticker
    width: Optional[int] = None
    #: Height of the sticker
    height: Optional[int] = None
    #: The sticker's label/name
    label: Optional[str] = None

    def __init__(self, uid: Optional[int] = None):
        super(Sticker, self).__init__(uid=uid)

    @classmethod
    def _from_graphql(cls, data)-> Sticker:
        if not data:
            return None
        self = cls(uid=data["id"])
        if data.get("pack"):
            self.pack = data["pack"].get("id")
        if data.get("sprite_image"):
            self.is_animated = True
            self.medium_sprite_image = data["sprite_image"].get("uri")
            self.large_sprite_image = data["sprite_image_2x"].get("uri")
            self.frames_per_row = data.get("frames_per_row")
            self.frames_per_col = data.get("frames_per_column")
            self.frame_rate = data.get("frame_rate")
        self.url = data.get("url")
        self.width = data.get("width")
        self.height = data.get("height")
        if data.get("label"):
            self.label = data["label"]
        return self
