" Poll control functions and HTTP API "

from itertools import groupby

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, deps
from app.schemas import User, Poll


def create_new_poll(
    database: Session, _user: User, title: str, description: str, options: list[str]
):
    "Create a new poll in the database and format a reponse."
    return crud.create_new_poll(database, title, description, options)


def delete_poll(database: Session, _user: User, poll_id: int):
    "Remove a poll from the database and format a response."
    return crud.delete_poll(database, poll_id)


def vote(database: Session, user: User, poll: int, option: int):
    "Add a vote to the database and format a response."
    return crud.poll_vote(database, user.id, poll, option)
