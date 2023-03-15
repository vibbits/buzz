" Create, Read, Update, and Delete on database reseources "

from typing import Optional
from datetime import datetime, timezone

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import User, Poll, PollOption, PollVote

# Auth


def get_user_by_subject(database: Session, subject: int) -> Optional[User]:
    return database.query(User).filter(User.id == subject).one_or_none()


def create_user(
    database: Session,
    subject: int,
    first_name: str,
    last_name: str,
    image: Optional[str],
) -> User:
    user = User(
        id=subject,
        created=datetime.now(timezone.utc),
        first_name=first_name,
        last_name=last_name,
        role="user",
        image=image,
    )

    try:
        database.add(user)
    except SQLAlchemyError as err:
        database.rollback()
        raise err
    else:
        database.commit()

    database.refresh(user)
    return user


def promote(database: Session, uid: int):
    if (user := database.query(User).filter(User.id == uid).one_or_none()) is not None:
        user.role = "admin"
        database.commit()
        database.refresh(user)
    return user


# Polls


def all_polls(database: Session):
    return database.query(Poll).all()


def create_new_poll(
    database: Session, title: str, description: str, options: list[str]
):
    poll = Poll(
        created=datetime.now(tz=timezone.utc), title=title, description=description
    )

    try:
        database.add(poll)
    except SQLAlchemyError as err:
        database.rollback()
        raise err
    else:
        database.commit()

    database.refresh(poll)
    poll_options = [PollOption(poll=poll.id, text=text) for text in options]
    try:
        database.add_all(poll_options)
    except SQLAlchemyError as err:
        database.rollback()
        raise err
    else:
        database.commit()

    final_options = database.query(PollOption).filter(PollOption.poll == poll.id).all()
    return {
        "id": poll.id,
        "title": title,
        "description": description,
        "options": [(opt.id, opt.text) for opt in final_options],
    }


def poll_vote(database: Session, uid: int, poll: int, option: int):
    vote = PollVote(option=option, poll=poll, user=uid)

    try:
        database.add(vote)
    except SQLAlchemyError as err:
        database.rollback()
        raise err
    else:
        database.commit()

    return {"poll": poll, "option": option}
