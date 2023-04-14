" Q&A (Discussion or Question) control and response formatting functions "

from sqlalchemy.orm import Session

from app import crud
from app.client import error, Package
from app.schemas import User

Arguments = dict[str, str | int | list[str]]


def create_new_discussion(database: Session, user: User, args: Arguments) -> Package:
    "Create a new Q&A."
    text = args.get("text")
    try:
        if isinstance(text, str):
            discussion = crud.create_new_discussion(database, user, text)
            return {
                "id": discussion.id,
                "text": discussion.text,
                "user": f"{user.first_name} {user.last_name}",
            }
        return error("type mismatch")
    except Exception as err:  # pylint: disable=broad-exception-caught
        return error(str(err))


def vote(database: Session, user: User, args: Arguments) -> Package:
    "Vote on a question."
    question = args.get("qa")
    if isinstance(question, int):
        crud.qa_vote(database, user.id, question)
        votes = crud.qa_votes(database, question)
        return {"qa": question, "count": len(votes)}
    return error("type mismatch")


def comment(database: Session, user: User, args: Arguments) -> Package:
    "Comment on a question."
    text = args.get("text")
    question = args.get("qa")
    try:
        if isinstance(text, str) and isinstance(question, int):
            qa_comment = crud.qa_comment(database, user, text, question)
            return {
                "id": qa_comment.id,
                "qa": qa_comment.question,
                "text": qa_comment.text,
                "user": f"{user.first_name} {user.last_name}",
            }
        return error("type mismatch")
    except Exception as err:  # pylint: disable=broad-exception-caught
        return error(str(err))


def delete(database: Session, _user: User, args: Arguments) -> Package:
    "Delete a whole Q&A."
    question = args.get("qa")
    if isinstance(question, int):
        crud.qa_delete(database, question)
        return {"qa": question}
    return error("type mismatch")
