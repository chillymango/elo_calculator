# Expose a few different APIs in this router
#
# 1. Create a game.
# 2. Join a game as some color (???)
#    This should probably be a websocket???
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, WebSocket

from server.core.dependencies import get_websocket_manager, get_game_manager, session_auth
from server.core.game import GameManager
from server.core.websocket_manager import Role, WebSocketManager
from server.models.dto.game import CreateGameRequest, CreateGameResponse, ListGamesResponse

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
    request: CreateGameRequest,
    _: UUID = Depends(session_auth),
    game_manager: GameManager = Depends(get_game_manager)
):
    game = game_manager.create_game()
    return CreateGameResponse(code=200, game_id=game.uuid)


@router.websocket("/game/{uuid}/ws")
async def websocket_game(
    websocket: WebSocket,
    uuid: str,
    user_id: UUID = Depends(session_auth),
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

    User commands should be broken into request / response pairs.
    """
    game_id = UUID(uuid)
    role = await websocket_manager.handshake(game_id, user_id)

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
            except:
                logger.warning(f"Failed to read message from remote???")
    finally:
        websocket_manager.unsubscribe(sub_id, game_id)
