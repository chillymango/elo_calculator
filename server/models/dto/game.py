from uuid import UUID
from pydantic import BaseModel, Field


class CreateGameRequest(BaseModel):
    # if this is provided, this game will be accessible through
    # a login code.
    game_code: str | None = None


class CreateGameResponse(BaseModel):
    code: int
    game_id: UUID


class ListGamesResponse(BaseModel):
    game_ids: list[UUID] = Field(default_factory=list)


class GetGameByCodeRequest(BaseModel):
    game_code: str


class GetGameByCodeResponse(BaseModel):
    game_id: UUID
