from __future__ import annotations

import json
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

VALID_ENVIRONMENTS: frozenset = frozenset({"development", "staging", "production"})


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    environment: Annotated[str, Field(default="development")]
    debug: Annotated[bool, Field(default=True)]
    log_level: Annotated[str, Field(default="DEBUG")]

    api_prefix: Annotated[str, Field(default="/api/v1")]
    app_name: Annotated[str, Field(default="Acuity LMS AI")]
    app_version: Annotated[str, Field(default="0.1.0")]

    database_url: Annotated[
        str, Field(default="postgresql+asyncpg://acuity:acuity@localhost:5432/acuity_lms")
    ]

    cors_origins: Annotated[list[str], Field(default=["http://localhost:3000", "http://localhost:5173"])]

    # -----------------------------------------------------------------------
    # Security
    # -----------------------------------------------------------------------
    secret_key: Annotated[str, Field(default="change-me-in-production-use-a-real-secret")]
    jwt_algorithm: Annotated[str, Field(default="HS256")]
    access_token_expire_minutes: Annotated[int, Field(default=30)]
    refresh_token_expire_days: Annotated[int, Field(default=7)]
    password_reset_token_expire_hours: Annotated[int, Field(default=1)]

    # -----------------------------------------------------------------------
    # AI
    # -----------------------------------------------------------------------
    gemini_api_key: Annotated[str, Field(default="")]
    gemini_model: Annotated[str, Field(default="gemini-1.5-pro")]

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        if v not in VALID_ENVIRONMENTS:
            valid = ", ".join(sorted(VALID_ENVIRONMENTS))
            msg = f"Invalid environment '{v}'. Must be one of: {valid}"
            raise ValueError(msg)
        return v

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v.startswith("postgresql+asyncpg://"):
            msg = "DATABASE_URL must use asyncpg driver (postgresql+asyncpg://)"
            raise ValueError(msg)
        return v

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def is_staging(self) -> bool:
        return self.environment == "staging"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def cors_origins_list(self) -> list[str]:
        if isinstance(self.cors_origins, str):
            return json.loads(self.cors_origins)
        return list(self.cors_origins)


settings = Settings()
