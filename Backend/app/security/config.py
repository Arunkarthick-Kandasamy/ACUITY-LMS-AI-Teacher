from __future__ import annotations

from datetime import timedelta

from app.config import settings as app_settings


class SecuritySettings:
    secret_key: str = app_settings.secret_key
    algorithm: str = app_settings.jwt_algorithm
    access_token_expire: timedelta = timedelta(minutes=app_settings.access_token_expire_minutes)
    refresh_token_expire: timedelta = timedelta(days=app_settings.refresh_token_expire_days)
    password_reset_token_expire: timedelta = timedelta(
        hours=app_settings.password_reset_token_expire_hours
    )


security_settings = SecuritySettings()
