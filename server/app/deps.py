" Provide Depends() objects for all API endpoints "

from typing import Generator
from datetime import datetime, timezone

from fastapi import Depends, Header, HTTPException, status
from fastapi.security.utils import get_authorization_scheme_param
from jose import jwt
from jose.exceptions import JWTError
from sqlalchemy.orm import Session as SessionType

from app.config import settings
from app.database import Session
from app.schemas import User


def get_db() -> Generator[SessionType, None, None]:
    "Provide access to the database"
    try:
        database = Session()
        yield database
    finally:
        database.close()


def current_user(authorization: str = Header()) -> User:
    "Check the bearer token and retrieve associated user information."
    scheme, token = get_authorization_scheme_param(authorization)
    if scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid scheme",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(token, settings.api_secret, "HS256")
    except JWTError as err:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Decoding JWT: {err}"
        ) from err

    expiry = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    current_time = datetime.now(tz=timezone.utc)
    if expiry < current_time:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Credentials expired"
        )

    return User(**payload)


def current_admin(user: User = Depends(current_user)) -> User:
    """
    Check the bearer token is for an administrator,
    and return associated administrator information.
    """
    if not user.role == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not an admin"
        )

    return user
