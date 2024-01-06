from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class UserSession(BaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    user_id: UUID
    # TODO: eventually create real user accounts with some basic
    # auth in order to handle things like ranked matches. But
    # for now we can just enter a name when they open the app
    name: str
    expires_at: datetime

    @property
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at
