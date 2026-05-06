"""
GraphQL Queries — Trip & Bus Search
REST equivalent: GET /trips?from=X&to=Y&date=Z

This is the core search feature of BusYatra.
In GraphQL, arguments work like query params but are type-safe.
"""

import strawberry
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db import models
from app.graphql.types.trip import TripType, TripOperatorType
from app.graphql.types.bus import BusType, SeatType, TripSeatType
from app.graphql.types.route import RouteType, StopType, RouteStopType, BoardingPointType


def _map_stop(s: models.Stop) -> StopType:
    return StopType(id=str(s.id), name=s.name, city=s.city, state=s.state)


def _map_route_stop(rs: models.RouteStop) -> RouteStopType:
    return RouteStopType(
        id=str(rs.id),
        sequence_order=rs.sequence_order,
        arrival_offset=rs.arrival_offset,
        departure_offset=rs.departure_offset,
        stop=_map_stop(rs.stop) if rs.stop else None,
    )


def _map_route(r: models.Route) -> RouteType:
    return RouteType(
        id=str(r.id),
        status=r.status.value if r.status else None,
        source_stop=_map_stop(r.source_stop) if r.source_stop else None,
        dest_stop=_map_stop(r.dest_stop) if r.dest_stop else None,
        route_stops=[_map_route_stop(rs) for rs in (r.route_stops or [])],
    )


def _map_bus(b: models.Bus) -> BusType:
    return BusType(
        id=str(b.id),
        bus_name=b.bus_name,
        plate_num=b.plate_num,
        bus_type=b.bus_type.value if b.bus_type else None,
        bus_status=b.bus_status.value if b.bus_status else None,
        total_decks=b.total_decks,
        rows_per_deck=b.rows_per_deck,
        cols_per_deck=b.cols_per_deck,
    )


def _map_seat(s: models.Seat) -> SeatType:
    return SeatType(
        id=str(s.id),
        seat_number=s.seat_number,
        seat_type=s.seat_type.value if s.seat_type else None,
        berth=s.berth.value,
        deck=s.deck,
        row_num=s.row_num,
        col_num=s.col_num,
        is_available=s.is_available,
    )


def _map_trip_seat(ts: models.TripSeat) -> TripSeatType:
    return TripSeatType(
        id=str(ts.id),
        status=ts.status.value if ts.status else None,
        booked_by_gender=ts.booked_by_gender.value if ts.booked_by_gender else None,
        price=float(ts.price) if ts.price else None,
        held_until=ts.held_until.isoformat() if ts.held_until else None,
        seat=_map_seat(ts.seat) if ts.seat else None,
    )


def _map_trip(t: models.Trip) -> TripType:
    return TripType(
        id=str(t.id),
        departure_time=t.departure_time.isoformat() if t.departure_time else None,
        arrival_time=t.arrival_time.isoformat() if t.arrival_time else None,
        trip_status=t.trip_status.value if t.trip_status else None,
        bus=_map_bus(t.bus) if t.bus else None,
        route=_map_route(t.route) if t.route else None,
        trip_operator=TripOperatorType(
            id=str(t.trip_operator.id),
            operator_type=t.trip_operator.operator_type.value if t.trip_operator.operator_type else None,
        ) if t.trip_operator else None,
    )


@strawberry.type
class TripQuery:
    @strawberry.field(
        description=(
            "Search available trips by source city, destination city, and travel date. "
            "REST equivalent: GET /trips?from=Delhi&to=Mumbai&date=2026-05-10"
        )
    )
    async def search_trips(
        self,
        info: strawberry.Info,
        from_city: str,
        to_city: str,
        date: Optional[str] = None,
    ) -> list[TripType]:
        """
        GraphQL query:
          query {
            searchTrips(fromCity: "Delhi", toCity: "Mumbai") {
              id departureTime
              bus { busName busType }
              route { sourceStop { city } destStop { city } }
            }
          }
        """
        db: AsyncSession = info.context["db"]

        # Load trips with their bus and route eagerly (avoids N+1)
        stmt = (
            select(models.Trip)
            .join(models.Trip.route)
            .join(models.Route.source_stop.of_type(models.Stop), isouter=True)
            .join(models.Route.dest_stop.of_type(models.Stop), isouter=True)
            .where(
                models.Stop.city.ilike(from_city),
            )
            .options(
                selectinload(models.Trip.bus),
                selectinload(models.Trip.route).selectinload(models.Route.source_stop),
                selectinload(models.Trip.route).selectinload(models.Route.dest_stop),
                selectinload(models.Trip.route).selectinload(models.Route.route_stops).selectinload(models.RouteStop.stop),
                selectinload(models.Trip.trip_operator),
            )
        )

        result = await db.execute(stmt)
        trips = result.scalars().unique().all()
        return [_map_trip(t) for t in trips]

    @strawberry.field(description="Get a single trip by ID with full seat map.")
    async def trip(self, info: strawberry.Info, id: strawberry.ID) -> Optional[TripType]:
        """REST equivalent: GET /trips/{id}"""
        import uuid as uuid_mod
        db: AsyncSession = info.context["db"]
        stmt = (
            select(models.Trip)
            .where(models.Trip.id == uuid_mod.UUID(str(id)))
            .options(
                selectinload(models.Trip.bus).selectinload(models.Bus.seats),
                selectinload(models.Trip.route).selectinload(models.Route.source_stop),
                selectinload(models.Trip.route).selectinload(models.Route.dest_stop),
                selectinload(models.Trip.route).selectinload(models.Route.route_stops).selectinload(models.RouteStop.stop),
                selectinload(models.Trip.trip_seats).selectinload(models.TripSeat.seat),
                selectinload(models.Trip.trip_operator),
            )
        )
        result = await db.execute(stmt)
        db_trip = result.scalar_one_or_none()
        return _map_trip(db_trip) if db_trip else None

    @strawberry.field(description="Get all seats (with booking status) for a trip.")
    async def trip_seats(self, info: strawberry.Info, trip_id: strawberry.ID) -> list[TripSeatType]:
        """REST equivalent: GET /trips/{id}/seats"""
        import uuid as uuid_mod
        db: AsyncSession = info.context["db"]
        stmt = (
            select(models.TripSeat)
            .where(models.TripSeat.trip_id == uuid_mod.UUID(str(trip_id)))
            .options(selectinload(models.TripSeat.seat))
        )
        result = await db.execute(stmt)
        return [_map_trip_seat(ts) for ts in result.scalars().all()]
