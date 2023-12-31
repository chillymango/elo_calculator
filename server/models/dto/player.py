from uuid import UUID
from pydantic import BaseModel, ConfigDict


class AddPlayer(BaseModel):
    name: str


class Player(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID
    name: str


class ListPlayersResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    players: list[Player]
