" Create, Read, Update, and Delete on database reseources "

from typing import Optional
from datetime import datetime, timezone

from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app import schemas
from app.models import (
    User,
    Poll,
    PollOption,
    PollVote,
    Question,
    QuestionComment,
    QuestionVote,
)

# Auth


def get_user_by_subject(database: Session, subject: int) -> Optional[User]:
    "Retrieve a user from the database given their OpenID Connect unique identifier (subject)."
    return database.query(User).filter(User.id == subject).one_or_none()


def create_user(
    database: Session,
    subject: int,
    first_name: str,
    last_name: str,
    image: Optional[str],
) -> User:
    "Create a user in the database."
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

    database.commit()

    database.refresh(user)
    return user


def promote(database: Session, uid: int) -> Optional[User]:
    "Promote a user: change role from user to admin."
    if (user := database.query(User).filter(User.id == uid).one_or_none()) is not None:
        user.role = "admin"
        database.commit()
        database.refresh(user)
    return user


# Polls


def all_polls(database: Session) -> list[Poll]:
    "Retrieve all polls from the database."
    return database.query(Poll).order_by(desc(Poll.created)).all()


def create_new_poll(
    database: Session, title: str, description: str, hidden: bool, options: list[str]
) -> Poll:
    "Create a new poll in the database."
    poll = Poll(
        created=datetime.now(tz=timezone.utc),
        title=title,
        description=description,
        hidden=hidden,
    )

    try:
        database.add(poll)
    except SQLAlchemyError as err:
        database.rollback()
        raise err

    database.commit()

    poll_options = [PollOption(poll=poll.id, text=text) for text in options]
    try:
        database.add_all(poll_options)
    except SQLAlchemyError as err:
        database.rollback()
        raise err

    database.commit()
    database.refresh(poll)

    return poll


def delete_poll(database: Session, poll: int) -> None:
    "Remove a poll from the database. Returns False on failure"
    the_poll = database.query(Poll).filter(Poll.id == poll).one_or_none()
    if the_poll is not None:
        database.delete(the_poll)
        database.commit()


def hide_poll(database: Session, poll: int) -> None:
    """
    Show poll in the database.
    """
    db_poll = database.query(Poll).filter(Poll.id == poll).one_or_none()

    try:
        if db_poll is not None:
            db_poll.hidden = True
        database.commit()
    except SQLAlchemyError as err:
        database.rollback()
        raise err


def show_poll(database: Session, poll: int) -> None:
    """
    Show poll in the database.
    """
    db_poll = database.query(Poll).filter(Poll.id == poll).one_or_none()

    try:
        if db_poll is not None:
            db_poll.hidden = False
        database.commit()
    except SQLAlchemyError as err:
        database.rollback()
        raise err


def poll_vote(database: Session, uid: int, poll: int, option: int) -> None:
    """
    Add a vote to a poll in the database.
    If the vote already exists, delete it.
    """
    try:
        if (
            vote := database.query(PollVote)
            .filter(PollVote.user == uid, PollVote.option == option)
            .one_or_none()
        ) is None:
            database.add(PollVote(option=option, poll=poll, user=uid))
        else:
            database.delete(vote)

        database.commit()
    except SQLAlchemyError as err:
        database.rollback()
        raise err


def poll_votes(database: Session, poll: int, option: int) -> list[PollVote]:
    "Retrieve the votes for a given poll option"
    return (
        database.query(PollVote)
        .filter(PollVote.poll == poll, PollVote.option == option)
        .all()
    )


# Discussions / Q&A


def all_discussions(database: Session) -> list[Question]:
    "Retrieve all Q&As form the database."
    return database.query(Question).order_by(desc(Question.created)).all()


def create_new_discussion(database: Session, user: schemas.User, text: str) -> Question:
    "Create a new Q&A in the database."
    discussion = Question(
        created=datetime.now(tz=timezone.utc), text=text, user=user.id
    )

    try:
        database.add(discussion)
    except SQLAlchemyError as err:
        database.rollback()
        raise err

    database.commit()

    database.refresh(discussion)
    return discussion


def qa_votes(database: Session, question: int) -> list[QuestionVote]:
    "Retrieve the votes for a given Q&A"
    return database.query(QuestionVote).filter(QuestionVote.question == question).all()


def qa_vote(database: Session, uid: int, question: int) -> None:
    """
    Add a vote to a question in the database.
    If the vote already exists, delete it.
    """
    try:
        if (
            vote := database.query(QuestionVote)
            .filter(QuestionVote.user == uid, QuestionVote.question == question)
            .one_or_none()
        ) is None:
            database.add(QuestionVote(question=question, user=uid))
        else:
            database.delete(vote)

        database.commit()
    except SQLAlchemyError as err:
        database.rollback()
        raise err


def qa_comment(
    database: Session, user: schemas.User, text: str, question: int
) -> QuestionComment:
    "Add a comment to a Q&A in the database."
    comment = QuestionComment(
        created=datetime.now(tz=timezone.utc),
        text=text,
        question=question,
        user=user.id,
    )

    try:
        database.add(comment)
    except SQLAlchemyError as err:
        database.rollback()
        raise err

    database.commit()
    database.refresh(comment)
    return comment


def qa_delete(database: Session, question: int) -> None:
    "Remove a Q&A from the database."
    the_qa = database.query(Question).filter(Question.id == question).one_or_none()
    if the_qa is not None:
        database.delete(the_qa)
        database.commit()
