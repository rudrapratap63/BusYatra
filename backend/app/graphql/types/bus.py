"""
GraphQL Types — Bus, Seat, TripSeat
"""

import strawberry
from typing import Optional


@strawberry.type
class SeatType:
    """A physical seat on a bus."""
    id: strawberry.ID
    seat_number: Optional[str]
    seat_type: Optional[str]       # seater / sleeper
    berth: str                     # lower / upper / none
    deck: int
    row_num: Optional[int]
    col_num: Optional[int]
    is_available: bool


@strawberry.type
class TripSeatType:
    """
    A seat for a specific trip — has booking status, price, hold timer.
    REST equivalent: GET /trips/{id}/seats returns a list of these.
    """
    id: strawberry.ID
    status: Optional[str]          # available / booked / blocked / held
    booked_by_gender: Optional[str]
    price: Optional[float]
    held_until: Optional[str]
    seat: Optional[SeatType]       # ← nested! client can request seat.seatNumber etc.


@strawberry.type
class BusType:
    """A bus owned by an organization."""
    id: strawberry.ID
    bus_name: Optional[str]
    plate_num: str
    bus_type: Optional[str]        # ac / non_ac
    bus_status: Optional[str]
    total_decks: int
    rows_per_deck: Optional[int]
    cols_per_deck: Optional[int]
