"""GraphQL Mutations - route, route stop, and boarding point CRUD."""

import uuid
from typing import Annotated, Optional, Union

import strawberry
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import models
from app.graphql.permissions import has_role
from app.graphql.queries.booking import _map_boarding_point
from app.graphql.queries.trip import _map_route_stop, _map_stop
from app.graphql.types.errors import AuthError, ForbiddenError, NotFoundError, ValidationError
from app.graphql.types.route import BoardingPointType, RouteType


@strawberry.input
class CreateRouteInput:
    source_stop_id: strawberry.ID
    dest_stop_id: strawberry.ID
    status: Optional[str] = "active"


@strawberry.input
class RouteStopInput:
    stop_id: strawberry.ID
    sequence_order: int
    arrival_offset: Optional[int] = None
    departure_offset: Optional[int] = None


@strawberry.input
class AddRouteStopsInput:
    route_id: strawberry.ID
    stops: list[RouteStopInput]


@strawberry.input
class SetRouteStatusInput:
    route_id: strawberry.ID
    status: str


@strawberry.input
class AddBoardingPointInput:
    route_id: strawberry.ID
    stop_id: strawberry.ID
    name: str
    type: str = "both"


RouteMutationResult = Annotated[
    Union[RouteType, AuthError, ForbiddenError, NotFoundError, ValidationError],
    strawberry.union("RouteMutationResult"),
]


BoardingPointMutationResult = Annotated[
    Union[BoardingPointType, AuthError, ForbiddenError, NotFoundError, ValidationError],
    strawberry.union("BoardingPointMutationResult"),
]


