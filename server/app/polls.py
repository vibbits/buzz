" Poll control functions and HTTP API "

from itertools import groupby

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, deps
from app.schemas import User, Poll

router = APIRouter()


@router.get("/", response_model=list[Poll])
async def get_polls(
    database: Session = Depends(deps.get_db), _user: User = Depends(deps.current_user)
):
    def make_poll(poll):
        options = [(opt.text, opt.id) for opt in poll.options]
        votes = {
            id: len(list(vals))
            for (id, vals) in groupby(sorted(vote.option for vote in poll.votes))
        }
        return Poll(
            id=poll.id,
            title=poll.title,
            description=poll.description,
            options=options,
            votes=votes,
        )

    return [make_poll(poll) for poll in crud.all_polls(database)]


def create_new_poll(
    database: Session, _uid: int, title: str, description: str, options: list[str]
):
    return crud.create_new_poll(database, title, description, options)


def delete_poll(database: Session, _uid: int, poll_id: int):
    return crud.delete_poll(database, poll_id)


def vote(database: Session, uid: int, poll: int, option: int):
    return crud.poll_vote(database, uid, poll, option)
