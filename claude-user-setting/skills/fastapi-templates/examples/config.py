# Pattern 6: Configuration (YAML + Pydantic v2 Settings)
# - Environment-aware config loading from YAML files
# - Nested Pydantic models for grouped settings
# - Module-level singleton pattern
#
# Directory structure:
#   app/core/config/
#   ├── __init__.py              # Exports settings singleton
#   ├── config.py                # Settings class & loading logic
#   ├── config.example.yaml      # Template for all environments
#   ├── config.local.yaml        # Local development overrides
#   ├── config.dev.yaml          # Dev environment
#   └── config.live.yaml         # Production environment

# -------------------------------------------------------------------
# core/config/config.py
# -------------------------------------------------------------------
import os
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    YamlConfigSettingsSource,
)

Env = Literal["local", "dev", "qa", "live"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

_CONFIG_DIR = Path(__file__).resolve().parent
_ENV: Env = os.getenv("ENV", "local")
_CONFIG_PATH = _CONFIG_DIR / f"config.{_ENV}.yaml"


class EmbeddingConfig(BaseModel):
    """Embedding API related settings."""

    api_base_url: str = Field(
        default="http://localhost:8080",
        description="Base URL of the embedding API.",
        pattern=r"^https?://.+",
    )


class Settings(BaseSettings):
    """Application settings resolved from YAML config files.

    Priority (highest -> lowest):
      1. Environment variables
      2. YAML config file (config.{ENV}.yaml)
      3. Field defaults
    """

    model_config = ConfigDict(
        yaml_file=str(_CONFIG_PATH),
    )

    env: Env = Field(default=_ENV, description="Runtime environment name.")
    log_level: LogLevel = Field(default="INFO", description="Python logging level.")
    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Override source priority: env vars -> YAML -> defaults."""
        if not _CONFIG_PATH.is_file():
            raise FileNotFoundError(
                f"Config file not found: {_CONFIG_PATH}\n"
                f"Available environments: local, dev, qa, live"
            )
        return (
            init_settings,
            env_settings,
            YamlConfigSettingsSource(settings_cls, yaml_file=_CONFIG_PATH),
            file_secret_settings,
        )


# Singleton — instantiated once at module load
settings = Settings()


# -------------------------------------------------------------------
# core/config/config.local.yaml (YAML example)
# -------------------------------------------------------------------
# log_level: "DEBUG"
#
# embedding:
#   api_base_url: "http://localhost:8080"


# -------------------------------------------------------------------
# core/config/__init__.py
# -------------------------------------------------------------------
# from app.core.config.config import settings
#
# __all__ = ["settings"]


# -------------------------------------------------------------------
# Usage: inject config via lifespan (main.py)
# -------------------------------------------------------------------
# from app.core.config import settings
#
# @asynccontextmanager
# async def lifespan(app: FastAPI) -> AsyncIterator[None]:
#     """Manage application startup and shutdown resources."""
#     http_client = httpx.AsyncClient(base_url=settings.embedding.api_base_url)
#     app.state.embedding_client = EmbeddingClient(http_client=http_client)
#     yield
#     await http_client.aclose()
#
# def create_app() -> FastAPI:
#     logger.info(f"Starting application in {settings.env} environment")
#     app = FastAPI(title="My Service", lifespan=lifespan)
#     return app


# -------------------------------------------------------------------
# Usage: configure logger from settings (core/logging/logger.py)
# -------------------------------------------------------------------
# from app.core.config import settings
#
# def _setup_logger() -> logging.Logger:
#     log = logging.getLogger("my-service")
#     log.setLevel(getattr(logging, settings.log_level, logging.INFO))
#
#     if settings.env == "local":
#         handler.setFormatter(ColoredConsoleFormatter())   # Human-readable
#     else:
#         handler.setFormatter(JsonFormatter())             # Structured JSON
#     return log
#
# logger = _setup_logger()
