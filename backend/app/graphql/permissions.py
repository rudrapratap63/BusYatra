"""
GraphQL RBAC helpers.

Resolvers can call these helpers directly, and future schema fields can reuse
the permission classes with Strawberry's ``permission_classes`` argument.
"""

from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any, ParamSpec, TypeVar, cast

import strawberry
from graphql import GraphQLError
from strawberry.permission import BasePermission

from app.db.models import RoleEnum, User


P = ParamSpec("P")
R = TypeVar("R")


def _role_value(role: RoleEnum | str) -> str:
    return role.value if isinstance(role, RoleEnum) else role


def _allowed_role_values(roles: tuple[RoleEnum | str, ...]) -> set[str]:
    return {_role_value(role) for role in roles}


def get_current_user(info: strawberry.Info) -> User | None:
    return cast(User | None, info.context.get("current_user"))


def is_authenticated(info: strawberry.Info) -> bool:
    return get_current_user(info) is not None


def has_role(user: User | None, *roles: RoleEnum | str) -> bool:
    if not user or not user.role:
        return False
    return user.role.value in _allowed_role_values(roles)


def require_authenticated(info: strawberry.Info) -> User:
    current_user = get_current_user(info)
    if not current_user:
        raise GraphQLError("Authentication required")
    return current_user


def require_role(info: strawberry.Info, *roles: RoleEnum | str) -> User:
    current_user = require_authenticated(info)
    if not has_role(current_user, *roles):
        allowed = ", ".join(sorted(_allowed_role_values(roles)))
        raise GraphQLError(f"Forbidden: requires one of these roles: {allowed}")
    return current_user


def require_any_role(
    *roles: RoleEnum | str,
) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
    """
    Decorator form for async resolvers.

    Example:
        @strawberry.field
        @require_any_role(RoleEnum.admin)
        async def users(...)
    """

    def decorator(resolver: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        @wraps(resolver)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            info = _find_info(args, kwargs)
            require_role(info, *roles)
            return await resolver(*args, **kwargs)

        return wrapper

    return decorator


def _find_info(args: tuple[Any, ...], kwargs: dict[str, Any]) -> strawberry.Info:
    maybe_info = kwargs.get("info")
    if isinstance(maybe_info, strawberry.Info):
        return maybe_info

    for arg in args:
        if isinstance(arg, strawberry.Info):
            return arg

    raise RuntimeError("RBAC decorator could not find strawberry.Info")


class IsAuthenticated(BasePermission):
    message = "Authentication required"

    async def has_permission(
        self,
        source: Any,
        info: strawberry.Info,
        **kwargs: Any,
    ) -> bool:
        return is_authenticated(info)


def role_permission(*roles: RoleEnum | str) -> type[BasePermission]:
    allowed_roles = tuple(roles)
    allowed_display = ", ".join(sorted(_allowed_role_values(allowed_roles)))

    class HasRole(BasePermission):
        message = f"Forbidden: requires one of these roles: {allowed_display}"

        async def has_permission(
            self,
            source: Any,
            info: strawberry.Info,
            **kwargs: Any,
        ) -> bool:
            return has_role(get_current_user(info), *allowed_roles)

    return HasRole
