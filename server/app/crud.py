" Create, Read, Update, and Delete on database reseources "

from typing import Optional
from datetime import datetime, timezone

from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app import schemas
from app.models import User, Poll, PollOption, PollVote, Question, QuestionComment

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
    return database.query(Poll).order_by(desc(Poll.created)).all()


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
        "options": [(opt.text, opt.id) for opt in final_options],
    }


def delete_poll(database: Session, poll: int):
    the_poll = database.query(Poll).filter(Poll.id == poll).one_or_none()
    if the_poll is not None:
        database.delete(the_poll)
        database.commit()
        return {"poll_id": poll}

    return {}


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


# Discussions / Q&A


def all_discussions(database: Session):
    return (
        database.query(Question)
        .order_by(desc(Question.created), desc(Question.votes))
        .all()
    )


def create_new_discussion(database: Session, user: schemas.User, text: str):
    qa = Question(
        created=datetime.now(tz=timezone.utc), text=text, votes=0, user=user.id
    )

    try:
        database.add(qa)
    except SQLAlchemyError as err:
        database.rollback()
        raise err
    else:
        database.commit()

    database.refresh(qa)

    return {
        "id": qa.id,
        "text": qa.text,
        "user": f"{user.first_name} {user.last_name}",
    }


def qa_vote(database: Session, qa: int):
    if (
        discussion := database.query(Question).filter(Question.id == qa).one_or_none()
    ) is not None:
        discussion.votes = discussion.votes + 1
        database.commit()

        return {"qa": qa}
    return {}


def qa_comment(database: Session, user: schemas.User, text: str, qa: int):
    comment = QuestionComment(
        created=datetime.now(tz=timezone.utc), text=text, question=qa, user=user.id
    )

    try:
        database.add(comment)
    except SQLAlchemyError as err:
        database.rollback()
        raise err
    else:
        database.commit()

    database.refresh(comment)

    return {
        "id": comment.id,
        "qa": comment.question,
        "text": comment.text,
        "user": f"{user.first_name} {user.last_name}",
    }
