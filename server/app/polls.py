" Poll control functions and HTTP API "

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, deps
from app.schemas import User, Poll

router = APIRouter()


@router.get("/", response_model=list[Poll])
async def get_polls(
    database: Session = Depends(deps.get_db), _user: User = Depends(deps.current_user)
):
    return [Poll.from_orm(poll) for poll in crud.all_polls(database)]


def create_new_poll(
    database: Session, _uid: int, title: str, description: str, options: list[str]
):
    return crud.create_new_poll(database, title, description, options)


def vote(database: Session, uid: int, poll: int, option: int):
    return crud.poll_vote(database, uid, poll, option)
