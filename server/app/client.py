" Handling of connected realtime clients "

import logging
from typing import Literal
from uuid import UUID, uuid4 as uuid

from fastapi import WebSocket

from app.authorization import user_from_token
from app.schemas import User

Message = dict[str, str]

log = logging.getLogger(__name__)


class Client:
    "A connected client: tracks useful data for a connected client."
    id: UUID
    socket: WebSocket
    user: User

    def __init__(self, socket: WebSocket, user: User):
        self.id = uuid()
        self.socket = socket
        self.user = user

    @property
    def name(self) -> str:
        "Derive connected users real name."
        return f"{self.user.first_name} {self.user.last_name}"

    @property
    def role(self) -> Literal["admin"] | Literal["user"]:
        "Derive connected users role."
        return self.user.role


def connected(client: Client) -> Message:
    "Construct a message to connected clients that another client has connected."
    return {
        "msg": "connected",
        "id": str(client.id),
        "name": client.name,
    }


def disconnected(client: Client) -> Message:
    "Construct a message to connected clients that a client has disconnected."
    return {"msg": "disconnected", "id": str(client.id)}


class ConnectionManager:
    """
    Tracks all connected clients and provides operations for communicating with connected clients.
    """

    clients: list[Client] = []

    async def connect(self, socket: WebSocket) -> Client:
        """
        Add a client to the list of connected clients.
        Perform startup handshake when a client connects to a WebSocket.
        Return a connected client object or throw an exception.
        """
        # Wait for a "ready" message
        log.info("Waiting on 'ready' message")
        ready = await socket.receive_json()
        log.info("Ready: %s", ready)
        # Request the bearer token.
        log.info("Requesting bearer token")
        await socket.send_json({"msg": "auth"})
        token = await socket.receive_json()
        user = user_from_token(token["bearer"])

        client = Client(socket, user)
        await self.broadcast(connected(client))

        self.clients.append(client)
        log.info("Client %s added: %s (%s)", client.id, client.name, client.role)

        return client

    async def broadcast(self, message: Message):
        """
        Send a message to _all_ connected clients.
        This can throw a `WebSocketDisconnect exception when a client has closed the connection already.
        """
        log.info("broadcast()ing: %s", message)

        for client in self.clients:
            log.debug("Sending to %s", client.id)
            await client.socket.send_json(message)

        log.info("Broadcast sent")

    async def disconnect(self, client: Client):
        """
        Remove a client from the list of connected clients.
        NOTE: This function does _not_ close the websocket connection.
        """
        log.info("disconnect(%s) %s", client.id, client.name)
        self.clients.remove(client)
        log.info("Client %s removed", client.id)

        await self.broadcast(disconnected(client))
