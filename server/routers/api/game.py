import asyncio
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, WebSocket
from fastapi.exceptions import HTTPException
from starlette.websockets import WebSocketDisconnect

from server.core.dependencies import get_websocket_manager, get_game_manager, session_auth, validate_token
from server.core.game import GameManager
from server.core.websocket_manager import Role, WebSocketManager
from server.models.dto.game import (
    CreateGameRequest,
    CreateGameResponse,
    ListGamesResponse,
    GetGameByCodeRequest,
    GetGameByCodeResponse,
)
from server.models.orm.game import GameState

router = APIRouter()

logger = logging.getLogger(__name__)

@router.websocket("/wstest")
async def websocket_test(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")


@router.get("/game", response_model=ListGamesResponse)
async def get_games(_: UUID = Depends(session_auth), game_manager: GameManager = Depends(get_game_manager)):
    return ListGamesResponse(game_ids=game_manager.get_all_game_ids())


@router.post("/game", response_model=CreateGameResponse)
async def create_game(
    _: CreateGameRequest,
    player_id: UUID = Depends(session_auth),
    game_manager: GameManager = Depends(get_game_manager)
):
    game = game_manager.create_game(player_id)
    return CreateGameResponse(code=200, game_id=game.uuid)


@router.get("/game/code", response_model=GetGameByCodeResponse)
async def get_game_code(
    code: str,
    _: UUID = Depends(session_auth),
    game_manager: GameManager = Depends(get_game_manager)
):
    game = game_manager.get_game_by_code(code)
    if game is None:
        raise ValueError(f"No game found with code {code}")
    return GetGameByCodeResponse(game_id=game.uuid)


@router.get("/game/{uuid}", response_model=GameState)
async def get_game(
    uuid: str,
    _: UUID = Depends(session_auth),
    game_manager: GameManager = Depends(get_game_manager)
):
    game_id = UUID(uuid)
    game = game_manager.get_game_by_id(game_id)
    if game is None:
        raise ValueError("Game with provided id does not exist")
    return game


@router.websocket("/game/{uuid}/ws")
async def websocket_game(
    websocket: WebSocket,
    uuid: str,
    token: str,
    websocket_manager: WebSocketManager = Depends(get_websocket_manager),
):
    """
    The WebSocket game flow is as follows

    When a new client connects, it presents its session id.
    
    The session id can be used to look up a matching user id. Depending on the user id,
    a different set of permissions will be applied to the user. After the SessionInit
    message is issued by the client, the server will respond with a SessionAcknowledge
    message. This SessionAcknowledge message should inform the client which permissions
    it can expect to receive from the server.

    If the user id matches the host, host permissions are enabled.
    If the user id matches one of the player ids, they get the matching permissions.
    If the user id does not match any of the ids, they will only receive
    game state updates.

    Commands are asynchronous and do not come with any explicit response feedback.
    """
    game_id = UUID(uuid)
    try:
        user_id = session_auth(validate_token(token))
    except HTTPException:
        logger.error("Invalid token")
        await websocket.close(code=1008, reason="Invalid token")
        return

    role = await websocket_manager.handshake(websocket, game_id, user_id)
    if role == Role.FORBIDDEN:
        logger.warning(f"Failed to establish role for connected player {user_id} and game {game_id}")
        await websocket.close(code=1008)

    await websocket.accept()

    # after handshake success, register subscription
    sub_id = websocket_manager.subscribe(websocket, game_id)
    # start listening for commands
    try:
        while True:
            try:
                data = await websocket.receive_json()
                await websocket_manager.dispatch(data, role)
            except WebSocketDisconnect:
                logger.debug(f"WebSocket disconnect for user {str(user_id)}")
                break
            except Exception as exc:
                print(f"{type(exc)} - {repr(exc)}")
                await asyncio.sleep(1.0)
                logger.warning(f"Failed to read message from remote???")
    finally:
        websocket_manager.unsubscribe(sub_id, game_id)