@strawberry.type
class RouteMutation:
    @strawberry.mutation(description="Create an organization route between two shared stops.")
    async def create_route(
        self,
        info: strawberry.Info,
        input: CreateRouteInput,
    ) -> RouteMutationResult:
        db: AsyncSession = info.context["db"]
        org_result = await _get_owned_org_for_route_mutation(db, info)
        if isinstance(org_result, (AuthError, ForbiddenError, ValidationError)):
            return org_result
        org = org_result

        try:
            source_stop_id = uuid.UUID(str(input.source_stop_id))
            dest_stop_id = uuid.UUID(str(input.dest_stop_id))
        except ValueError:
            return ValidationError(message="Invalid source or destination stop ID")
        if source_stop_id == dest_stop_id:
            return ValidationError(message="Source and destination stops must be different")

        source_stop, dest_stop = await _get_two_stops(db, source_stop_id, dest_stop_id)
        if not source_stop:
            return NotFoundError(message="Source stop not found")
        if not dest_stop:
            return NotFoundError(message="Destination stop not found")

        try:
            status = models.RouteStatusEnum(input.status or models.RouteStatusEnum.active.value)
        except ValueError:
            return ValidationError(message="Invalid route status")

        route = models.Route(
            org_id=org.id,
            source_stop_id=source_stop.id,
            dest_stop_id=dest_stop.id,
            status=status,
        )
        db.add(route)
        await db.commit()
        return await _load_and_map_route(db, route.id)

    @strawberry.mutation(description="Add ordered stops to a route with timing offsets in minutes.")
    async def add_route_stops(
        self,
        info: strawberry.Info,
        input: AddRouteStopsInput,
    ) -> RouteMutationResult:
        db: AsyncSession = info.context["db"]
        route_result = await _get_owned_route(db, info, input.route_id)
        if isinstance(route_result, (AuthError, ForbiddenError, NotFoundError, ValidationError)):
            return route_result
        route = route_result

        validation_error = _validate_route_stop_inputs(input.stops)
        if validation_error:
            return validation_error

        stop_ids = [uuid.UUID(str(stop_input.stop_id)) for stop_input in input.stops]
        stops_result = await db.execute(select(models.Stop).where(models.Stop.id.in_(stop_ids)))
        stops_by_id = {stop.id: stop for stop in stops_result.scalars().all()}
        missing_stop_ids = [stop_id for stop_id in stop_ids if stop_id not in stops_by_id]
        if missing_stop_ids:
            return NotFoundError(message="One or more route stops were not found")

        sequence_orders = [stop_input.sequence_order for stop_input in input.stops]
        existing_sequence_result = await db.execute(
            select(models.RouteStop.sequence_order).where(
                models.RouteStop.route_id == route.id,
                models.RouteStop.sequence_order.in_(sequence_orders),
            )
        )
        if existing_sequence_result.scalars().first() is not None:
            return ValidationError(message="Route stop sequence already exists")

        existing_stop_result = await db.execute(
            select(models.RouteStop.stop_id).where(
                models.RouteStop.route_id == route.id,
                models.RouteStop.stop_id.in_(stop_ids),
            )
        )
        if existing_stop_result.scalars().first() is not None:
            return ValidationError(message="A stop can only appear once on a route")

        for stop_input in input.stops:
            db.add(
                models.RouteStop(
                    route_id=route.id,
                    stop_id=uuid.UUID(str(stop_input.stop_id)),
                    sequence_order=stop_input.sequence_order,
                    arrival_offset=stop_input.arrival_offset,
                    departure_offset=stop_input.departure_offset,
                )
            )

        await db.commit()
        return await _load_and_map_route(db, route.id)

    @strawberry.mutation(description="Set a route status to active or inactive.")
    async def set_route_status(
        self,
        info: strawberry.Info,
        input: SetRouteStatusInput,
    ) -> RouteMutationResult:
        db: AsyncSession = info.context["db"]
        route_result = await _get_owned_route(db, info, input.route_id)
        if isinstance(route_result, (AuthError, ForbiddenError, NotFoundError, ValidationError)):
            return route_result
        route = route_result

        try:
            route.status = models.RouteStatusEnum(input.status)
        except ValueError:
            return ValidationError(message="Invalid route status")

        db.add(route)
        await db.commit()
        return await _load_and_map_route(db, route.id)

    @strawberry.mutation(description="Add a boarding or dropping point for a stop on a route.")
    async def add_boarding_point(
        self,
        info: strawberry.Info,
        input: AddBoardingPointInput,
    ) -> BoardingPointMutationResult:
        db: AsyncSession = info.context["db"]
        route_result = await _get_owned_route(db, info, input.route_id)
        if isinstance(route_result, (AuthError, ForbiddenError, NotFoundError, ValidationError)):
            return route_result
        route = route_result

        try:
            stop_id = uuid.UUID(str(input.stop_id))
        except ValueError:
            return ValidationError(message="Invalid stop ID")
        if not await _route_has_stop(db, route, stop_id):
            return ValidationError(message="Boarding point stop must be on the route")

        name = " ".join(input.name.strip().split())
        if not name:
            return ValidationError(message="Boarding point name is required")
        if len(name) > 120:
            return ValidationError(message="Boarding point name must be 120 characters or fewer")

        try:
            point_type = models.BoardingStopTypeEnum(input.type)
        except ValueError:
            return ValidationError(message="Invalid boarding point type")

        existing_result = await db.execute(
            select(models.BoardingPoint).where(
                models.BoardingPoint.org_id == route.org_id,
                models.BoardingPoint.stop_id == stop_id,
                func.lower(models.BoardingPoint.name) == name.lower(),
            )
        )
        if existing_result.scalar_one_or_none():
            return ValidationError(message="Boarding point already exists for this stop")

        boarding_point = models.BoardingPoint(
            org_id=route.org_id,
            stop_id=stop_id,
            name=name,
            type=point_type,
        )
        db.add(boarding_point)
        await db.commit()

        result = await db.execute(
            select(models.BoardingPoint)
            .where(models.BoardingPoint.id == boarding_point.id)
            .options(selectinload(models.BoardingPoint.stop))
        )
        return _map_boarding_point(result.scalar_one())


async def _get_owned_org_for_route_mutation(
    db: AsyncSession,
    info: strawberry.Info,
) -> models.Org | AuthError | ForbiddenError | ValidationError:
    current_user: models.User | None = info.context.get("current_user")
    if not current_user:
        return AuthError(message="Authentication required")
    if not has_role(current_user, models.RoleEnum.org_admin, models.RoleEnum.admin):
        return ForbiddenError(message="Only organization admins can manage routes")
    if has_role(current_user, models.RoleEnum.admin):
        return ValidationError(message="Platform admins must act through an organization owner account")

    result = await db.execute(
        select(models.Org).where(models.Org.owner_user_id == current_user.id)
    )
    org = result.scalar_one_or_none()
    if not org:
        return ValidationError(message="Current user does not own an organization")
    if org.approval_status == models.OrgApprovalEnum.suspended:
        return ForbiddenError(message="Suspended organizations cannot manage routes")
    return org


