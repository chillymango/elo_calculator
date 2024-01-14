from functools import wraps
from typing import Any, Callable

from server.constants import CommandType
from server.models.dto.command import Command


CommandCallback = Callable[[Command, Any], None]


class CommandRouter:
    """
    Supports a similar interface to the FastAPI APIRouter.

    Commands typically respond with an acknowledge of success, but this
    does not generally carry any data. The response object is intended
    to ACK so the client can proceed to the next request.
    """

    # routes are keyed on command key (str enum)
    routes: dict[CommandType, CommandCallback]

    def __init__(self):
        self.routes = dict()

    def add_command(self, command_type: CommandType, callback: CommandCallback):
        if command_type in self.routes:
            raise ValueError(f"Already have a command handler for type {command_type}")
        self.routes[command_type] = callback

    def command(self, command_type: CommandType):
        def decorator(func: CommandCallback) -> Command:
            self.add_command(command_type, func)
            return func
        return decorator
