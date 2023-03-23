" Abstraction for OpenID Connect and the VIB Services API "

import asyncio

import httpx

from app.config import settings

Token = dict[str, str]
Jwks = dict[str, str]


async def token(code: str, redirect: str) -> tuple[Token, Jwks]:
    async with httpx.AsyncClient() as client:
        [tkn, jwks] = await asyncio.gather(
            asyncio.ensure_future(
                client.post(
                    "https://services.vib.be/connect/token",
                    data={
                        "client_id": "training_vote",
                        "client_secret": settings.client_secret,
                        "grant_type": "authorization_code",
                        "code": code,
                        "state": "",
                        "scope": "openid profile email userroles roles",
                        "redirect_uri": redirect,
                    },
                )
            ),
            asyncio.ensure_future(
                client.get(
                    "https://services.vib.be/.well-known/openid-configuration/jwks"
                )
            ),
        )
        return (tkn.json(), jwks.json())


async def user_info(access_token: str) -> dict[str, str]:
    async with httpx.AsyncClient() as client:
        info = await client.get(
            "https://services.vib.be/connect/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        return info.json()
