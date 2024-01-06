from typing import Any
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm.session import Session

from server.core.database import get_sessionlocal
from server.core.game import GameManager
from server.core.user_session import UserSessionManager
from server.core.websocket_manager import WebSocketManager
from server.models.orm.game import GameState
from server.utils import jwt_util
from server.utils import tabulation_util


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def validate_token(token: str = Depends(oauth2_scheme)) -> dict[str, Any]:
    """
    Basic validation for tokens
    """
    try:
        return jwt_util.decode_token(token)
    except:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={'WWW-Authenticate': 'Bearer'}
        )


def get_database():
    db = get_sessionlocal()()
    try:
        yield db
    finally:
        db.close()


CACHE: dict[Any, Any] = {}


def get_cache():
    yield CACHE


def update_cache(db: Session = Depends(get_database)):
    # TODO: define cache interface, support redis, etc
    try:
        yield CACHE
    finally:
        # try and update the cache here but do not throw exception if we fail
        tabulation_util.update_cache(CACHE, db)


GAMES: dict[UUID, GameState] = {}


def session_auth(token_data: dict[str, Any] = Depends(validate_token)) -> UUID:
    """
    Validate a session token. If the session token is valid, we proceed
    by returning the user id referred to in the session token. If the
    session token is not valid, we reject the request.
    """
    return UUID(token_data["user_id"])


_user_session_manager = None

def get_user_session_manager() -> UserSessionManager:
    global _user_session_manager
    if _user_session_manager is None:
        _user_session_manager = UserSessionManager()
    return _user_session_manager


_game_manager = None

def get_game_manager() -> GameManager:
    global _game_manager
    if _game_manager is None:
        _game_manager = GameManager()
    return _game_manager


_websocket_manager = None

def get_websocket_manager(game_manager: GameManager = Depends(get_game_manager)) -> WebSocketManager:
    global _websocket_manager
    if _websocket_manager is None:
        _websocket_manager = WebSocketManager(game_manager)
    return _websocket_manager
