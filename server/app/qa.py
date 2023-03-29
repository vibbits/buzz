" Q&A (Discussion) control functions "

from sqlalchemy.orm import Session

from app import crud
from app.schemas import User


def create_new_discussion(database: Session, user: User, text: str):
    return crud.create_new_discussion(database, user, text)
