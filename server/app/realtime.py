" Realtime communication between clients "

from json import JSONDecodeError
import logging
from typing import Callable, Literal

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app import deps, polls, qa
from app.authorization import AuthorizationError
from app.client import ConnectionManager, Package, error, response
from app.schemas import User


# Types


router = APIRouter()

manager = ConnectionManager()

log = logging.getLogger(__name__)


# API

Arguments = dict[str, str | int | list[str]]

HandlerFn = Callable[[Session, User, Arguments], Package]


def pong_response(_database: Session, _user: User, _args: Arguments) -> Package:
    "Placeholder."
    return {}


dispatch: dict[
    str,
    tuple[Literal["user", "admin"], HandlerFn],
] = {
    "ping": ("user", pong_response),
    "new_poll": ("admin", polls.create_new_poll),
    "delete_poll": ("admin", polls.delete_poll),
    "poll_hide": ("admin", polls.hide_poll),
    "poll_show": ("admin", polls.show_poll),
    "poll_vote": ("user", polls.vote),
    "new_qa": ("user", qa.create_new_discussion),
    "qa_vote": ("user", qa.vote),
    "qa_comment": ("user", qa.comment),
    "qa_delete": ("admin", qa.delete),
}


@router.websocket("/ws")
async def realtime_comms(
    websocket: WebSocket,
    database: Session = Depends(deps.get_db),
) -> None:
    "Handle all realtime communication through the websocket."
    await websocket.accept()
    client = None
    log.info("New websocket connection on /ws")

    try:
        client = await manager.connect(websocket)
        log.info("Connected client: %s", client.uid)

        while True:
            message = await websocket.receive_json()
            (role, handler) = dispatch[message["msg"]]
            log.info("Received (from: %s): %s", client.uid, message)

            if message["msg"] == "ping":
                await websocket.send_json({"msg": "pong"})
            elif role == "admin" and client.role != "admin":
                await websocket.send_json(error("Forbidden"))
            else:
                await manager.broadcast(
                    response(
                        message["msg"],
                        handler(
                            database,
                            client.user,
                            {
                                key: value
                                for (key, value) in message.items()
                                if key != "msg"
                            },
                        ),
                    )
                )
    except WebSocketDisconnect as reason:
        log.warning("WebSocketDisconnect: %s", str(reason))
        if client is not None:
            log.info("Disconnecting client %s", client.uid)
            await manager.disconnect(client)

    except (JSONDecodeError, KeyError) as err:
        log.error("Error: %s", err)
        await websocket.send_json(error(str(err)))
        await websocket.close()
        if client is not None:
            await manager.disconnect(client)

    except AuthorizationError as err:
        log.error("Authorization error: %s", err)
        await websocket.send_json(error(str(err)))
        await websocket.close()
