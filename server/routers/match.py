from sqlalchemy.orm.session import Session
from fastapi import APIRouter, Depends

from server.core.dependencies import update_cache, get_database
from server.models.dto.match import MatchResult as MatchResultDto
from server.models.dto.response import Response
from server.models.orm.match import Match
from server.models.orm.player import Player

router = APIRouter()


@router.post("/match", response_model=Response)
def record_match_result(result: MatchResultDto, db: Session = Depends(get_database), cache = Depends(update_cache)):
    """
    Record the result of a match
    """
    winner = db.query(Player).filter(Player.name == result.winner).one()
    loser = db.query(Player).filter(Player.name == result.loser).one()
    match = Match(winner_id=winner.uuid, loser_id=loser.uuid)
    db.add(match)
    db.commit()
    return Response.success()


@router.match("/undo", response_model=Response)
def undo_last_match_results(db: Session = Depends(get_database), cache=Depends(update_cache)):
    """
    Undo the last match
    """
    match = db.query(Match).order_by(Match.created_at).first()
    db.delete(match)
    db.commit()
    return Response.success()
