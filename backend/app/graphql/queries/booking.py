"""
GraphQL Queries — Bookings
REST equivalent: GET /bookings/me, GET /bookings/{id}
"""

import strawberry
import uuid as uuid_mod
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db import models
from app.graphql.types.booking import BookingType, BookingPassengerType, PaymentType
from app.graphql.types.bus import TripSeatType
from app.graphql.queries.trip import _map_trip, _map_trip_seat
from app.graphql.queries.trip import _map_stop


def _map_boarding_point(bp: models.BoardingPoint):
    from app.graphql.types.route import BoardingPointType
    return BoardingPointType(
        id=str(bp.id),
        name=bp.name,
        type=bp.type.value if bp.type else None,
        stop=_map_stop(bp.stop) if bp.stop else None,
    )


def _map_payment(p: models.Payment) -> PaymentType:
    return PaymentType(
        id=str(p.id),
        amount=float(p.amount) if p.amount else None,
        payment_method=p.payment_method,
        payment_status=p.payment_status.value if p.payment_status else None,
        gateway_ref=p.gateway_ref,
    )


def _map_passenger(bp: models.BookingPassenger) -> BookingPassengerType:
    return BookingPassengerType(
        id=str(bp.id),
        name=bp.name,
        age=bp.age,
        gender=bp.gender.value if bp.gender else None,
        cancellation_status=bp.cancellation_status.value,
        refund_amount=float(bp.refund_amount) if bp.refund_amount else None,
        trip_seat=_map_trip_seat(bp.trip_seat) if bp.trip_seat else None,
    )


def _map_booking(b: models.Booking) -> BookingType:
    return BookingType(
        id=str(b.id),
        pnr=b.pnr,
        total_amount=float(b.total_amount) if b.total_amount else None,
        status=b.status.value if b.status else None,
        created_at=b.created_at.isoformat(),
        trip=_map_trip(b.trip) if b.trip else None,
        boarding_point=_map_boarding_point(b.boarding_point) if b.boarding_point else None,
        drop_point=_map_boarding_point(b.drop_point) if b.drop_point else None,
        passengers=[_map_passenger(p) for p in (b.passengers or [])],
        payment=_map_payment(b.payment) if b.payment else None,
    )


_BOOKING_LOAD_OPTIONS = [
    selectinload(models.Booking.trip).selectinload(models.Trip.bus),
    selectinload(models.Booking.trip).selectinload(models.Trip.route).selectinload(models.Route.source_stop),
    selectinload(models.Booking.trip).selectinload(models.Trip.route).selectinload(models.Route.dest_stop),
    selectinload(models.Booking.boarding_point).selectinload(models.BoardingPoint.stop),
    selectinload(models.Booking.drop_point).selectinload(models.BoardingPoint.stop),
    selectinload(models.Booking.passengers).selectinload(models.BookingPassenger.trip_seat).selectinload(models.TripSeat.seat),
    selectinload(models.Booking.payment),
]


@strawberry.type
class BookingQuery:
    @strawberry.field(description="Get all bookings for the current authenticated user.")
    async def my_bookings(self, info: strawberry.Info) -> list[BookingType]:
        """
        REST equivalent: GET /bookings/me
        
        GraphQL query:
          query {
            myBookings {
              pnr status
              trip { departureTime bus { busName } }
              passengers { name seat { seatNumber } }
            }
          }
        """
        db: AsyncSession = info.context["db"]
        current_user: models.User | None = info.context.get("current_user")
        if not current_user:
            return []

        stmt = (
            select(models.Booking)
            .where(models.Booking.user_id == current_user.id)
            .options(*_BOOKING_LOAD_OPTIONS)
        )
        result = await db.execute(stmt)
        return [_map_booking(b) for b in result.scalars().unique().all()]

    @strawberry.field(description="Get a specific booking by ID.")
    async def booking(self, info: strawberry.Info, id: strawberry.ID) -> Optional[BookingType]:
        """REST equivalent: GET /bookings/{id}"""
        db: AsyncSession = info.context["db"]
        stmt = (
            select(models.Booking)
            .where(models.Booking.id == uuid_mod.UUID(str(id)))
            .options(*_BOOKING_LOAD_OPTIONS)
        )
        result = await db.execute(stmt)
        db_booking = result.scalar_one_or_none()
        return _map_booking(db_booking) if db_booking else None
