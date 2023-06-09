" Data schemas for the HTTP interface "
# pylint: disable=too-few-public-methods,no-name-in-module

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
        "Enable ORM mode."
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
    hidden: bool
    options: list[tuple[str, int]]
    votes: dict[int, int]


class Comment(BaseModel):
    "A Q&A comment  on a discussion thread"
    id: int
    text: str
    user: str


class Discussion(BaseModel):
    "A Q&A discussion"
    id: int
    text: str
    votes: int
    user: str
    comments: list[Comment]


class State(BaseModel):
    "Current application state."
    polls: list[Poll]
    qas: list[Discussion]
