"""
Backend message type
"""
from typing import Generic, TypeVar
from pydantic import BaseModel

from server.constants import MessageType


T = TypeVar('T', bound='Message')


class Message(BaseModel, Generic[T]):
    type: MessageType
    body: T | None = None
