import logging
from aenum import Enum, extend_enum

log = logging.getLogger("client")


class CustomEnum(Enum): #type: ignore
    """Used internally by ``fbchat`` to support enumerations"""

    def __repr__(self):
        # For documentation:
        return f"{type(self).__name__}.{self.name}"

    @classmethod
    def _extend_if_invalid(cls, value):
        try:
            return cls(value)
        except ValueError:
            log.warning(
                "Failed parsing {.__name__}({!r}). Extending enum.".format(cls, value)
            )
            extend_enum(cls, f"UNKNOWN_{value}".upper(), value)
            return cls(value)
