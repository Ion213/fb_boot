from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional


@dataclass(eq=False)
class Poll:
    """Represents a poll."""

    #: Title of the poll
    title: str 
    #: List of :class:`PollOption`, can be fetched with :func:`fbchat.Client.fetchPollOptions`
    options: List["PollOption"]
    #: Options count
    options_count: Optional[int] = None
    #: ID of the poll
    uid: Optional[int] = None

    @classmethod
    def _from_graphql(cls, data)-> Poll:
        return cls(
            uid=int(data["id"]),
            title=data.get("title") if data.get("title") else data.get("text"),
            options=[PollOption._from_graphql(m) for m in data.get("options")],
            options_count=data.get("total_count"),
        )


@dataclass(eq=False)
class PollOption:
    """Represents a poll option."""

    #: Text of the poll option
    text: str
    #: Whether vote when creating or client voted
    vote: Optional[bool] = False
    #: ID of the users who voted for this poll option
    voters: Optional[List] = None
    #: Votes count
    votes_count: Optional[int] = None
    #: ID of the poll option
    uid: Optional[int] = None

    @classmethod
    def _from_graphql(cls, data)-> PollOption:
        if data.get("viewer_has_voted") is None:
            vote = None
        elif isinstance(data["viewer_has_voted"], bool):
            vote = data["viewer_has_voted"]
        else:
            vote: Optional[bool] = data["viewer_has_voted"] == "true"
        return cls(
            uid=int(data["id"]),
            text=data.get("text"),
            vote=vote,
            voters=(
                [m.get("node").get("id") for m in data.get("voters").get("edges")]
                if isinstance(data.get("voters"), dict)
                else data.get("voters")
            ),
            votes_count=(
                data.get("voters").get("count")
                if isinstance(data.get("voters"), dict)
                else data.get("total_count")
            ),
        )
