" Q&A (Discussion) control functions "

from sqlalchemy.orm import Session

from app import crud
from app.schemas import User


def create_new_discussion(database: Session, user: User, text: str):
    return crud.create_new_discussion(database, user, text)


def vote(database: Session, _user: User, qa: int):
    return crud.qa_vote(database, qa)


def comment(database: Session, user: User, text: str, qa: int):
    return crud.qa_comment(database, user, text, qa)


def delete(database: Session, _user: User, qa: int):
    return crud.qa_delete(database, qa)
