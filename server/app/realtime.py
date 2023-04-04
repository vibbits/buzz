" Realtime communication between clients "

import asyncio
from json import JSONDecodeError
from uuid import uuid4 as uuid
from uuid import UUID

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app import deps, polls, qa
from app.authorization import user_from_token, AuthorizationError
from app.client import ConnectionManager
from app.schemas import User


# Types

Message = dict[str, str]


class Client:
    id: UUID
    socket: WebSocket
    name: str

    def __init__(self, socket: WebSocket, name: str):
        self.id = uuid()
        self.socket = socket
        self.name = name


router = APIRouter()

manager = ConnectionManager()


# Messages


def error_msg(message: str) -> Message:
    return {"msg": "error", "error": message}


def response(message: str, package: dict[str, str]) -> Message:
    return {"msg": message} | package


# API

dispatch = {
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

    try:
        client = await manager.connect(websocket)

        while True:
            message = await websocket.receive_json()
            (role, fn) = dispatch[message["msg"]]

            if role == "admin" and client.role != "admin":
                await websocket.send_json(error_msg("Forbidden"))
            else:
                await manager.broadcast(
                    response(
                        message["msg"],
                        fn(
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
    except WebSocketDisconnect:
        if client is not None:
            manager.disconnect(client)

    except (JSONDecodeError, KeyError):
        await websocket.close()
        if client is not None:
            manager.disconnect(client)
    except AuthorizationError as err:
        await websocket.send_json(error_msg(str(err)))
        await websocket.close()
