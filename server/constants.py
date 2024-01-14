from enum import auto
from uuid import UUID
from strenum import StrEnum


TEST_GAME_ID = UUID('230ebb4c-3eb1-4cb3-96c2-bce8f7654580')


class CommandType(StrEnum):
    # spectator commands
    get_game_state = auto()
    become_player = auto()
    # player commands
    play_white_piece = auto()
    play_black_piece = auto()
    leave = auto()  # command only valid before game starts
    forfeit = auto()  # command only valid after game starts
    # host controls
    start_game = auto()
    kick_player = auto()
    close_game = auto()
    switch_places = auto()


class MessageType(StrEnum):
    acknowledge = auto()
    game_state = auto()
