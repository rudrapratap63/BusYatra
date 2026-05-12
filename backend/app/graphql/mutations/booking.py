"""
GraphQL Mutations — Booking
REST equivalent: POST /bookings, DELETE /bookings/{id}

This is the most complex mutation in BusYatra:
  - Validates trip & seats exist
  - Checks seat availability
  - Creates booking + passengers
  - Placeholder for payment initiation
"""

import strawberry
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db import models
from app.graphql.types.booking import BookingType
from app.graphql.queries.booking import _map_booking, _BOOKING_LOAD_OPTIONS
from app.graphql.permissions import has_role, require_authenticated, require_role


@strawberry.input
class PassengerInput:
    """Details for one passenger (maps to one seat)."""
    name: str
    age: int
    gender: str          # male / female / other
    seat_id: strawberry.ID  # which seat they want


@strawberry.input
class CreateBookingInput:
    """
    REST equivalent: POST /bookings request body
    
    GraphQL mutation:
      mutation {
        createBooking(input: {
          tripId: "abc"
          boardingPointId: "xyz"
          dropPointId: "pqr"
          passengers: [{ name: "Rudra", age: 25, gender: "male", seatId: "s1" }]
        }) {
          pnr status
        }
      }
    """
    trip_id: strawberry.ID
    boarding_point_id: strawberry.ID
    drop_point_id: strawberry.ID
    passengers: list[PassengerInput]


@strawberry.type
class BookingMutation:
    @strawberry.mutation(description="Create a new booking. Requires authentication.")
    async def create_booking(
        self,
        info: strawberry.Info,
        input: CreateBookingInput,
    ) -> Optional[BookingType]:
        db: AsyncSession = info.context["db"]
        current_user = require_role(info, models.RoleEnum.user)

        # 1. Validate trip exists
        trip_result = await db.execute(
            select(models.Trip).where(models.Trip.id == uuid.UUID(str(input.trip_id)))
        )
        trip = trip_result.scalar_one_or_none()
        if not trip:
            raise Exception("Trip not found")

        # 2. Create the booking
        import secrets, string
        pnr = "BY" + "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))

        booking = models.Booking(
            pnr=pnr,
            user_id=current_user.id,
            trip_id=trip.id,
            boarding_point_id=uuid.UUID(str(input.boarding_point_id)),
            drop_point_id=uuid.UUID(str(input.drop_point_id)),
            status=models.BookingStatusEnum.payment_pending,
        )
        db.add(booking)
        await db.flush()  # get booking.id without committing yet

        # 3. Create passengers & link trip seats
        for p_input in input.passengers:
            # Lock the trip seat
            ts_result = await db.execute(
                select(models.TripSeat).where(
                    models.TripSeat.seat_id == uuid.UUID(str(p_input.seat_id)),
                    models.TripSeat.trip_id == trip.id,
                    models.TripSeat.status == models.SeatStatusEnum.available,
                )
            )
            trip_seat = ts_result.scalar_one_or_none()
            if not trip_seat:
                await db.rollback()
                raise Exception(f"Seat {p_input.seat_id} is not available")

            trip_seat.status = models.SeatStatusEnum.held
            trip_seat.booking_id = booking.id
            trip_seat.booked_by_gender = models.GenderTypeEnum(p_input.gender)

            passenger = models.BookingPassenger(
                name=p_input.name,
                age=p_input.age,
                gender=models.GenderTypeEnum(p_input.gender),
                trip_seat_id=trip_seat.id,
                booking_id=booking.id,
            )
            db.add(passenger)

        await db.commit()

        # 4. Return the fresh booking with all relations
        stmt = (
            select(models.Booking)
            .where(models.Booking.id == booking.id)
            .options(*_BOOKING_LOAD_OPTIONS)
        )
        result = await db.execute(stmt)
        fresh_booking = result.scalar_one()
        return _map_booking(fresh_booking)

    @strawberry.mutation(description="Cancel a booking by ID.")
    async def cancel_booking(
        self,
        info: strawberry.Info,
        booking_id: strawberry.ID,
    ) -> Optional[BookingType]:
        """REST equivalent: DELETE /bookings/{id} or PATCH /bookings/{id}/cancel"""
        db: AsyncSession = info.context["db"]
        current_user = require_authenticated(info)
        filters = [models.Booking.id == uuid.UUID(str(booking_id))]
        if not has_role(current_user, models.RoleEnum.admin):
            filters.append(models.Booking.user_id == current_user.id)

        stmt = (
            select(models.Booking)
            .where(*filters)
            .options(*_BOOKING_LOAD_OPTIONS)
        )
        result = await db.execute(stmt)
        booking = result.scalar_one_or_none()

        if not booking:
            raise Exception("Booking not found")

        booking.status = models.BookingStatusEnum.cancelled

        # Release all seats
        for passenger in booking.passengers:
            if passenger.trip_seat:
                passenger.trip_seat.status = models.SeatStatusEnum.available
                passenger.trip_seat.booking_id = None
            passenger.cancellation_status = models.PassengerCancellationStatusEnum.cancelled

        await db.commit()

        # Re-fetch for response
        result2 = await db.execute(
            select(models.Booking)
            .where(models.Booking.id == booking.id)
            .options(*_BOOKING_LOAD_OPTIONS)
        )
        return _map_booking(result2.scalar_one())
