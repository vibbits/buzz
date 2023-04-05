" Application and API authorization functions "

from datetime import datetime, timezone

from jose import jwt
from jose.exceptions import JOSEError

from app.config import settings
from app.schemas import User


class AuthorizationError(Exception):
    "An error arrising from authorizing a user from a bearer token."


def user_from_token(token: str) -> User:
    """
    Check user authorization from a bearer token.
    Return user information on success.
    Throw an error if authorization fails.
    """
    try:
        payload = jwt.decode(token, settings.api_secret, "HS256")
    except JOSEError as err:
        raise AuthorizationError(str(err)) from err

    expiry = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    current_time = datetime.now(tz=timezone.utc)
    if expiry < current_time:
        raise AuthorizationError("Credential has expired")

    return User(**payload)
