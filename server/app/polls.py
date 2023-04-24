" Poll control functions and HTTP API "

from sqlalchemy.orm import Session

from app import crud
from app.client import error, Package
from app.schemas import User

Arguments = dict[str, str | int | list[str]]


def create_new_poll(
    database: Session,
    _user: User,
    args: Arguments,
) -> Package:
    "Create a new poll in the database and format a reponse."
    title = args.get("title")
    description = args.get("description")
    hidden = args.get("hidden")
    options = args.get("options")

    try:
        if (
            isinstance(title, str)
            and isinstance(description, str)
            and isinstance(options, list)
            and isinstance(hidden, bool)
            and all(isinstance(option, str) for option in options)
        ):
            poll = crud.create_new_poll(database, title, description, hidden, options)
            return {
                "id": poll.id,
                "title": poll.title,
                "description": poll.description,
                "hidden": poll.hidden,
                "options": [(opt.text, opt.id) for opt in poll.options],
            }

        return error("type mismatch")
    except Exception as err:  # pylint: disable=broad-exception-caught
        return error(str(err))


def delete_poll(database: Session, _user: User, args: Arguments) -> Package:
    "Remove a poll from the database and format a response."
    poll_id = args.get("poll_id")

    if isinstance(poll_id, int):
        crud.delete_poll(database, poll_id)
        return {"poll_id": poll_id}

    return error("type mismatch")

def hide_poll(database: Session, _user: User, args: Arguments) -> Package:
    
    poll_id = args.get("poll_id")

    if isinstance(poll_id, int):
        crud.hide_poll(database, poll_id)
        return {"poll_id": poll_id}

    return error("type mismatch")

    
def show_poll(database: Session, _user: User, args: Arguments) -> Package:
    poll_id = args.get("poll_id")

    if isinstance(poll_id, int):
        crud.show_poll(database, poll_id)
        return {"poll_id": poll_id}

    return error("type mismatch")


def vote(database: Session, user: User, args: Arguments) -> Package:
    "Add a vote to the database and format a response."
    poll = args.get("poll")
    option = args.get("option")
    if isinstance(poll, int) and isinstance(option, int):
        try:
            crud.poll_vote(database, user.id, poll, option)
            votes = crud.poll_votes(database, poll, option)
            return {"poll": poll, "option": option, "count": len(votes)}
        except Exception as err:  # pylint: disable=broad-exception-caught
            return error(f"Recording vote: {err}")

    return error("type mismatch")
