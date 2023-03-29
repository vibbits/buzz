" HTTP API for poll and discussion state "

from itertools import groupby

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, deps
from app.schemas import Comment, Discussion, Poll, State, User

router = APIRouter()


@router.get("/", response_model=State)
def get_state(
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

    def make_qa(qa):
        return Discussion(
            id=qa.id,
            text=qa.text,
            votes=qa.votes,
            user=f"{qa.asker.first_name} {qa.asker.last_name}",
            comments=[
                Comment(
                    id=comment.id,
                    text=comment.text,
                    user=f"{comment.commenter.first_name} {comment.commenter.last_name}",
                )
                for comment in qa.comments
            ],
        )

    return State(
        polls=[make_poll(poll) for poll in crud.all_polls(database)],
        qas=[make_qa(discussion) for discussion in crud.all_discussions(database)],
    )
