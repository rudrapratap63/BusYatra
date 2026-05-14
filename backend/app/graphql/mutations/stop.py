"""GraphQL Mutations - shared stop catalog CRUD."""

import uuid
from typing import Annotated, Optional, Union

import strawberry
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import models
from app.graphql.permissions import has_role
from app.graphql.queries.trip import _map_stop
from app.graphql.types.errors import AuthError, ForbiddenError, NotFoundError, ValidationError
from app.graphql.types.route import StopType


@strawberry.input
class AddStopInput:
    name: str
    city: str
    state: Optional[str] = None


@strawberry.input
class UpdateStopInput:
    stop_id: strawberry.ID
    name: Optional[str] = strawberry.UNSET
    city: Optional[str] = strawberry.UNSET
    state: Optional[str] = strawberry.UNSET


StopMutationResult = Annotated[
    Union[StopType, AuthError, ForbiddenError, NotFoundError, ValidationError],
    strawberry.union("StopMutationResult"),
]


@strawberry.type
class StopMutation:
    @strawberry.mutation(description="Add a shared stop to the global stop catalog.")
    async def add_stop(
        self,
        info: strawberry.Info,
        input: AddStopInput,
    ) -> StopMutationResult:
        db: AsyncSession = info.context["db"]
        current_user: models.User | None = info.context.get("current_user")
        if not current_user:
            return AuthError(message="Authentication required")
        if not has_role(current_user, models.RoleEnum.org_admin, models.RoleEnum.admin):
            return ForbiddenError(message="Only admins can manage stops")

        name = _normalize_text(input.name)
        city = _normalize_text(input.city)
        state = _normalize_text(input.state)
        validation_error = _validate_stop_fields(name=name, city=city)
        if validation_error:
            return validation_error

        existing_result = await db.execute(
            select(models.Stop).where(
                models.Stop.name.ilike(name),
                models.Stop.city.ilike(city),
                models.Stop.state.is_(None) if state is None else models.Stop.state.ilike(state),
            )
        )
        if existing_result.scalar_one_or_none():
            return ValidationError(message="Stop already exists")

        stop = models.Stop(name=name, city=city, state=state)
        db.add(stop)
        await db.commit()
        await db.refresh(stop)
        return _map_stop(stop)

    @strawberry.mutation(description="Update a shared stop in the global stop catalog.")
    async def update_stop(
        self,
        info: strawberry.Info,
        input: UpdateStopInput,
    ) -> StopMutationResult:
        db: AsyncSession = info.context["db"]
        current_user: models.User | None = info.context.get("current_user")
        if not current_user:
            return AuthError(message="Authentication required")
        if not has_role(current_user, models.RoleEnum.org_admin, models.RoleEnum.admin):
            return ForbiddenError(message="Only admins can manage stops")

        try:
            stop_id = uuid.UUID(str(input.stop_id))
        except ValueError:
            return ValidationError(message="Invalid stop ID")

        result = await db.execute(select(models.Stop).where(models.Stop.id == stop_id))
        stop = result.scalar_one_or_none()
        if not stop:
            return NotFoundError(message="Stop not found")

        if input.name is not strawberry.UNSET:
            stop.name = _normalize_text(input.name)
        if input.city is not strawberry.UNSET:
            stop.city = _normalize_text(input.city)
        if input.state is not strawberry.UNSET:
            stop.state = _normalize_text(input.state)

        validation_error = _validate_stop_fields(name=stop.name, city=stop.city)
        if validation_error:
            return validation_error

        existing_result = await db.execute(
            select(models.Stop).where(
                models.Stop.id != stop.id,
                models.Stop.name.ilike(stop.name),
                models.Stop.city.ilike(stop.city),
                models.Stop.state.is_(None)
                if stop.state is None
                else models.Stop.state.ilike(stop.state),
            )
        )
        if existing_result.scalar_one_or_none():
            return ValidationError(message="Stop already exists")

        db.add(stop)
        await db.commit()
        await db.refresh(stop)
        return _map_stop(stop)


def _normalize_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = " ".join(value.strip().split())
    return normalized or None


def _validate_stop_fields(name: str | None, city: str | None) -> ValidationError | None:
    if not name:
        return ValidationError(message="Stop name is required")
    if not city:
        return ValidationError(message="Stop city is required")
    if len(name) > 120:
        return ValidationError(message="Stop name must be 120 characters or fewer")
    if len(city) > 120:
        return ValidationError(message="Stop city must be 120 characters or fewer")
    return None
