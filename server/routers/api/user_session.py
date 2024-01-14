from uuid import uuid4, UUID

from fastapi import APIRouter, Depends

from server.core.dependencies import get_user_session_manager, session_auth
from server.core.user_session import UserSessionManager
from server.models.dto.user_session import LoginRequest, LoginResponse, ValidSessionResponse

router = APIRouter()


@router.get("/session", response_model=ValidSessionResponse)
def api_valid_session(_ = Depends(session_auth)):
    """
    If client starts and it thinks it has a valid session, use this endpoint
    to check???
    TODO: this seems somewhat unnecessary? In general I think we don't actually
    use this, and we reconcile errors by running re-authentication if we try
    to do something like list-games and it fails?
    """
    return ValidSessionResponse(success=True)


@router.post("/login", response_model=LoginResponse)
def api_login(
    request: LoginRequest,
    user_session_manager: UserSessionManager = Depends(get_user_session_manager)
):
    """
    When opening the app, clients will first log in here.

    If the client does not have any credentials stored locally, they will just provide
    a name to the login endpoint. A user session is then created for the user if the
    login flow succeeds, and they are returned a user session object.
    """
    # TODO: mobile app is not currently capable of sending null values in serialization.
    # We adjust for this here by making the request uuid type a str type and casting it.
    user_id = (UUID(request.user_id) if request.user_id else None) or uuid4()
    session, token = user_session_manager.login(user_id, request.name)
    return LoginResponse(code=200, message="successful login", session=session, token=token)
