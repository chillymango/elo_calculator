from datetime import datetime

from pydantic import BaseModel

from server.models.orm.match import Match

class PlayerRank(BaseModel):
    name: str
    elo: float
    win: int
    loss: int


class MatchRecord(BaseModel):
    winner: str
    loser: str
    date: str


class Summary(BaseModel):
    last_hydrated: str
    ordered_players: list[PlayerRank]
    match_history: list[MatchRecord]

    @classmethod
    def create_from_cache(
        cls,
        elo: dict[str, float],
        wins: dict[str, int],
        loss: dict[str, int],
        matches: list[Match]
    ):
        ordered_players = [PlayerRank(name=p, elo=score, win=wins.get(p, 0), loss=loss.get(p, 0)) for p, score in elo.items()]
        ordered_players.sort(key=lambda x: x.elo, reverse=True)
        match_history = [MatchRecord(winner=m.winner.name, loser=m.loser.name, date=m.created_at.isoformat()) for m in matches]
        match_history.sort(key=lambda x: x.date, reverse=True)
        return cls(
            last_hydrated=datetime.utcnow().isoformat(),
            ordered_players=ordered_players,
            match_history=match_history,
        )


class SummaryResponseDto(BaseModel):
    response_json_str: str
