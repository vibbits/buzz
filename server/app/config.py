" Application runtime configuration "

import secrets

from pydantic import BaseSettings


class Settings(BaseSettings):
    client_secret: str

    api_secret: str = secrets.token_urlsafe(32)
    api_token_expire: int = 12 * 60  # 12 hours in minutes


settings = Settings()
