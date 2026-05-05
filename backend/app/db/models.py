import uuid
import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class RoleEnum(str, enum.Enum):
    user = "user"
    operator = "operator"
    org_admin = "org_admin"
    admin = "admin"


class GenderTypeEnum(str, enum.Enum):
    male = "male"
    female = "female"
    other = "other"


class OperatorTypeEnum(str, enum.Enum):
    driver = "driver"
    conductor = "conductor"


class BusTypeEnum(str, enum.Enum):
    ac = "ac"
    non_ac = "non_ac"


class BookingStatusEnum(str, enum.Enum):
    confirmed = "confirmed"
    payment_pending = "payment_pending"
    cancelled = "cancelled"


class OrgApprovalEnum(str, enum.Enum):
    pending_approval = "pending_approval"
    active = "active"
    suspended = "suspended"


class TripStatusEnum(str, enum.Enum):
    scheduled = "scheduled"
    started = "started"
    cancelled = "cancelled"
    completed = "completed"


class RouteStatusEnum(str, enum.Enum):
    active = "active"
    inactive = "inactive"


class BoardingStopTypeEnum(str, enum.Enum):
    boarding = "boarding"
    dropping = "dropping"
    both = "both"


class SeatTypeEnum(str, enum.Enum):
    seater = "seater"
    sleeper = "sleeper"


class BerthTypeEnum(str, enum.Enum):
    lower = "lower"
    upper = "upper"
    none = "none"


class SeatStatusEnum(str, enum.Enum):
    available = "available"
    booked = "booked"
    blocked = "blocked"
    held = "held"


class PaymentStatusEnum(str, enum.Enum):
    pending = "pending"
    success = "success"
    failed = "failed"
    refunded = "refunded"


class BusStatusEnum(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    retired = "retired"


class PassengerCancellationStatusEnum(str, enum.Enum):
    active = "active"
    cancelled = "cancelled"


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    phone_num: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[RoleEnum | None] = mapped_column(Enum(RoleEnum), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    org: Mapped["Org | None"] = relationship(back_populates="owner", uselist=False)
    trip_operator: Mapped["TripOperator | None"] = relationship(
        back_populates="user", uselist=False
    )
    bookings: Mapped[list["Booking"]] = relationship(back_populates="user")


class Org(Base):
    __tablename__ = "orgs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    phone_num: Mapped[str | None] = mapped_column(String, nullable=True)
    owner_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    approval_status: Mapped[OrgApprovalEnum | None] = mapped_column(
        Enum(OrgApprovalEnum), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    owner: Mapped["User | None"] = relationship(back_populates="org", foreign_keys=[owner_user_id])
    buses: Mapped[list["Bus"]] = relationship(back_populates="org")
    routes: Mapped[list["Route"]] = relationship(back_populates="org")
    trips: Mapped[list["Trip"]] = relationship(back_populates="org")
    boarding_points: Mapped[list["BoardingPoint"]] = relationship(back_populates="org")


class Bus(Base):
    __tablename__ = "buses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    bus_name: Mapped[str | None] = mapped_column(String, nullable=True)
    org_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("orgs.id"), nullable=True
    )
    plate_num: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    bus_type: Mapped[BusTypeEnum | None] = mapped_column(Enum(BusTypeEnum), nullable=True)
    bus_status: Mapped[BusStatusEnum | None] = mapped_column(Enum(BusStatusEnum), nullable=True)
    total_decks: Mapped[int] = mapped_column(Integer, default=1, server_default="1")
    rows_per_deck: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cols_per_deck: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Relationships
    org: Mapped["Org | None"] = relationship(back_populates="buses")
    seats: Mapped[list["Seat"]] = relationship(back_populates="bus")
    trips: Mapped[list["Trip"]] = relationship(back_populates="bus")


class TripOperator(Base):
    __tablename__ = "trip_operators"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    operator_type: Mapped[OperatorTypeEnum | None] = mapped_column(
        Enum(OperatorTypeEnum), nullable=True
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, unique=True
    )
    trip_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trips.id"), nullable=True, unique=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    user: Mapped["User | None"] = relationship(back_populates="trip_operator")
    trip: Mapped["Trip | None"] = relationship(back_populates="trip_operator")


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    pnr: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    total_amount: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    boarding_point_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("boarding_points.id"), nullable=True
    )
    drop_point_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("boarding_points.id"), nullable=True
    )
    trip_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trips.id"), nullable=True
    )
    status: Mapped[BookingStatusEnum | None] = mapped_column(
        Enum(BookingStatusEnum), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user: Mapped["User | None"] = relationship(back_populates="bookings")
    boarding_point: Mapped["BoardingPoint | None"] = relationship(
        foreign_keys=[boarding_point_id]
    )
    drop_point: Mapped["BoardingPoint | None"] = relationship(
        foreign_keys=[drop_point_id]
    )
    trip: Mapped["Trip | None"] = relationship(back_populates="booking", foreign_keys=[trip_id])
    passengers: Mapped[list["BookingPassenger"]] = relationship(back_populates="booking")
    payment: Mapped["Payment | None"] = relationship(back_populates="booking", uselist=False)
    trip_seat: Mapped["TripSeat | None"] = relationship(
        back_populates="booking", uselist=False
    )


class BookingPassenger(Base):
    __tablename__ = "booking_passengers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gender: Mapped[GenderTypeEnum | None] = mapped_column(Enum(GenderTypeEnum), nullable=True)
    trip_seat_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trip_seats.id"), nullable=True, unique=True
    )
    booking_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bookings.id"), nullable=True
    )
    cancellation_status: Mapped[PassengerCancellationStatusEnum] = mapped_column(
        Enum(PassengerCancellationStatusEnum),
        default=PassengerCancellationStatusEnum.active,
        server_default="active",
    )
    refund_amount: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)

    # Relationships
    trip_seat: Mapped["TripSeat | None"] = relationship(back_populates="passenger")
    booking: Mapped["Booking | None"] = relationship(back_populates="passengers")