async def _get_owned_route(
    db: AsyncSession,
    info: strawberry.Info,
    route_id: strawberry.ID,
) -> models.Route | AuthError | ForbiddenError | NotFoundError | ValidationError:
    try:
        parsed_route_id = uuid.UUID(str(route_id))
    except ValueError:
        return ValidationError(message="Invalid route ID")

    org_result = await _get_owned_org_for_route_mutation(db, info)
    if isinstance(org_result, (AuthError, ForbiddenError, ValidationError)):
        return org_result

    result = await db.execute(
        select(models.Route).where(
            models.Route.id == parsed_route_id,
            models.Route.org_id == org_result.id,
        )
    )
    route = result.scalar_one_or_none()
    if not route:
        return NotFoundError(message="Route not found")
    return route


async def _get_two_stops(
    db: AsyncSession,
    first_stop_id: uuid.UUID,
    second_stop_id: uuid.UUID,
) -> tuple[models.Stop | None, models.Stop | None]:
    result = await db.execute(
        select(models.Stop).where(models.Stop.id.in_([first_stop_id, second_stop_id]))
    )
    stops_by_id = {stop.id: stop for stop in result.scalars().all()}
    return stops_by_id.get(first_stop_id), stops_by_id.get(second_stop_id)


def _validate_route_stop_inputs(inputs: list[RouteStopInput]) -> ValidationError | None:
    if not inputs:
        return ValidationError(message="At least one route stop is required")

    seen_sequences: set[int] = set()
    seen_stops: set[str] = set()
    previous_sequence: int | None = None
    previous_departure_offset: int | None = None
    for stop_input in sorted(inputs, key=lambda item: item.sequence_order):
        try:
            uuid.UUID(str(stop_input.stop_id))
        except ValueError:
            return ValidationError(message="Invalid route stop ID")
        if stop_input.sequence_order < 1:
            return ValidationError(message="Route stop sequence must be greater than zero")
        if stop_input.sequence_order in seen_sequences:
            return ValidationError(message="Route stop sequence values must be unique")
        seen_sequences.add(stop_input.sequence_order)

        stop_key = str(stop_input.stop_id)
        if stop_key in seen_stops:
            return ValidationError(message="A stop can only appear once on a route")
        seen_stops.add(stop_key)

        if stop_input.arrival_offset is not None and stop_input.arrival_offset < 0:
            return ValidationError(message="Arrival offset cannot be negative")
        if stop_input.departure_offset is not None and stop_input.departure_offset < 0:
            return ValidationError(message="Departure offset cannot be negative")
        if (
            stop_input.arrival_offset is not None
            and stop_input.departure_offset is not None
            and stop_input.departure_offset < stop_input.arrival_offset
        ):
            return ValidationError(message="Departure offset cannot be before arrival offset")
        current_offset = (
            stop_input.departure_offset
            if stop_input.departure_offset is not None
            else stop_input.arrival_offset
        )
        if (
            previous_departure_offset is not None
            and current_offset is not None
            and current_offset < previous_departure_offset
        ):
            return ValidationError(message="Route stop offsets must increase with sequence")
        if previous_sequence is not None and stop_input.sequence_order <= previous_sequence:
            return ValidationError(message="Route stop sequence must increase")
        previous_sequence = stop_input.sequence_order
        if current_offset is not None:
            previous_departure_offset = current_offset

    return None


async def _route_has_stop(
    db: AsyncSession,
    route: models.Route,
    stop_id: uuid.UUID,
) -> bool:
    if stop_id in {route.source_stop_id, route.dest_stop_id}:
        return True
    result = await db.execute(
        select(models.RouteStop.id).where(
            models.RouteStop.route_id == route.id,
            models.RouteStop.stop_id == stop_id,
        )
    )
    return result.scalar_one_or_none() is not None


async def _load_and_map_route(db: AsyncSession, route_id: uuid.UUID) -> RouteType:
    result = await db.execute(
        select(models.Route)
        .where(models.Route.id == route_id)
        .options(
            selectinload(models.Route.source_stop),
            selectinload(models.Route.dest_stop),
            selectinload(models.Route.route_stops).selectinload(models.RouteStop.stop),
        )
    )
    route = result.scalar_one()
    sorted_route_stops = sorted(
        route.route_stops or [],
        key=lambda route_stop: route_stop.sequence_order or 0,
    )
    return RouteType(
        id=str(route.id),
        status=route.status.value if route.status else None,
        source_stop=_map_stop(route.source_stop) if route.source_stop else None,
        dest_stop=_map_stop(route.dest_stop) if route.dest_stop else None,
        route_stops=[_map_route_stop(route_stop) for route_stop in sorted_route_stops],
    )
