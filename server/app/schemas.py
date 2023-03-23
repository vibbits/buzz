" Data schemas for the HTTP interface "
from typing import Literal, Optional, Union

from pydantic import BaseModel

# Auth / User


class User(BaseModel):
    "A User"
    id: int
    first_name: str
    last_name: str
    role: Union[Literal["user"], Literal["admin"]]
    image: Optional[str]

    class Config:
        orm_mode = True


class Token(BaseModel):
    "An API Bearer Token"
    access_token: str
    user: User


class AuthorizationCode(BaseModel):
    "The result of a login using the OpenID Connect Authorization Code flow."
    code: str
    redirect: str


# Polls


class Poll(BaseModel):
    "A Poll description"
    id: int
    title: str
    description: str
    options: list[tuple[str, int]]
    votes: dict[int, int]
