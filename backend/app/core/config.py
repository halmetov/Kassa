from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://postgres:123@localhost:5432/kassa_db"

    jwt_secret_key: str = "kassa_project"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    refresh_token_expire_minutes: int = 60 * 24 * 7
    media_root: str = "app/static/uploads"
    vite_host: str | None = None
    vite_port: int | None = None

    environment: str = "dev"
    auto_run_migrations: bool = True
    autogenerate_migrations: bool | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def should_autogenerate_migrations(self) -> bool:
        if self.autogenerate_migrations is not None:
            return self.autogenerate_migrations
        return self.environment.lower() in {"dev", "development"}

    @property
    def project_root(self) -> Path:
        return Path(__file__).resolve().parents[2]

    @property
    def media_root_path(self) -> Path:
        media_root = Path(self.media_root)
        if not media_root.is_absolute():
            media_root = self.project_root / media_root
        return media_root


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
