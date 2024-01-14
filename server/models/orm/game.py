import logging
import random
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, root_validator

from server.utils import board_util

logger = logging.getLogger(__name__)

class Phase(int, Enum):
    INITIALIZED = 0
    RUNNING = 1
    PAUSED = 2
    FINISHED = 3
    ERROR = 4


class EndOfGameTrigger(str, Enum):
    ERROR = 0
    BOARD_POSITION = 1
    FORFEIT = 2
    LOBBY_CLOSE = 3


def initialize_board(size: int = 5):
    return [[[0 for _ in range(size)] for _ in range(size)] for _ in range(size)]


def gen_random_code(length: int = 4, alpha = "ABCDEFGHJKLMNPQRSTUVWXYZ"):
    return "".join(alpha[random.randrange(0, len(alpha))] for _ in range(length))


# we pre-generate some to ensure that we never run into collisions.
# codes are put back into the available pool after games finish and get
# recorded by the cleanup worker.
RANDOM_CODES = set(gen_random_code() for _ in range(10000))

def get_random_code():
    return RANDOM_CODES.pop()


class GameState(BaseModel):
    """
    This model is intended to be stored locally.

    At the moment, storage in a single process is acceptable.
    If we need to scale to multiple hosts we can just use redis.
    """
    created_at: datetime = Field(default_factory=datetime.utcnow)
    modified_at: datetime = Field(default_factory=datetime.utcnow)
    finished_at: datetime | None = None

    uuid: UUID = Field(default_factory=uuid4)
    code: str = Field(default_factory=get_random_code)

    # The board is a 3D array of integers.
    # 0 indicates an unoccupied space.
    # 1 indicates white has played.
    # 2 indicates black has played.
    board: list[list[list[int]]] = Field(default_factory=initialize_board)

    # the host gets extra permissions in the lobby, for example to change the clock
    # settings, or to swap player colors (or set to random). the host is the first
    # player to join the game.
    host_player_id: UUID | None
    white_player_id: UUID | None
    black_player_id: UUID | None

    white_is_connected: bool = False
    black_is_connected: bool = False
    spectator_count: int = 0

    phase: Phase = Phase.INITIALIZED
    end_of_game_trigger: EndOfGameTrigger | None = None
    winner: int = 0

    # When clients make play move requests they will need to provide the
    # turn number. In doing this, they will ensure that we do not apply the
    # same move multiple times.
    turn_number: int = 0

    # move history is typically not broadcast over network unless specifically
    # requested by client.
    # move history tuple is (player, x, y, z)
    move_history: list[tuple[int, int, int, int]] = Field(default_factory=list)

    @root_validator(pre=True)
    def update_modified_at(cls, values):
        # Check if it's an update (not the initial creation)
        if 'modified_at' in values and values['modified_at'] is not None:
            values['modified_at'] = datetime.utcnow()
        return values

    @property
    def whose_turn(self):
        if self.phase == Phase.RUNNING and self.turn_number % 2 == 0:
            return 1
        if self.phase == Phase.RUNNING and self.turn_number % 2 == 1:
            return 2
        return 0

    def network_json(self):
        return self.json(exclude=set(["move_history"]))

    def _play_piece(self, player: int, x: int, y: int, z: int):
        self._only_in_game("Play Piece")
        if self.board[x][y][z] != 0:
            raise ValueError("Position already occupied")
        self.turn_number += 1
        self.move_history.append((player, x, y, z))
        self.board[x][y][z] = 1

        if board_util.has_four_in_line(self.board, player):
            self.end_of_game(EndOfGameTrigger.BOARD_POSITION)

    def _only_on_init(self, name: str):
        if self.phase != Phase.INITIALIZED:
            raise ValueError(f"Cannot `{name}` after game has started")

    def _only_in_game(self, name: str):
        if self.phase != Phase.RUNNING:
            raise ValueError(f"Cannot `{name}` if game is not running")

    def switch_places(self):
        self._only_on_init("Switch Places")
        self.white_player_id, self.black_player_id = self.black_player_id, self.white_player_id

    def remove_player(self, remove_player_id: UUID):
        self._only_on_init("Remove Player")
        if self.white_player_id == remove_player_id:
            self.white_player_id = None
        elif self.black_player_id == remove_player_id:
            self.black_player_id = None

    def play_white(self, x: int, y: int, z: int):
        self._play_piece(1, x, y, z)

    def play_black(self, x: int, y: int, z: int):
        self._play_piece(2, x, y, z)

    def try_promote_player(self, user_id: UUID):
        """
        Attempt to promote a user into a game player.

        This operation will only succeed if there are available player slots. There should
        only be 0 or 1 available player slot at any given time (a room with 2 empty slots
        should be deleted), so promoting a player successfully will have them occupy the
        free slot.
        """
        self._only_on_init("Promote Player")
        if self.white_player_id is None and self.black_player_id is None:
            raise ValueError("Lobby appears to be empty and closed")
        if self.white_player_id is not None and self.black_player_id is not None:
            raise ValueError("Game has two active players already")

        if self.white_player_id is not None:
            self.black_player_id = user_id
        elif self.white_player_id is not None:
            self.white_player_id = user_id

        raise RuntimeError("Something went very wrong")

    def _user_is_game_player(self, user_id: UUID) -> bool:
        return user_id in (self.white_player_id, self.black_player_id)

    def start(self) -> None:
        self._only_on_init("Start")
        logger.debug(f"Game with id {self.uuid} has started")
        self.phase = Phase.RUNNING

    def player_leave_game(self, user_id: UUID):
        """
        Remove player from game. If the player is not in the game, we consider this to be
        a no-op and do not throw an exception. This will just return success to the client.
        """
        # this is only valid in games that are not currently running
        self._only_on_init("Leave Game")
        if user_id == self.white_player_id:
            self.white_player_id = None
        elif user_id == self.black_player_id:
            self.black_player_id = None

    def end_of_game(self, winner: int, trigger: EndOfGameTrigger):
        self.end_of_game_trigger = trigger
        match trigger:
            case EndOfGameTrigger.ERROR:
                self.phase = Phase.ERROR
            case EndOfGameTrigger.BOARD_POSITION:
                self.winner = winner
                self.phase = Phase.FINISHED
            case EndOfGameTrigger.FORFEIT:
                self.winner = winner
                self.phase = Phase.FINISHED
            case EndOfGameTrigger.LOBBY_CLOSE:
                self.phase = Phase.FINISHED

    def close(self):
        self.end_of_game(0, EndOfGameTrigger.LOBBY_CLOSE)

    def player_forfeit_game(self, user_id: UUID):
        """
        Active player forfeits game. If this is successful we trigger an end-of-game event.
        """
        self._only_in_game("Forfeit Game")
        # This is only valid in games that are currently running.
        if user_id == self.white_player_id:
            winner = 2
        elif user_id == self.black_player_id:
            winner = 1
        else:
            raise ValueError("Forfeiting user does not appear to be a game player")
        self.end_of_game(winner, EndOfGameTrigger.FORFEIT)
