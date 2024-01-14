from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm.session import Session

from server.core.dependencies import get_database, get_cache
from server.models.dto.player import AddPlayer, ListPlayersResponse, Player as PlayerDto
from server.models.dto.response import Response
from server.models.orm.player import Player
from server.utils import tabulation_util

router = APIRouter()


@router.post("/add_player", response_model=Response)
def add_player(player: AddPlayer, db: Session = Depends(get_database), cache = Depends(get_cache)):
    exists = db.query(Player).filter(Player.name == player.name).first()
    if exists:
        raise HTTPException(
            status_code=500,
            detail="Player already exists"
        )
    db.add(Player(name=player.name))
    db.commit()
    tabulation_util.update_cache(cache, db)
    return Response.success()


@router.get("/players", response_model=ListPlayersResponse)
def list_players(db: Session = Depends(get_database)):
    return ListPlayersResponse(players=[PlayerDto(uuid=p.uuid, name=p.name) for p in db.query(Player).all()])
