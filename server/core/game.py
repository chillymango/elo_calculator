import logging
from collections import defaultdict
from contextlib import contextmanager
from typing import Callable
from uuid import UUID

from server import constants
from server.models.orm.game import GameState

logger = logging.getLogger(__name__)


class GameManager:
    
    # map of game id to game state
    _games: dict[UUID, GameState]
    # a list of subscriber callbacks
    _game_subs: list[Callable[[GameState], None]]
    # cached json blobs for game states. intended for network transport
    _game_cache: dict[UUID, str]

    def __init__(self):
        self._games = dict()
        self._game_subs = list()
        self._game_cache = dict()
        self._game_codes = dict()

        test_game = GameState()
        test_game.uuid = constants.TEST_GAME_ID
        self.set_game(test_game)

    def create_game(self) -> GameState:
        game = GameState()
        self._games[game.uuid] = game
        return game

    def set_game(self, game: GameState) -> None:
        self._games[game.uuid] = game

    def get_game_by_id(self, game_id: UUID) -> GameState | None:
        return self._games.get(game_id)

    def get_all_game_ids(self) -> list[UUID]:
        return list(self._games.keys())

    @property
    def game_cache(self) -> dict[UUID, str]:
        return self._game_cache

    def register_subscriber(self, callback: Callable[[GameState], None]):
        """
        A subscriber is a callable which takes a GameState object as input
        and returns None.

        These subscribers will run on all game changes.
        """
        self._game_subs.append(callback)

    def unregister_subscriber(self, callback: Callable[[GameState], None]):
        """
        The unregister will need to be done by providing the actual original callback.
        """
        if callback not in self._game_subs:
            logger.warning(f"Tried to remove non-existent callback {callback}")
            return
        self._game_subs.remove(callback)

    def _update_game(self, game: GameState):
        self._game_cache[game.uuid] = game.network_json()
        for cb in self._game_subs:
            cb(game)

    @contextmanager
    def game_context(self, game_id: UUID) -> GameState:
        game = self.get_game_by_id(game_id)
        if game is None:
            raise ValueError("Missing game with specified id")

        # NOTE: we enforce ACID by retaining a copy of the original object.
        # We need to use a deep copy because the game state contains a 3D list.
        orig = game.copy(deep=True)
        try:
            yield game
        except BaseException:
            game = orig
        finally:
            self._update_game(game)
