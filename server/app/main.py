"""
Main entry point
"""

import uvicorn
from fastapi import APIRouter, FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from app import auth, polls, realtime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter()
router.include_router(auth.router, prefix="/auth")
router.include_router(polls.router, prefix="/poll")
router.include_router(realtime.router)

app.include_router(router)


def main() -> None:
    "Launched with `poetry run start` at server root level"
    uvicorn.run("app.main:app", host="0.0.0.0", reload=True)
