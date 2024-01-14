import asyncio
import logging
from collections import defaultdict
from contextlib import contextmanager
from typing import Callable, Iterator
from uuid import UUID

from server import constants
from server.models.orm.game import GameState

logger = logging.getLogger(__name__)

SENTINEL_TIMEOUT = 60.0


class GameManager:
    
    # map of game id to game state
    _games: dict[UUID, GameState]
    # a list of subscriber callbacks
    _game_subs: list[Callable[[GameState], None]]
    # cached json blobs for game states. intended for network transport
    _game_cache: dict[UUID, str]
    # map of game code to game
    _game_codes: dict[UUID, GameState]
    # a map of game id to connection sentinel for host connection validation.
    # a connection sentinel is an asyncio event that gets set by the websocket
    # handler when the host of a game connects to the game.
    _sentinels: dict[UUID, asyncio.Event]

    def __init__(self):
        """
        NOTE: because FastAPI uses asyncio i don't believe we need to lock this class. A dictionary
        update is not awaitable and so there's no danger to multiple coroutines making update calls
        at similar times.
        """
        self._games = dict()
        self._game_subs = list()
        self._game_cache = dict()
        self._game_codes = dict()
        self._sentinels = dict()

        test_game = GameState()
        test_game.uuid = constants.TEST_GAME_ID
        self.set_game(test_game)

    def create_game(self, host_player_id: UUID) -> GameState:
        # by default set them to white
        game = GameState(host_player_id=host_player_id, white_player_id=host_player_id)
        self._games[game.uuid] = game
        self._game_cache[game.uuid] = game.network_json()
        self._game_codes[game.code] = game
        # if game creator does not connect to the game within 1 minute, we should
        # cancel the game and issue a termination request
        self._sentinels[game.uuid] = asyncio.Event()
        asyncio.create_task(self.cancel_game(game.uuid))
        return game

    async def cancel_game(self, game_id: UUID):
        """
        If a game is created but the host does not connect over WebSocket
        """
        try:
            await asyncio.wait_for(self._sentinels[game_id].wait(), timeout=SENTINEL_TIMEOUT)
            return
        except asyncio.TimeoutError:
            pass

        # if our sentinel timed out, rotate the game into an unfinished state
        with self.game_context(game_id) as game:
            game.close()

    def set_game(self, game: GameState) -> None:
        self._games[game.uuid] = game

    def get_game_by_id(self, game_id: UUID) -> GameState | None:
        return self._games.get(game_id)

    def get_game_by_code(self, game_code: str) -> GameState | None:
        return self._game_codes.get(game_code)

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
    def game_context(self, game_id: UUID) -> Iterator[GameState]:
        """
        WARN: do not put any awaitable in the game context. The concurrency safety
        of this function is generally guaranteed by the assumption that this
        coroutine will run from start to finish in a single iteration.

        TODO: when switching to redis for game storage (which is needed for supporting
        a multiprocess game server), this logic will need to be revised to include a
        multiprocessing locking mechanism.

        See: https://redis.io/docs/manual/patterns/distributed-locks/
        """
        game = self.get_game_by_id(game_id)
        if game is None:
            raise ValueError("Missing game with specified id")

        # NOTE: we enforce ACID by retaining a copy of the original object.
        # We need to use a deep copy because the game state contains a 3D list.
        orig = game.copy(deep=True)
        try:
            yield game
            self._update_game(game)
        except BaseException:
            game = orig           
