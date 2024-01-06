from uuid import UUID
from pydantic import BaseModel
from server.models.orm.user_session import UserSession


class LoginRequest(BaseModel):
    """
    In a login request, if the client does not provide a user id, a
    new one will be created for them. This user id is returned for
    their reference.
    """
    user_id: UUID | None = None
    name: str


class LoginResponse(BaseModel):
    code: int
    message: str
    session: UserSession | None
    token: str | None


class ValidSessionResponse(BaseModel):
    success: bool
