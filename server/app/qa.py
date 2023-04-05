" Q&A (Discussion or Question) control and response formatting functions "

from sqlalchemy.orm import Session

from app import crud
from app.schemas import User


def create_new_discussion(database: Session, user: User, text: str):
    "Create a new Q&A."
    return crud.create_new_discussion(database, user, text)


def vote(database: Session, _user: User, question: int):
    "Vote on a question."
    return crud.qa_vote(database, question)


def comment(database: Session, user: User, text: str, question: int):
    "Comment on a question."
    return crud.qa_comment(database, user, text, question)


def delete(database: Session, _user: User, question: int):
    "Delete a whole Q&A."
    return crud.qa_delete(database, question)
