" Realtime communication between clients "

import asyncio
from json import JSONDecodeError
from uuid import uuid4 as uuid
from uuid import UUID

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app import deps, polls, qa
from app.authorization import user_from_token, AuthorizationError
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

connected_clients: dict[str, Client] = {}


async def broadcast(message: Message):
    for client in connected_clients.values():
        await client.socket.send_json(message)


# Messages


def connected(client: Client) -> Message:
    return {
        "msg": "connected",
        "id": str(client.id),
        "name": client.name,
    }


def disconnected(client: Client) -> Message:
    return {"msg": "disconnected", "id": str(client.id)}


def error_msg(message: str) -> Message:
    return {"msg": "error", "error": message}


def response(message: str, package: dict[str, str]) -> Message:
    return {"msg": message} | package


def conn_info() -> Message:
    return {"clients": str(len(connected_clients))}


# API

dispatch = {
    "new_poll": ("admin", polls.create_new_poll),
    "delete_poll": ("admin", polls.delete_poll),
    "poll_vote": ("user", polls.vote),
    "new_qa": ("user", qa.create_new_discussion),
    "qa_vote": ("user", qa.vote),
}


@router.websocket("/ws")
async def realtime_comms(
    websocket: WebSocket,
    database: Session = Depends(deps.get_db),
):
    await websocket.accept()
    client = None

    try:
        # Wait for a "ready" message
        await websocket.receive_json()
        # First, request the bearer token.
        await websocket.send_json({"msg": "auth"})
        token = await websocket.receive_json()
        user = user_from_token(token["bearer"])

        client = Client(websocket, name=f"{user.first_name} {user.last_name}")
        await broadcast(connected(client))
        connected_clients[str(client.id)] = client

        while True:
            message = await websocket.receive_json()
            (role, fn) = dispatch[message["msg"]]

            if role == "admin" and user.role != "admin":
                await websocket.send_json(error_msg("Forbidden"))
            else:
                await broadcast(
                    response(
                        message["msg"],
                        fn(
                            database,
                            user,
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
            del connected_clients[str(client.id)]
            await broadcast(disconnected(client))
    except (JSONDecodeError, KeyError):
        await websocket.close()
        if client is not None:
            del connected_clients[str(client.id)]
            await broadcast(disconnected(client))
    except AuthorizationError as err:
        await websocket.send_json(error_msg(str(err)))
        await websocket.close()
