" Realtime communication between clients "

from json import JSONDecodeError
import logging
from uuid import uuid4 as uuid
from uuid import UUID

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app import deps, polls, qa
from app.authorization import AuthorizationError
from app.client import ConnectionManager


# Types

Message = dict[str, str]


router = APIRouter()

manager = ConnectionManager()

log = logging.getLogger(__name__)


# Messages


def error_msg(message: str) -> Message:
    return {"msg": "error", "error": message}


def response(message: str, package: dict[str, str]) -> Message:
    return {"msg": message} | package


# API

dispatch = {
    "ping": ("user", lambda: {"msg": "pong"}),
    "new_poll": ("admin", polls.create_new_poll),
    "delete_poll": ("admin", polls.delete_poll),
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
):
    await websocket.accept()
    client = None
    log.info("New websocket connection on /ws")

    try:
        client = await manager.connect(websocket)
        log.info(f"Connected client: {client.id}")

        while True:
            message = await websocket.receive_json()
            (role, handler) = dispatch[message["msg"]]
            log.info(f"Received (from: {client.id}): {message}")

            if message["msg"] == "ping":
                await websocket.send_json(handler())
            elif role == "admin" and client.role != "admin":
                await websocket.send_json(error_msg("Forbidden"))
            else:
                await manager.broadcast(
                    response(
                        message["msg"],
                        handler(
                            database,
                            client.user,
                            **{
                                key: value
                                for (key, value) in message.items()
                                if key != "msg"
                            },
                        ),
                    )
                )
    except WebSocketDisconnect as dc:
        log.warn(f"WebSocketDisconnect: {dc}")
        if client is not None:
            log.info(f"Disconnecting client {client.id}")
            await manager.disconnect(client)

    except (JSONDecodeError, KeyError) as err:
        log.error(f"Error: {err}")
        await websocket.send_json(error_msg(str(err)))
        await websocket.close()
        if client is not None:
            await manager.disconnect(client)

    except AuthorizationError as err:
        log.error(f"Authorization error: {err}")
        await websocket.send_json(error_msg(str(err)))
        await websocket.close()
