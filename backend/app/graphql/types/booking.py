"""
GraphQL Types — Booking, BookingPassenger, Payment
"""

import strawberry
from typing import Optional
from app.graphql.types.trip import TripType
from app.graphql.types.route import BoardingPointType
from app.graphql.types.bus import TripSeatType


@strawberry.type
class PaymentType:
    id: strawberry.ID
    amount: Optional[float]
    payment_method: Optional[str]
    payment_status: Optional[str]
    gateway_ref: Optional[str]


@strawberry.type
class BookingPassengerType:
    """A passenger associated with one seat in a booking."""
    id: strawberry.ID
    name: Optional[str]
    age: Optional[int]
    gender: Optional[str]
    cancellation_status: str
    refund_amount: Optional[float]
    trip_seat: Optional[TripSeatType]


@strawberry.type
class BookingType:
    """
    A full booking — contains all seats, passengers, payment info.
    REST equivalent: GET /bookings/{id}
    
    But in GraphQL, a traveller's "My Trips" page can request:
      booking { pnr status trip { departureTime } passengers { name seatNum } }
    in ONE query vs 3+ REST calls!
    """
    id: strawberry.ID
    pnr: str
    total_amount: Optional[float]
    status: Optional[str]
    created_at: str
    trip: Optional[TripType]
    boarding_point: Optional[BoardingPointType]
    drop_point: Optional[BoardingPointType]
    passengers: list[BookingPassengerType]
    payment: Optional[PaymentType]
