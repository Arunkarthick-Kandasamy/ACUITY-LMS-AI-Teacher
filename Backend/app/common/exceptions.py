from __future__ import annotations


class AppException(Exception):
    status_code: int = 500
    code: str = "INTERNAL_ERROR"
    message: str = "An unexpected error occurred"
    details: list | None = None

    def __init__(
        self,
        message: str | None = None,
        code: str | None = None,
        details: list | None = None,
    ) -> None:
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code
        self.details = details
        super().__init__(self.message)


class NotFoundException(AppException):
    status_code = 404
    code = "NOT_FOUND"
    message = "Resource not found"


class ValidationException(AppException):
    status_code = 400
    code = "VALIDATION_ERROR"
    message = "Validation failed"


class UnauthorizedException(AppException):
    status_code = 401
    code = "UNAUTHORIZED"
    message = "Not authenticated"


class ForbiddenException(AppException):
    status_code = 403
    code = "FORBIDDEN"
    message = "Not authorized"


class ConflictException(AppException):
    status_code = 409
    code = "CONFLICT"
    message = "Resource conflict"
