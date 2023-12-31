from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm.session import Session

from server.core.database import get_sessionlocal
from server.utils import jwt_util
from server.utils import tabulation_util


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def validate_token(token: str = Depends(oauth2_scheme)):
    try:
        jwt_util.decode_token(token)
    except:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={'WWW-Authenticate': 'Bearer'}
        )


def get_database():
    db = get_sessionlocal()()
    try:
        yield db
    finally:
        db.close()


CACHE: dict[Any, Any] = {}


def get_cache():
    yield CACHE


def update_cache(db: Session = Depends(get_database)):
    # TODO: define cache interface, support redis, etc
    try:
        yield CACHE
    finally:
        # try and update the cache here but do not throw exception if we fail
        print("Updating cache")
        tabulation_util.update_cache(CACHE, db)
