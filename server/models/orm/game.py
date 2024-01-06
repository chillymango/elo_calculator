from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, root_validator


class Phase(int, Enum):
    INITIALIZED = 0
    RUNNING = 1
    PAUSED = 2
    FINISHED = 3


def initialize_board(size: int = 5):
    return [[[0 for _ in range(size)] for _ in range(size)] for _ in range(size)]


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
    winner: int = 0

    # When clients make play move requests they will need to provide the
    # turn number. In doing this, they will ensure that we do not apply the
    # same move multiple times.
    turn_number: int = 0

    # move history is typically not broadcast over network unless specifically
    # requested by client.
    move_history: list[tuple[int, int]] = Field(default_factory=list)

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

    def play_white(self, x: int, y: int, z: int):
        self.board[x][y][z] = 1

    def play_black(self, x: int, y: int, z: int):
        self.board[x][y][z] = 2
