" Application runtime configuration "
# pylint: disable=too-few-public-methods

import secrets

from pydantic import BaseSettings


class Settings(BaseSettings):
    "Application runtime configuration."
    client_secret: str = "????"

    api_secret: str = secrets.token_urlsafe(32)
    api_token_expire: int = 12 * 60  # 12 hours in minutes

    database_uri: str = "sqlite:///buzz.sqlite"


settings = Settings()
