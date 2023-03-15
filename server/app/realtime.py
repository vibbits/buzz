" Realtime communication between clients "

from json import JSONDecodeError
from uuid import uuid4 as uuid
from uuid import UUID

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app import deps, polls
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
    "poll_vote": ("user", polls.vote),
}


@router.websocket("/ws")
async def realtime_comms(
    websocket: WebSocket,
    database: Session = Depends(deps.get_db),
    user: User = Depends(deps.current_user),
):
    await websocket.accept()
    client = Client(websocket, name=f"{user.first_name} {user.last_name}")
    await broadcast(connected(client))
    connected_clients[str(client.id)] = client

    try:
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
                            user.id,
                            **{
                                key: value
                                for (key, value) in message.items()
                                if key != "msg"
                            },
                        ),
                    )
                )
    except WebSocketDisconnect:
        del connected_clients[str(client.id)]
        await broadcast(disconnected(client))
    except (JSONDecodeError, KeyError):
        del connected_clients[str(client.id)]
        await websocket.close()
        await broadcast(disconnected(client))


@router.websocket("/debug")
async def realtime_debug(
    websocket: WebSocket,
    database: Session = Depends(deps.get_db),
):
    print("DEBUGGING", flush=True)
    await websocket.accept()
    client = Client(websocket, name=f"debug")
    await broadcast(connected(client))
    connected_clients[str(client.id)] = client

    try:
        while True:
            message = await websocket.receive_json()
            await broadcast(conn_info())
    except WebSocketDisconnect:
        del connected_clients[str(client.id)]
        await broadcast(disconnected(client))
    except (JSONDecodeError, KeyError):
        del connected_clients[str(client.id)]
        await websocket.close()
        await broadcast(disconnected(client))
