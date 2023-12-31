from pydantic import BaseModel


class MatchResult(BaseModel):
    winner: str
    loser: str
