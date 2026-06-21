from __future__ import annotations

import re

from passlib.context import CryptContext

from app.common.exceptions import ValidationException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

PASSWORD_REGEX = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$"


def hash_password(password: str) -> str:
    validate_password_strength(password)
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def validate_password_strength(password: str) -> None:
    if not re.match(PASSWORD_REGEX, password):
        raise ValidationException(
            message=(
                "Password must be at least 8 characters long and contain at least "
                "one uppercase letter, one lowercase letter, and one digit"
            ),
            code="WEAK_PASSWORD",
        )
