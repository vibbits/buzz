" Handling of connected realtime clients "

import logging
from threading import Lock
from typing import Literal
from uuid import UUID, uuid4 as uuid

from fastapi import WebSocket

from app.authorization import user_from_token
from app.schemas import User

Message = dict[str, str]

log = logging.getLogger(__name__)


class Client:
    id: UUID
    socket: WebSocket
    user: User

    def __init__(self, socket: WebSocket, user: User):
        self.id = uuid()
        self.socket = socket
        self.user = user

    @property
    def name(self) -> str:
        return f"{self.user.first_name} {self.user.last_name}"

    @property
    def role(self) -> Literal["admin"] | Literal["user"]:
        return self.user.role


def connected(client: Client) -> Message:
    return {
        "msg": "connected",
        "id": str(client.id),
        "name": client.name,
    }


def disconnected(client: Client) -> Message:
    return {"msg": "disconnected", "id": str(client.id)}


class ConnectionManager:
    clients: list[Client] = []
    lock: Lock = Lock()

    async def connect(self, socket: WebSocket) -> Client:
        # Wait for a "ready" message
        ready = await socket.receive_json()
        log.info(f"Ready: {ready}")
        # Request the bearer token.
        await socket.send_json({"msg": "auth"})
        token = await socket.receive_json()
        user = user_from_token(token["bearer"])

        client = Client(socket, user)
        await self.broadcast(connected(client))
        log.info(f"connect({client.id}) waiting on lock? {self.lock.locked()}")
        with self.lock:
            self.clients.append(client)

        log.info(f"Client {client.id} added")

        return client

    async def broadcast(self, message: Message):
        log.info(f"broadcast() waiting on lock? {self.lock.locked()}")
        with self.lock:
            for client in self.clients:
                await client.socket.send_json(message)

        log.info("Broadcast sent")

    async def disconnect(self, client: Client):
        log.info(f"disconnect({client.id}) waiting on lock? {self.lock.locked()}")
        with self.lock:
            self.clients.remove(client)

        log.info(f"Client {client.id} removed")

        await self.broadcast(disconnected(client))
