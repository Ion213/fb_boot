from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from ._attachment import Attachment
from .. import _util


@dataclass(eq=False)
class LocationAttachment(Attachment):
    """Represents a user location.

    Latitude and longitude OR address is provided by Facebook.
    """

    #: Latitude of the location
    latitude: Optional[float] = None
    #: Longitude of the location
    longitude: Optional[float] = None
    #: URL of image showing the map of the location
    image_url: Optional[str] = field(default=None, init=False)
    #: Width of the image
    image_width: Optional[int] = field(default=None, init=False)
    #: Height of the image
    image_height: Optional[int] = field(default=None, init=False)
    #: URL to Bing maps with the location
    url: Optional[str] = field(default=None, init=False)
    # Address of the location
    address: Optional[str] = field(default=None)

    # Put here for backwards compatibility, so that the init argument order is preserved
    uid: Optional[int] = None

    @classmethod
    def _from_graphql(cls, data)-> LocationAttachment:
        url = data.get("url")
        address = _util.get_url_parameter(_util.get_url_parameter(url, "u"), "where1")
        try:
            latitude, longitude = [float(x) for x in address.split(", ")]
            address = None
        except ValueError:
            latitude, longitude = None, None
        rtn = cls(
            uid=int(data["deduplication_key"]),
            latitude=latitude,
            longitude=longitude,
            address=address,
        )
        media = data.get("media")
        if media and media.get("image"):
            image = media["image"]
            rtn.image_url = image.get("uri")
            rtn.image_width = image.get("width")
            rtn.image_height = image.get("height")
        rtn.url = url
        return rtn


@dataclass(eq=False, init=False)
class LiveLocationAttachment(LocationAttachment):
    """Represents a live user location."""

    #: Name of the location
    name: Optional[str] = None
    #: Timestamp when live location expires
    expiration_time: Optional[int] = None
    #: True if live location is expired
    is_expired: Optional[bool] = None

    def __init__(self, name=None, expiration_time=None, is_expired=None, **kwargs):
        super(LiveLocationAttachment, self).__init__(**kwargs)
        self.expiration_time = expiration_time
        self.is_expired = is_expired

    @classmethod
    def _from_pull(cls, data)-> LiveLocationAttachment:
        return cls(
            uid=data["id"],
            latitude=data["coordinate"]["latitude"] / (10 ** 8)
            if not data.get("stopReason")
            else None,
            longitude=data["coordinate"]["longitude"] / (10 ** 8)
            if not data.get("stopReason")
            else None,
            name=data.get("locationTitle"),
            expiration_time=data["expirationTime"],
            is_expired=bool(data.get("stopReason")),
        )

    @classmethod
    def _from_graphql(cls, data)-> LiveLocationAttachment:
        target = data["target"]
        rtn = cls(
            uid=int(target["live_location_id"]),
            latitude=target["coordinate"]["latitude"]
            if target.get("coordinate")
            else None,
            longitude=target["coordinate"]["longitude"]
            if target.get("coordinate")
            else None,
            name=data["title_with_entities"]["text"],
            expiration_time=target.get("expiration_time"),
            is_expired=target.get("is_expired"),
        )
        media = data.get("media")
        if media and media.get("image"):
            image = media["image"]
            rtn.image_url = image.get("uri")
            rtn.image_width = image.get("width")
            rtn.image_height = image.get("height")
        rtn.url = data.get("url")
        return rtn
