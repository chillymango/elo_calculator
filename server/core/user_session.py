from datetime import datetime, timedelta
from uuid import UUID

from server.models.orm.user_session import UserSession
from server.utils import jwt_util


SessionAndToken = tuple[UserSession, str]


class UserSessionManager:
    """
    Internal storage of user sessions.

    When a user connects through the game for the first time, they are
    granted a session token. The session token needs to be provided on
    all requests in order for the requests to be valid.

    User sessions will also keep track of whether a user is in an active
    game or not. If a user is in an active game when they connect, that
    game will be brought up.
    """

    _expiry_timedelta: timedelta

    # map of session id to a user session
    _user_sessions: dict[UUID, UserSession]
    # need to be able to look up sessions by user
    _user_id_to_session: dict[UUID, UserSession]

    def __init__(self, expiry_timedelta: timedelta | None = None):
        # by default if we don't log in for 2 days we clear the user session
        self._expiry_timedelta = expiry_timedelta or timedelta(days=2)
        self._user_sessions = dict()
        self._user_id_to_session = dict()

    def create_user_session(self, user_id: UUID, name: str) -> UserSession:
        # TODO: add name validation
        return UserSession(user_id=user_id, name=name, expires_at=datetime.utcnow() + self._expiry_timedelta)

    def login(self, user_id: UUID, name: str) -> SessionAndToken:
        """
        Perform a login flow for the given user.

        This will also generate a jwt access token for the user. The access token
        will be used to establish identity in future requests made to the service.
        """
        user_session = self.create_user_session(user_id, name)
        token = jwt_util.create_access_token({"user_id": user_id.hex}, expires_at=user_session.expires_at)
        self._user_sessions[user_session.uuid] = user_session
        self._user_id_to_session[user_id] = user_session
        return (user_session, token)

    def get_session_for_user_id(self, user_id: UUID) -> UserSession | None:
        return self._user_id_to_session.get(user_id)

    def get_session_by_id(self, session_id: UUID) -> UserSession | None:
        return self._user_sessions.get(session_id)
