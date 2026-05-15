"""GraphQL Mutations - trip scheduling and trip seat generation."""

import uuid
from datetime import datetime
from typing import Annotated, Optional, Union

import strawberry
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import models
from app.graphql.permissions import has_role
from app.graphql.queries.trip import _map_trip
from app.graphql.types.errors import AuthError, ForbiddenError, NotFoundError, ValidationError
from app.graphql.types.trip import TripType


@strawberry.input
class CreateTripInput:
    bus_id: strawberry.ID
    route_id: strawberry.ID
    departure_time: str
    arrival_time: Optional[str] = None
    trip_status: str = "scheduled"


TripMutationResult = Annotated[
    Union[TripType, AuthError, ForbiddenError, NotFoundError, ValidationError],
    strawberry.union("TripMutationResult"),
]


@strawberry.type
class TripMutation:
    @strawberry.mutation(description="Schedule a trip and generate trip seats from the bus layout.")
    async def create_trip(
        self,
        info: strawberry.Info,
        input: CreateTripInput,
    ) -> TripMutationResult:
        db: AsyncSession = info.context["db"]
        org_result = await _get_owned_org_for_trip_mutation(db, info)
        if isinstance(org_result, (AuthError, ForbiddenError, ValidationError)):
            return org_result
        org = org_result

        try:
            bus_id = uuid.UUID(str(input.bus_id))
            route_id = uuid.UUID(str(input.route_id))
        except ValueError:
            return ValidationError(message="Invalid bus or route ID")

        departure_time = _parse_datetime(input.departure_time)
        if not departure_time:
            return ValidationError(message="Invalid departure time")
        arrival_time = _parse_datetime(input.arrival_time) if input.arrival_time else None
        if input.arrival_time and not arrival_time:
            return ValidationError(message="Invalid arrival time")
        if arrival_time and arrival_time <= departure_time:
            return ValidationError(message="Arrival time must be after departure time")

        try:
            trip_status = models.TripStatusEnum(input.trip_status)
        except ValueError:
            return ValidationError(message="Invalid trip status")

        bus_result = await db.execute(
            select(models.Bus)
            .where(models.Bus.id == bus_id, models.Bus.org_id == org.id)
            .options(selectinload(models.Bus.seats))
        )
        bus = bus_result.scalar_one_or_none()
        if not bus:
            return NotFoundError(message="Bus not found")
        if bus.bus_status != models.BusStatusEnum.active:
            return ValidationError(message="Only active buses can be scheduled")
        if not bus.seats:
            return ValidationError(message="Bus must have seats before scheduling a trip")

        route_result = await db.execute(
            select(models.Route).where(
                models.Route.id == route_id,
                models.Route.org_id == org.id,
            )
        )
        route = route_result.scalar_one_or_none()
        if not route:
            return NotFoundError(message="Route not found")
        if route.status != models.RouteStatusEnum.active:
            return ValidationError(message="Only active routes can be scheduled")

        trip = models.Trip(
            org_id=org.id,
            bus_id=bus.id,
            route_id=route.id,
            departure_time=departure_time,
            arrival_time=arrival_time,
            trip_status=trip_status,
        )
        db.add(trip)
        await db.flush()

        for seat in bus.seats:
            db.add(
                models.TripSeat(
                    trip_id=trip.id,
                    seat_id=seat.id,
                    status=(
                        models.SeatStatusEnum.available
                        if seat.is_available
                        else models.SeatStatusEnum.blocked
                    ),
                )
            )

        await db.commit()
        return await _load_and_map_trip(db, trip.id)


async def _get_owned_org_for_trip_mutation(
    db: AsyncSession,
    info: strawberry.Info,
) -> models.Org | AuthError | ForbiddenError | ValidationError:
    current_user: models.User | None = info.context.get("current_user")
    if not current_user:
        return AuthError(message="Authentication required")
    if not has_role(current_user, models.RoleEnum.org_admin, models.RoleEnum.admin):
        return ForbiddenError(message="Only organization admins can schedule trips")
    if has_role(current_user, models.RoleEnum.admin):
        return ValidationError(message="Platform admins must act through an organization owner account")

    result = await db.execute(
        select(models.Org).where(models.Org.owner_user_id == current_user.id)
    )
    org = result.scalar_one_or_none()
    if not org:
        return ValidationError(message="Current user does not own an organization")
    if org.approval_status == models.OrgApprovalEnum.suspended:
        return ForbiddenError(message="Suspended organizations cannot schedule trips")
    return org


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = f"{normalized[:-1]}+00:00"
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


async def _load_and_map_trip(db: AsyncSession, trip_id: uuid.UUID) -> TripType:
    result = await db.execute(
        select(models.Trip)
        .where(models.Trip.id == trip_id)
        .options(
            selectinload(models.Trip.bus),
            selectinload(models.Trip.route).selectinload(models.Route.source_stop),
            selectinload(models.Trip.route).selectinload(models.Route.dest_stop),
            selectinload(models.Trip.route)
            .selectinload(models.Route.route_stops)
            .selectinload(models.RouteStop.stop),
            selectinload(models.Trip.trip_operator),
        )
    )
    return _map_trip(result.scalar_one())
