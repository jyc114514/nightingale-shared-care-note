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

    def validate_runtime_security(self) -> None:
        """Fail closed for unsafe production cookie/session configuration."""

        if self.session_ttl_minutes <= 0:
            raise ValueError("SESSION_TTL_MINUTES must be positive")
        if self.app_env.lower() == "production":
            if not self.cookie_secure:
                raise ValueError("COOKIE_SECURE=true is required when APP_ENV=production")
            if self.session_secret is None or len(self.session_secret) < 32:
                raise ValueError(
                    "SESSION_SECRET with at least 32 characters is required in production"
                )


settings = Settings()


def get_settings() -> Settings:
    """Return the process settings; tests may override this dependency."""

    return settings
