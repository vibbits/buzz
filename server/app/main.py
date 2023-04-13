"""
Main entry point
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
import logging
import sqlite3
from urllib.parse import urlparse

import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import auth, database, realtime, state
from app.config import settings

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Restore the database to :memory: on startup, and
    Backup the :memory: database on shutdown.
    See: https://www.sqlite.org/backup.html
    """
    path = "." + urlparse(settings.backup_database_uri).path
    live_database_connection = database.engine.raw_connection().driver_connection

    if ":memory:" in settings.database_uri:
        log.debug("Restoring database from disk...")
        restore = sqlite3.connect(path)
        if live_database_connection is not None:
            restore.backup(target=live_database_connection)

    yield

    if ":memory:" in settings.database_uri:
        log.debug("Saving database to disk...")
        backup = sqlite3.connect(path)
        if live_database_connection is not None:
            live_database_connection.backup(target=backup)


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter()
router.include_router(auth.router, prefix="/auth")
router.include_router(state.router, prefix="/state")
router.include_router(realtime.router)

app.include_router(router)

print("SETTINGS FOR THIS SESSION:")
print(settings.dict())


def main() -> None:
    "Launched with `poetry run start` at server root level"
    uvicorn.run("app.main:app", host="0.0.0.0", reload=True)
