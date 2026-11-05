from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    # An absolute .env path keeps the configuration independent of the
    # working directory, like the default database location.
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = Field(
        default=f"sqlite:///{(PROJECT_ROOT / 'documents.db').as_posix()}",
        min_length=1,
    )


settings = Settings()
