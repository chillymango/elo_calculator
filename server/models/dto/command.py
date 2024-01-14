from datetime import datetime
from typing import Generic, TypeVar
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from server.constants import CommandType

T = TypeVar('T', bound='Body')


class Command(BaseModel, Generic[T]):
    """
    Base command model.

    The command type should indicate where it is routed to.
    """
    type: CommandType
    body: T | None = None


class Body(BaseModel):
    version: int = 1
    timestamp: datetime
    event_id: UUID = Field(default_factory=uuid4)
    game_id: UUID
    user_id: UUID


class DefaultCommand(Command[Body]):
    """
    Commands that do not require any additional fields can just be cast to this type when
    deserializing.
    """


class PlayPieceBody(Body):
    current_turn: int
    pos_x: int
    pos_y: int
    pos_z: int


class PlayPiece(Command[PlayPieceBody]): ...


class KickPlayerBody(Body):
    kicked_player_id: UUID


class KickPlayer(Command[KickPlayerBody]): ...
