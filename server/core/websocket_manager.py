"""
WebSocket Session Manager

This is intended for use with the game router endpoint
"""
import asyncio
import logging
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from fastapi import WebSocket
from server.core.game import GameManager
from server.models.orm.game import GameState

logger = logging.getLogger(__name__)


class Subscription:
    """
    This subscription class is responsible for the broadcast of the latest
    state values to individual clients.

    Problem Statement: if our publishes get backed up for whatever reason, the naive
    algorithm will progressively fall further and further behind. Instead, we should
    skip publishing older stale states and instead only publish latest states.

    Solution?: whenever the game state updates, we mark the subscription as stale, and
    that we must update it. At the start of an update out request, we first mark that
    we are attempting to update a client's game state. Afterwards we perform the publish
    and run the publish until success or giveup. On giveup, we generally mark the sub as
    dead and should proceed to clean it up. This means that if a large number of state
    updates come in while our coroutine is waiting, we read the latest version instead
    of trying to catch up to older, stale states.
    """

    # this is the current game state object model
    _game: GameState

    # this is used to look up the current json string cache for
    # the object model. this is always expected to match the same
    # as game state and is used so that multiple subscribers do not
    # need to serialize the same dictionary.
    _game_cache: dict[str, str]

    # websocket to publish state updates on
    _websocket: WebSocket

    # asyncio event to trigger stale state updates
    _stale: asyncio.Event

    # asyncio Task that runs the subscription update
    _task: asyncio.Task | None

    def __init__(
        self,
        game: GameState,
        game_cache: dict[str, str],
        websocket: WebSocket,
    ):
        self._game = game
        self._game_cache = game_cache
        self._websocket = websocket
        self._stale = asyncio.Event()
        self._task = None

    def start(self):
        self._task = asyncio.create_task(self.run())

    def stop(self):
        self._task.cancel()

    def mark_stale(self):
        self._stale.set()

    async def run(self):
        while True:
            await self._stale.wait()
            self._stale.clear()
            # read the latest value from game and publish it??
            # TODO: publish an update message instead of printing out
            print(self._game_cache.get(self._game.uuid))


class Role(Enum):
    """
    (very) Basic RBAC
    """
    FORBIDDEN = 0  # forbidden
    SPECTATOR = 1
    PLAYER = 2
    HOST = 3
    ADMIN = 4


class WebSocketManager:

    _game_manager: GameManager
    # map of subscription id to subscription object
    _subscriptions: dict[UUID, Subscription]
    # map of game id to subscriptions for that game
    _game_to_subs: dict[UUID, list[Subscription]]

    def __init__(self, game_manager: GameManager):
        self._game_manager = game_manager
        self._subscriptions = dict()
        self._game_to_subs = dict()
        self._game_manager.register_subscriber(self._update_subscribers)

    async def handshake(self, websocket: WebSocket, game_id: UUID, user_id: UUID) -> Role:
        """
        Perform the initial handshake.
        """
        game = self._game_manager.get_game_by_id(game_id)
    
        # TODO: consider if we should not let players connect to finished games
        if game is None:
            logger.warning("Attempted to connect to a non-existent game")
            await websocket.close(code=1008, reason="No game found with that uuid")
            return Role.FORBIDDEN

        if user_id == game.host_player_id:
            return Role.HOST
        if user_id == game.white_player_id or user_id == game.black_player_id:
            return Role.PLAYER

        # TODO: handle some additional authorization?
        return Role.SPECTATOR

    def _update_subscribers(self, game: GameState):
        """
        Find all subscriptions for a specific game and flag them to update.
        """
        subs = self._game_to_subs[game.uuid]
        for sub in subs:
            sub.mark_stale()

    def subscribe(self, websocket: WebSocket, game_id: UUID) -> UUID:
        sub_id = uuid4()
        game = self._game_manager.get_game_by_id(game_id)
        if game is None:
            raise ValueError("Missing game by id")

        sub = Subscription(
            game=game,
            game_cache=self._game_manager.game_cache,
            websocket=websocket
        )
        sub.start()
        self._subscriptions[sub_id] = sub
        self._game_to_subs[game_id].append(sub)

    def unsubscribe(self, sub_id: UUID, game_id: UUID):
        sub = self._subscriptions.pop(sub_id, None)
        if sub is None:
            logger.warning(f"Could not find subscription with uuid {sub_id}")
            return
        game_subs = self._subscriptions[game_id]
        sub.stop()
        if sub not in game_subs:
            logger.warning(f"Could not find subscription with uuid {sub_id} in game subs for {game_id}")

    async def dispatch(self, data: dict[str, Any], role: Role):
        # TODO: implement
        print(f"Dispatch with {data} - role={role}")
