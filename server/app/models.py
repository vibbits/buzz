" Database models: declarative SQL table descriptions "
# pylint: disable=too-few-public-methods

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    "Base class for SQLAlchemy."


# Authentication


class User(Base):
    "Table recording users."
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True
    )  # Same as the oidc subject
    created = mapped_column(DateTime, nullable=False)
    first_name = mapped_column(String)
    last_name = mapped_column(String)
    role = mapped_column(String, nullable=False)
    active = mapped_column(DateTime)
    image = mapped_column(String)


# Polls


class Poll(Base):
    "Table for recording polls."
    __tablename__ = "polls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created = mapped_column(DateTime, nullable=False)
    title = mapped_column(String, nullable=False)
    description = mapped_column(String)
    options: Mapped[list["PollOption"]] = relationship(
        "PollOption", cascade="all, delete"
    )
    votes: Mapped[list["PollVote"]] = relationship("PollVote", cascade="all, delete")


class PollOption(Base):
    "Table for recording poll options."
    __tablename__ = "poll_options"

    id = mapped_column(Integer, primary_key=True)
    poll = mapped_column(Integer, ForeignKey("polls.id"), nullable=False)
    text = mapped_column(String, nullable=False)


class PollVote(Base):
    "Table for recording votes on polls."
    __tablename__ = "poll_votes"
    __table_args__ = (
        UniqueConstraint("option", "poll", "user", name="one_vote_per_user_per_option"),
    )

    id = mapped_column(Integer, primary_key=True)
    option = mapped_column(Integer, ForeignKey("poll_options.id"), nullable=False)
    poll = mapped_column(Integer, ForeignKey("polls.id"), nullable=False)
    user = mapped_column(Integer, ForeignKey("users.id"), nullable=False)


# Questions


class Question(Base):
    "Q&A questions."
    __tablename__ = "questions"

    id = mapped_column(Integer, primary_key=True)
    text = mapped_column(String, nullable=False)
    created = mapped_column(DateTime, nullable=False)
    user = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    asker: Mapped[User] = relationship("User")
    votes: Mapped[list["QuestionVote"]] = relationship(
        "QuestionVote",
        cascade="all, delete",
    )
    comments: Mapped[list["QuestionComment"]] = relationship(
        "QuestionComment",
        cascade="all, delete",
        order_by="desc(QuestionComment.created)",
    )


class QuestionComment(Base):
    "Comments or responses to questions"
    __tablename__ = "question_comments"

    id = mapped_column(Integer, primary_key=True)
    created = mapped_column(DateTime, nullable=False)
    text = mapped_column(String, nullable=False)
    question = mapped_column(Integer, ForeignKey("questions.id"), nullable=False)
    user = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    commenter: Mapped[User] = relationship("User")


class QuestionVote(Base):
    "Table for recording votes on questions."
    __tablename__ = "question_votes"
    __table_args__ = (UniqueConstraint("question", "user", name="one_vote_per_user"),)

    id = mapped_column(Integer, primary_key=True)
    question = mapped_column(Integer, ForeignKey("questions.id"), nullable=False)
    user = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
