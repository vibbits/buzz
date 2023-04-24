" HTTP API for poll and discussion state "

from itertools import groupby

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, deps
from app import models as dbmdl
from app.schemas import Comment, Discussion, Poll, State, User

router = APIRouter()


@router.get("/", response_model=State)
def get_state(
    database: Session = Depends(deps.get_db), _user: User = Depends(deps.current_user)
) -> State:
    """
    Current application state. Including:
    - Polls
    - Q&A
    """

    def make_poll(poll: dbmdl.Poll) -> Poll:
        "Create a Poll according to the schema from a ORM object."
        options = [(opt.text, opt.id) for opt in poll.options]
        votes = {
            id: len(list(vals))
            for (id, vals) in groupby(sorted(vote.option for vote in poll.votes))
        }
        return Poll(
            id=poll.id,
            title=poll.title,
            description=poll.description,
            hidden=poll.hidden,
            options=options,
            votes=votes,
        )

    def make_qa(question: dbmdl.Question) -> Discussion:
        "Create a Discussion accoring to the schema from an ORM object."
        return Discussion(
            id=question.id,
            text=question.text,
            votes=len(question.votes),
            user=f"{question.asker.first_name} {question.asker.last_name}",
            comments=[
                Comment(
                    id=comment.id,
                    text=comment.text,
                    user=f"{comment.commenter.first_name} {comment.commenter.last_name}",
                )
                for comment in question.comments
            ],
        )

    return State(
        polls=[make_poll(poll) for poll in crud.all_polls(database)],
        qas=[make_qa(discussion) for discussion in crud.all_discussions(database)],
    )
