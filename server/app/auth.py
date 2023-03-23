" User authentication with VIB Services "

from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
import httpx
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTClaimsError, JWTError

from app import crud, deps
from app.config import settings
from app.database import Session
from app.oidc import token, user_info
from app.schemas import AuthorizationCode, Token, User

router = APIRouter()


@router.get("/login")
async def login_redirect(redirect: str):
    params = {
        "client_id": "training_vote",
        "redirect_uri": redirect,
        "response_type": "code",
        "scope": "openid profile",
        "state": "null",
    }
    return RedirectResponse(
        f"https://services.vib.be/connect/authorize?{urlencode(params)}"
    )


def create_access_token(user: dict[str, str]) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.api_token_expire)
    to_encode = user | {"exp": expire.timestamp()}
    return jwt.encode(to_encode, settings.api_secret, "HS256")


@router.post("/token")
async def get_bearer_token(
    body: AuthorizationCode, database: Session = Depends(deps.get_db)
) -> Token:
    (tkn, keys) = await token(body.code, body.redirect)
    if "error" in tkn:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Fetching token: {tkn['error']}",
        )

    try:
        id_token = jwt.decode(
            tkn["id_token"],
            keys,
            audience="training_vote",
            access_token=tkn["access_token"],
        )
    except (ExpiredSignatureError, JWTClaimsError, JWTError) as err:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Decoding JWT: {err}"
        ) from err

    if (
        user := crud.get_user_by_subject(database, subject=int(id_token["sub"]))
    ) is None:
        userinfo = await user_info(tkn["access_token"])
        user = crud.create_user(
            database,
            subject=int(id_token["sub"]),
            first_name=userinfo["name"],
            last_name=userinfo["family_name"],
            image=None,
        )

    access_token = create_access_token(
        {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "iat": user.created.timestamp(),
            "role": user.role,
        }
    )

    return Token(access_token=access_token, user=User.from_orm(user))


@router.get("/me")
async def me(user: User = Depends(deps.current_user)):
    return user
