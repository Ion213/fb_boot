from __future__ import annotations
from dataclasses import dataclass, field 
from typing import Any, Optional
from ._attachment import Attachment


@dataclass(eq=False)
class FileAttachment(Attachment):
    """Represents a file that has been sent as a Facebook attachment."""

    #: URL where you can download the file
    url: Optional[str] = field(default=None)
    #: Size of the file in bytes
    size: Any = field(default=None)
    #: Name of the file
    name: Optional[str] = field(default=None)
    #: Whether Facebook determines that this file may be harmful
    is_malicious: Optional[bool] = field(default=None)
    # Put here for backwards compatibility, so that the init argument order is preserved
    uid: Optional[int] = field(default=None)

    @classmethod
    def _from_graphql(cls, data)->FileAttachment:
        return cls(
            url=data.get("url"),
            name=data.get("filename"),
            is_malicious=data.get("is_malicious"),
            uid=data.get("message_file_fbid"),
        )


@dataclass(eq=False)
class AudioAttachment(Attachment):
    """Represents an audio file that has been sent as a Facebook attachment."""

    #: Name of the file
    filename: Optional[str] = field(default=None)
    #: URL of the audio file
    url: Optional[str] = field(default=None)
    #: Duration of the audio clip in milliseconds
    duration: Optional[int] = field(default=None)
    #: Audio type
    audio_type: Any = field(default=None)

    # Put here for backwards compatibility, so that the init argument order is preserved
    uid: Optional[int] = field(default=None)

    @classmethod
    def _from_graphql(cls, data)-> AudioAttachment:
        return cls(
            filename=data.get("filename"),
            url=data.get("playable_url"),
            duration=data.get("playable_duration_in_ms"),
            audio_type=data.get("audio_type"),
        )


@dataclass(eq=False, init=False)
class ImageAttachment(Attachment):
    """Represents an image that has been sent as a Facebook attachment.

    To retrieve the full image URL, use: `Client.fetchImageUrl`, and pass it the id of
    the image attachment.
    """

    #: The extension of the original image (e.g. ``png``)
    original_extension: Optional[str] = field(default=None)
    #: Width of original image
    width: Optional[int] = field(default=None)
    #: Height of original image
    height: Optional[int] = field(default=None)

    #: Whether the image is animated
    is_animated: Optional[bool] = field(default=None)

    #: URL to a thumbnail of the image
    thumbnail_url: Optional[str] = field(default=None)

    #: URL to a medium preview of the image
    preview_url: Optional[str] = field(default=None)
    #: Width of the medium preview image
    preview_width: Optional[int] = field(default=None)
    #: Height of the medium preview image
    preview_height: Optional[int] = field(default=None)

    #: URL to a large preview of the image
    large_preview_url: Optional[int] = field(default=None)
    #: Width of the large preview image
    large_preview_width: Optional[int] = field(default=None)
    #: Height of the large preview image
    large_preview_height: Optional[int] = field(default=None)

    #: URL to an animated preview of the image (e.g. for GIFs)
    animated_preview_url: Optional[str] = field(default=None)
    #: Width of the animated preview image
    animated_preview_width: Optional[int] = field(default=None)
    #: Height of the animated preview image
    animated_preview_height: Optional[int] = field(default=None)

    def __init__(
        self,
        original_extension=None,
        width=None,
        height=None,
        is_animated=None,
        thumbnail_url=None,
        preview=None,
        large_preview=None,
        animated_preview=None,
        **kwargs
    ):
        super(ImageAttachment, self).__init__(**kwargs)
        self.original_extension = original_extension
        if width is not None:
            width = int(width)
        self.width = width
        if height is not None:
            height = int(height)
        self.height = height
        self.is_animated = is_animated
        self.thumbnail_url = thumbnail_url

        if preview is None:
            preview = {}
        self.preview_url = preview.get("uri")
        self.preview_width = preview.get("width")
        self.preview_height = preview.get("height")

        if large_preview is None:
            large_preview = {}
        self.large_preview_url = large_preview.get("uri")
        self.large_preview_width = large_preview.get("width")
        self.large_preview_height = large_preview.get("height")

        if animated_preview is None:
            animated_preview = {}
        self.animated_preview_url = animated_preview.get("uri")
        self.animated_preview_width = animated_preview.get("width")
        self.animated_preview_height = animated_preview.get("height")

        def __post_init__(self):
            if self.width and not isinstance(self.width, int):
                self.width = int(self.width)
            if self.height and not isinstance(self.height, int):
                self.height = int(self.height)
            if self.preview_width and not isinstance(self.preview_width, int):
                self.preview_width = int(self.preview_width)
            if self.preview_height and not isinstance(self.preview_height, int):
                self.preview_height = int(self.preview_height)
            if self.large_preview_width and not isinstance(self.large_preview_width, int):
                self.large_preview_width = int(self.large_preview_width)
            if self.large_preview_height and not isinstance(self.large_preview_height, int):
                self.large_preview_height = int(self.large_preview_height)
            if self.animated_preview_width and not isinstance(self.animated_preview_width, int):
                self.animated_preview_width = int(self.animated_preview_width)
            if self.animated_preview_height and not isinstance(self.animated_preview_height, int):
                self.animated_preview_height = int(self.animated_preview_height)

    

    @classmethod
    def _from_graphql(cls, data)-> ImageAttachment:
        return cls(
            original_extension=data.get("original_extension")
            or (data["filename"].split("-")[0] if data.get("filename") else None),
            width=data.get("original_dimensions", {}).get("width"),
            height=data.get("original_dimensions", {}).get("height"),
            is_animated=data["__typename"] == "MessageAnimatedImage",
            thumbnail_url=data.get("thumbnail", {}).get("uri"),
            preview=data.get("preview") or data.get("preview_image"),
            large_preview=data.get("large_preview"),
            animated_preview=data.get("animated_image"),
            uid=data.get("legacy_attachment_id"),
        )

    @classmethod
    def _from_list(cls, data)-> ImageAttachment:
        data = data["node"]
        return cls(
            width=data["original_dimensions"].get("x"),
            height=data["original_dimensions"].get("y"),
            thumbnail_url=data["image"].get("uri"),
            large_preview=data["image2"],
            preview=data["image1"],
            uid=data["legacy_attachment_id"],
        )


