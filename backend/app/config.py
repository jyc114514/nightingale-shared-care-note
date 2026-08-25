"""Environment-backed settings for the local Gate A implementation."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the local Gate A implementation."""

    app_env: str = "development"
    database_url: str = "sqlite:///./nightingale.db"
    session_secret: str | None = None
    cookie_secure: bool = False
    session_ttl_minutes: int = 60
    allowed_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    demo_seed_password: str | None = None
    llm_provider: str | None = None
    llm_api_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def allowed_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


settings = Settings()


def get_settings() -> Settings:
    """Return the process settings; tests may override this dependency."""

    return settings
