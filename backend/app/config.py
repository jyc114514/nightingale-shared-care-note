"""Environment-backed settings for the Phase 0 scaffold.

The settings object only defines placeholders. No credentials or external service
connections are required by the Phase 0 application.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Optional configuration reserved for later implementation phases."""

    database_url: str | None = None
    session_secret: str | None = None
    llm_provider: str | None = None
    llm_api_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