class Stop(Base):
    __tablename__ = "stops"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    city: Mapped[str | None] = mapped_column(String, nullable=True)
    state: Mapped[str | None] = mapped_column(String, nullable=True)

    # Relationships
    boarding_points: Mapped[list["BoardingPoint"]] = relationship(back_populates="stop")
    route_stops: Mapped[list["RouteStop"]] = relationship(back_populates="stop")


class Route(Base):
    __tablename__ = "routes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    org_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("orgs.id"), nullable=True
    )
    source_stop_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stops.id"), nullable=True
    )
    dest_stop_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stops.id"), nullable=True
    )
    status: Mapped[RouteStatusEnum | None] = mapped_column(Enum(RouteStatusEnum), nullable=True)

    # Relationships
    org: Mapped["Org | None"] = relationship(back_populates="routes")
    source_stop: Mapped["Stop | None"] = relationship(foreign_keys=[source_stop_id])
    dest_stop: Mapped["Stop | None"] = relationship(foreign_keys=[dest_stop_id])
    route_stops: Mapped[list["RouteStop"]] = relationship(back_populates="route")
    trips: Mapped[list["Trip"]] = relationship(back_populates="route")
    segment_prices: Mapped[list["RouteSegmentPrice"]] = relationship(back_populates="route")


class RouteStop(Base):
    __tablename__ = "route_stops"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    route_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("routes.id"), nullable=True
    )
    stop_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stops.id"), nullable=True
    )
    sequence_order: Mapped[int | None] = mapped_column(Integer, nullable=True)
    arrival_offset: Mapped[int | None] = mapped_column(Integer, nullable=True)   # minutes from departure
    departure_offset: Mapped[int | None] = mapped_column(Integer, nullable=True)

    __table_args__ = (
        UniqueConstraint("route_id", "sequence_order", name="uq_route_stop_sequence"),
    )

    # Relationships
    route: Mapped["Route | None"] = relationship(back_populates="route_stops")
    stop: Mapped["Stop | None"] = relationship(back_populates="route_stops")


class BoardingPoint(Base):
    __tablename__ = "boarding_points"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    stop_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stops.id"), nullable=True
    )
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    type: Mapped[BoardingStopTypeEnum | None] = mapped_column(
        Enum(BoardingStopTypeEnum), nullable=True
    )
    org_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("orgs.id"), nullable=True
    )

    # Relationships
    stop: Mapped["Stop | None"] = relationship(back_populates="boarding_points")
    org: Mapped["Org | None"] = relationship(back_populates="boarding_points")


