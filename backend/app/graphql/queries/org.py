"""GraphQL Queries - organization dashboard data."""

from typing import Optional

import strawberry
from graphql import GraphQLError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import models
from app.graphql.permissions import has_role, require_authenticated
from app.graphql.queries.trip import _map_bus, _map_route, _map_trip
from app.graphql.types.bus import BusType
from app.graphql.types.org import OrgDetailType
from app.graphql.types.route import RouteType
from app.graphql.types.trip import TripType


def _map_org_detail(org: models.Org) -> OrgDetailType:
    return OrgDetailType(
        id=str(org.id),
        name=org.name,
        email=org.email,
        phone_num=org.phone_num,
        approval_status=org.approval_status.value if org.approval_status else None,
        buses=[_map_bus(bus) for bus in (org.buses or [])],
        routes=[_map_route(route) for route in (org.routes or [])],
    )


@strawberry.type
class OrgQuery:
    @strawberry.field(description="Get the current organization with dashboard resources.")
    async def my_org(self, info: strawberry.Info) -> Optional[OrgDetailType]:
        db: AsyncSession = info.context["db"]
        current_user = require_authenticated(info)
        org = await _get_owned_org(db, current_user, include_dashboard_resources=True)
        return _map_org_detail(org) if org else None

    @strawberry.field(description="List buses owned by the current organization.")
    async def org_buses(self, info: strawberry.Info) -> list[BusType]:
        db: AsyncSession = info.context["db"]
        current_user = require_authenticated(info)
        org = await _get_owned_org(db, current_user)
        if not org:
            return []

        result = await db.execute(
            select(models.Bus)
            .where(models.Bus.org_id == org.id)
            .order_by(models.Bus.bus_name, models.Bus.plate_num)
        )
        return [_map_bus(bus) for bus in result.scalars().all()]

    @strawberry.field(description="List routes owned by the current organization.")
    async def org_routes(self, info: strawberry.Info) -> list[RouteType]:
        db: AsyncSession = info.context["db"]
        current_user = require_authenticated(info)
        org = await _get_owned_org(db, current_user)
        if not org:
            return []

        result = await db.execute(
            select(models.Route)
            .where(models.Route.org_id == org.id)
            .options(
                selectinload(models.Route.source_stop),
                selectinload(models.Route.dest_stop),
                selectinload(models.Route.route_stops).selectinload(models.RouteStop.stop),
            )
        )
        return [_map_route(route) for route in result.scalars().unique().all()]

    @strawberry.field(description="List trips scheduled by the current organization.")
    async def org_trips(self, info: strawberry.Info) -> list[TripType]:
        db: AsyncSession = info.context["db"]
        current_user = require_authenticated(info)
        org = await _get_owned_org(db, current_user)
        if not org:
            return []

        result = await db.execute(
            select(models.Trip)
            .where(models.Trip.org_id == org.id)
            .options(
                selectinload(models.Trip.bus),
                selectinload(models.Trip.route).selectinload(models.Route.source_stop),
                selectinload(models.Trip.route).selectinload(models.Route.dest_stop),
                selectinload(models.Trip.route)
                .selectinload(models.Route.route_stops)
                .selectinload(models.RouteStop.stop),
                selectinload(models.Trip.trip_operator),
            )
            .order_by(models.Trip.departure_time.desc().nullslast())
        )
        return [_map_trip(trip) for trip in result.scalars().unique().all()]


async def _get_owned_org(
    db: AsyncSession,
    current_user: models.User,
    include_dashboard_resources: bool = False,
) -> models.Org | None:
    if not has_role(current_user, models.RoleEnum.org_admin):
        raise GraphQLError("Only organization admins can access organization dashboard data")

    stmt = select(models.Org).where(models.Org.owner_user_id == current_user.id)
    if include_dashboard_resources:
        stmt = stmt.options(
            selectinload(models.Org.buses),
            selectinload(models.Org.routes).selectinload(models.Route.source_stop),
            selectinload(models.Org.routes).selectinload(models.Route.dest_stop),
            selectinload(models.Org.routes)
            .selectinload(models.Route.route_stops)
            .selectinload(models.RouteStop.stop),
        )

    result = await db.execute(stmt)
    return result.scalar_one_or_none()