@dataclass(eq=False, init=False)
class VideoAttachment(Attachment):
    """Represents a video that has been sent as a Facebook attachment."""

    #: Size of the original video in bytes
    size: Optional[int] = field(default=None)
    #: Width of original video
    width: Optional[int] = field(default=None)
    #: Height of original video
    height: Optional[int] = field(default=None)
    #: Length of video in milliseconds
    duration: Optional[int] = field(default=None)
    #: URL to very compressed preview video
    preview_url: Optional[int] = field(default=None)
    #: URL to a small preview image of the video
    small_image_url: Optional[str] = field(default=None)
    #: Width of the small preview image
    small_image_width: Optional[int] = field(default=None)
    #: Height of the small preview image
    small_image_height: Optional[int] = field(default=None)
    #: URL to a medium preview image of the video
    medium_image_url: Optional[str] = field(default=None)
    #: Width of the medium preview image
    medium_image_width: Optional[int] = field(default=None)
    #: Height of the medium preview image
    medium_image_height: Optional[int] = field(default=None)

    #: URL to a large preview image of the video
    large_image_url: Optional[str] = field(default=None)
    #: Width of the large preview image
    large_image_width: Optional[int] = field(default=None)
    #: Height of the large preview image
    large_image_height: Optional[int] = field(default=None)

    def __init__(
        self,
        size=None,
        width=None,
        height=None,
        duration=None,
        preview_url=None,
        small_image=None,
        medium_image=None,
        large_image=None,
        **kwargs
    ):
        super(VideoAttachment, self).__init__(**kwargs)
        self.size = size
        self.width = width
        self.height = height
        self.duration = duration
        self.preview_url = preview_url

        if small_image is None:
            small_image = {}
        self.small_image_url = small_image.get("uri")
        self.small_image_width = small_image.get("width")
        self.small_image_height = small_image.get("height")

        if medium_image is None:
            medium_image = {}
        self.medium_image_url = medium_image.get("uri")
        self.medium_image_width = medium_image.get("width")
        self.medium_image_height = medium_image.get("height")

        if large_image is None:
            large_image = {}
        self.large_image_url = large_image.get("uri")
        self.large_image_width = large_image.get("width")
        self.large_image_height = large_image.get("height")

    @classmethod
    def _from_graphql(cls, data)-> VideoAttachment:
        return cls(
            width=data.get("original_dimensions", {}).get("width"),
            height=data.get("original_dimensions", {}).get("height"),
            duration=data.get("playable_duration_in_ms"),
            preview_url=data.get("playable_url"),
            small_image=data.get("chat_image"),
            medium_image=data.get("inbox_image"),
            large_image=data.get("large_image"),
            uid=data.get("legacy_attachment_id"),
        )

    @classmethod
    def _from_subattachment(cls, data)-> VideoAttachment:
        media = data["media"]
        return cls(
            duration=media.get("playable_duration_in_ms"),
            preview_url=media.get("playable_url"),
            medium_image=media.get("image"),
            uid=data["target"].get("video_id"),
        )

    @classmethod
    def _from_list(cls, data)-> VideoAttachment:
        data = data["node"]
        return cls(
            width=data["original_dimensions"].get("x"),
            height=data["original_dimensions"].get("y"),
            small_image=data["image"],
            medium_image=data["image1"],
            large_image=data["image2"],
            uid=data["legacy_attachment_id"],
        )


def graphql_to_attachment(data):
    _type = data["__typename"]
    if _type in ["MessageImage", "MessageAnimatedImage"]:
        return ImageAttachment._from_graphql(data)
    elif _type == "MessageVideo":
        return VideoAttachment._from_graphql(data)
    elif _type == "MessageAudio":
        return AudioAttachment._from_graphql(data)
    elif _type == "MessageFile":
        return FileAttachment._from_graphql(data)

    return Attachment(uid=data.get("legacy_attachment_id"))


def graphql_to_subattachment(data):
    target = data.get("target")
    type_ = target.get("__typename") if target else None

    if type_ == "Video":
        return VideoAttachment._from_subattachment(data)

    return None
