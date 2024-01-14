from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from server.core import env
from server.core.dependencies import validate_token
from server.utils import jwt_util

router = APIRouter()


def authenticate_user(username: str, password: str):
    if username != env.AUTH_USERNAME or password != env.AUTH_PASSWORD:
        return None
    return dict(username=username, password=password)


@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if user is None:
        raise HTTPException(\
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={'WWW-Authenticate': 'Bearer'}
        )
    token_expiry = timedelta(minutes=env.TOKEN_EXPIRY_MINUTES)
    access_token = jwt_util.create_access_token({"sub": user["username"]}, expires_delta=token_expiry)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/is_authorized")
async def is_authorized(token = Depends(validate_token)):
    return "ok"

# TODO: implement refresh token
