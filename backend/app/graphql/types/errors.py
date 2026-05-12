"""Typed GraphQL errors returned by mutation unions."""

import strawberry


@strawberry.type
class AuthError:
    message: str
    code: str = "AUTHENTICATION_REQUIRED"


@strawberry.type
class ForbiddenError:
    message: str
    code: str = "FORBIDDEN"


@strawberry.type
class ValidationError:
    message: str
    code: str = "VALIDATION_ERROR"


@strawberry.type
class NotFoundError:
    message: str
    code: str = "NOT_FOUND"