class Trip(Base):
    __tablename__ = "trips"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    arrival_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    departure_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    org_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("orgs.id"), nullable=True
    )
    bus_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("buses.id"), nullable=True
    )
    route_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("routes.id"), nullable=True
    )
    trip_status: Mapped[TripStatusEnum | None] = mapped_column(
        Enum(TripStatusEnum), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    org: Mapped["Org | None"] = relationship(back_populates="trips")
    bus: Mapped["Bus | None"] = relationship(back_populates="trips")
    route: Mapped["Route | None"] = relationship(back_populates="trips")
    trip_operator: Mapped["TripOperator | None"] = relationship(
        back_populates="trip", uselist=False
    )
    booking: Mapped["Booking | None"] = relationship(
        back_populates="trip", foreign_keys="Booking.trip_id", uselist=False
    )
    trip_seats: Mapped[list["TripSeat"]] = relationship(back_populates="trip")


class Seat(Base):
    __tablename__ = "seats"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    bus_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("buses.id"), nullable=True
    )
    seat_number: Mapped[str | None] = mapped_column(String, nullable=True)  # e.g. "1A", "U2"
    seat_type: Mapped[SeatTypeEnum | None] = mapped_column(Enum(SeatTypeEnum), nullable=True)
    berth: Mapped[BerthTypeEnum] = mapped_column(
        Enum(BerthTypeEnum), default=BerthTypeEnum.none, server_default="none"
    )
    deck: Mapped[int] = mapped_column(Integer, default=1, server_default="1")
    row_num: Mapped[int | None] = mapped_column(Integer, nullable=True)
    col_num: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_available: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="true"
    )

    # Relationships
    bus: Mapped["Bus | None"] = relationship(back_populates="seats")
    trip_seat: Mapped["TripSeat | None"] = relationship(
        back_populates="seat", uselist=False
    )


class TripSeat(Base):
    __tablename__ = "trip_seats"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    trip_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trips.id"), nullable=True
    )
    seat_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("seats.id"), nullable=True, unique=True
    )
    status: Mapped[SeatStatusEnum | None] = mapped_column(Enum(SeatStatusEnum), nullable=True)
    booked_by_gender: Mapped[GenderTypeEnum | None] = mapped_column(
        Enum(GenderTypeEnum), nullable=True
    )
    price: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    held_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    booking_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bookings.id"), nullable=True, unique=True
    )

    # Relationships
    trip: Mapped["Trip | None"] = relationship(back_populates="trip_seats")
    seat: Mapped["Seat | None"] = relationship(back_populates="trip_seat")
    booking: Mapped["Booking | None"] = relationship(
        back_populates="trip_seat", foreign_keys=[booking_id]
    )
    passenger: Mapped["BookingPassenger | None"] = relationship(
        back_populates="trip_seat", uselist=False
    )


class RouteSegmentPrice(Base):
    __tablename__ = "route_segment_prices"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    route_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("routes.id"), nullable=True
    )
    from_stop_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stops.id"), nullable=True
    )
    to_stop_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stops.id"), nullable=True
    )
    seat_type: Mapped[SeatTypeEnum | None] = mapped_column(Enum(SeatTypeEnum), nullable=True)
    berth_type: Mapped[BerthTypeEnum] = mapped_column(
        Enum(BerthTypeEnum), default=BerthTypeEnum.none, server_default="none"
    )
    price: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint(
            "route_id",
            "from_stop_id",
            "to_stop_id",
            "seat_type",
            "berth_type",
            name="uq_route_segment_price",
        ),
    )

    # Relationships
    route: Mapped["Route | None"] = relationship(back_populates="segment_prices")
    from_stop: Mapped["Stop | None"] = relationship(foreign_keys=[from_stop_id])
    to_stop: Mapped["Stop | None"] = relationship(foreign_keys=[to_stop_id])


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    amount: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    gateway_ref: Mapped[str | None] = mapped_column(String, nullable=True)
    payment_method: Mapped[str | None] = mapped_column(String, nullable=True)
    payment_status: Mapped[PaymentStatusEnum | None] = mapped_column(
        Enum(PaymentStatusEnum), nullable=True
    )
    booking_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bookings.id"), nullable=True, unique=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    booking: Mapped["Booking | None"] = relationship(back_populates="payment")
