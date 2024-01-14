"""
Client commands
"""
from fastapi import Depends

from server.constants import CommandType
from server.core.command import CommandRouter
from server.core.dependencies import get_game_manager, get_websocket_manager
from server.core.game import GameManager
from server.core.websocket_manager import WebSocketManager
from server.models.dto.command import Command, DefaultCommand, KickPlayer, PlayPiece

router = CommandRouter()


@router.command(CommandType.get_game_state)
def get_game_state_handler(
    command: DefaultCommand,
    websocket_manager: WebSocketManager = Depends(get_websocket_manager)
):
    # TODO: this currently makes every client fetch an update, which is unnecessary.
    # I think it's OK though because this endpoint is primarily for testing and will
    # most likely not see usage in production.
    websocket_manager.update_subscribers(command.body.game_id)


@router.command(CommandType.become_player)
def spectator_promote_to_player(
    command: DefaultCommand,
    game_manager: GameManager = Depends(get_game_manager),
):
    """
    Attempt to have a spectator player promote themselves to a player. There will
    always either be 0 or 1 open slots. If there are 0 open player slots, this
    request will be rejected. If there is 1 open player slot, this request will
    be accepted.
    """
    with game_manager.game_context(command.body.game_id) as game:
        game.try_promote_player(command.body.user_id)


@router.command(CommandType.play_white_piece)
def play_white_piece(
    command: PlayPiece,
    game_manager: GameManager = Depends(get_game_manager),
):
    with game_manager.game_context(command.body.game_id) as game:
        if command.body.current_turn != game.turn_number:
            raise ValueError("Piece does not match current turn")
        game.play_white(command.body.pos_x, command.body.pos_y, command.body.pos_z)


@router.command(CommandType.play_black_piece)
def play_black_piece(
    command: PlayPiece,
    game_manager: GameManager = Depends(get_game_manager),
):
    with game_manager.game_context(command.body.game_id) as game:
        if command.body.current_turn != game.turn_number:
            raise ValueError("Piece does not match current turn")
        game.play_black(command.body.pos_x, command.body.pos_y, command.body.pos_z)


@router.command(CommandType.leave)
def player_leave(command: DefaultCommand, game_manager: GameManager = Depends(get_game_manager)):
    with game_manager.game_context(command.body.game_id) as game:
        game.player_leave_game(command.body.user_id)


@router.command(CommandType.forfeit)
def player_forfeit(command: DefaultCommand, game_manager: GameManager = Depends(get_game_manager)):
    with game_manager.game_context(command.body.game_id) as game:
        game.player_forfeit_game(command.body.user_id)


@router.command(CommandType.start_game)
def start_game(command: DefaultCommand, game_manager: GameManager = Depends(get_game_manager)):
    with game_manager.game_context(command.body.game_id) as game:
        game.start()


@router.command(CommandType.kick_player)
def kick_player(command: KickPlayer, game_manager: GameManager = Depends(get_game_manager)):
    with game_manager.game_context(command.body.game_id) as game:
        game.remove_player(command.body.kicked_player_id)


@router.command(CommandType.close_game)
def close_game(command: DefaultCommand, game_manager: GameManager = Depends(get_game_manager)):
    with game_manager.game_context(command.body.game_id) as game:
        game.close()


@router.command(CommandType.switch_places)
def switch_places(command: DefaultCommand, game_manager: GameManager = Depends(get_game_manager)):
    with game_manager.game_context(command.body.game_id) as game:
        game.switch_places()
