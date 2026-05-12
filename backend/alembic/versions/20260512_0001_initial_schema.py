"""Initial database schema.

Revision ID: 20260512_0001
Revises:
Create Date: 2026-05-12
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260512_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


role_enum = sa.Enum("user", "operator", "org_admin", "admin", name="roleenum")
gender_type_enum = sa.Enum("male", "female", "other", name="gendertypeenum")
operator_type_enum = sa.Enum("driver", "conductor", name="operatortypeenum")
bus_type_enum = sa.Enum("ac", "non_ac", name="bustypeenum")
booking_status_enum = sa.Enum(
    "confirmed", "payment_pending", "cancelled", name="bookingstatusenum"
)
org_approval_enum = sa.Enum(
    "pending_approval", "active", "suspended", name="orgapprovalenum"
)
trip_status_enum = sa.Enum(
    "scheduled", "started", "cancelled", "completed", name="tripstatusenum"
)
route_status_enum = sa.Enum("active", "inactive", name="routestatusenum")
boarding_stop_type_enum = sa.Enum(
    "boarding", "dropping", "both", name="boardingstoptypeenum"
)
seat_type_enum = sa.Enum("seater", "sleeper", name="seattypeenum")
berth_type_enum = sa.Enum("lower", "upper", "none", name="berthtypeenum")
seat_status_enum = sa.Enum(
    "available", "booked", "blocked", "held", name="seatstatusenum"
)
payment_status_enum = sa.Enum(
    "pending", "success", "failed", "refunded", name="paymentstatusenum"
)
bus_status_enum = sa.Enum("active", "inactive", "retired", name="busstatusenum")
passenger_cancellation_status_enum = sa.Enum(
    "active", "cancelled", name="passengercancellationstatusenum"
)


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(), nullable=True),
        sa.Column("phone_num", sa.String(), nullable=False),
        sa.Column("role", role_enum, nullable=True),
        sa.Column("is_verified", sa.Boolean(), server_default="false", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_table(
        "stops",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("city", sa.String(), nullable=True),
        sa.Column("state", sa.String(), nullable=True),
    )

    op.create_table(
        "orgs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=False, unique=True),
        sa.Column("phone_num", sa.String(), nullable=True),
        sa.Column("owner_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approval_status", org_approval_enum, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"]),
    )

    op.create_table(
        "buses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("bus_name", sa.String(), nullable=True),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("plate_num", sa.String(), nullable=False, unique=True),
        sa.Column("bus_type", bus_type_enum, nullable=True),
        sa.Column("bus_status", bus_status_enum, nullable=True),
        sa.Column("total_decks", sa.Integer(), server_default="1", nullable=False),
        sa.Column("rows_per_deck", sa.Integer(), nullable=True),
        sa.Column("cols_per_deck", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["org_id"], ["orgs.id"]),
    )

    op.create_table(
        "routes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("source_stop_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("dest_stop_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", route_status_enum, nullable=True),
        sa.ForeignKeyConstraint(["org_id"], ["orgs.id"]),
        sa.ForeignKeyConstraint(["source_stop_id"], ["stops.id"]),
        sa.ForeignKeyConstraint(["dest_stop_id"], ["stops.id"]),
    )

    op.create_table(
        "boarding_points",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("stop_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("type", boarding_stop_type_enum, nullable=True),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["stop_id"], ["stops.id"]),
        sa.ForeignKeyConstraint(["org_id"], ["orgs.id"]),
    )

    op.create_table(
        "route_stops",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("route_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("stop_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("sequence_order", sa.Integer(), nullable=True),
        sa.Column("arrival_offset", sa.Integer(), nullable=True),
        sa.Column("departure_offset", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["route_id"], ["routes.id"]),
        sa.ForeignKeyConstraint(["stop_id"], ["stops.id"]),
        sa.UniqueConstraint("route_id", "sequence_order", name="uq_route_stop_sequence"),
    )

    op.create_table(
        "trips",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("arrival_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("departure_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("bus_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("route_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("trip_status", trip_status_enum, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["org_id"], ["orgs.id"]),
        sa.ForeignKeyConstraint(["bus_id"], ["buses.id"]),
        sa.ForeignKeyConstraint(["route_id"], ["routes.id"]),
    )

    op.create_table(
        "seats",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("bus_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("seat_number", sa.String(), nullable=True),
        sa.Column("seat_type", seat_type_enum, nullable=True),
        sa.Column("berth", berth_type_enum, server_default="none", nullable=False),
        sa.Column("deck", sa.Integer(), server_default="1", nullable=False),
        sa.Column("row_num", sa.Integer(), nullable=True),
        sa.Column("col_num", sa.Integer(), nullable=True),
        sa.Column("is_available", sa.Boolean(), server_default="true", nullable=False),
        sa.ForeignKeyConstraint(["bus_id"], ["buses.id"]),
    )

    op.create_table(
        "trip_operators",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("operator_type", operator_type_enum, nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True, unique=True),
        sa.Column("trip_id", postgresql.UUID(as_uuid=True), nullable=True, unique=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["trip_id"], ["trips.id"]),
    )

    op.create_table(
        "bookings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("pnr", sa.String(), nullable=False, unique=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("total_amount", sa.Numeric(10, 2), nullable=True),
        sa.Column("boarding_point_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("drop_point_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("trip_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", booking_status_enum, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["boarding_point_id"], ["boarding_points.id"]),
        sa.ForeignKeyConstraint(["drop_point_id"], ["boarding_points.id"]),
        sa.ForeignKeyConstraint(["trip_id"], ["trips.id"]),
    )

    op.create_table(
        "route_segment_prices",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("route_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("from_stop_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("to_stop_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("seat_type", seat_type_enum, nullable=True),
        sa.Column("berth_type", berth_type_enum, server_default="none", nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["route_id"], ["routes.id"]),
        sa.ForeignKeyConstraint(["from_stop_id"], ["stops.id"]),
        sa.ForeignKeyConstraint(["to_stop_id"], ["stops.id"]),
        sa.UniqueConstraint(
            "route_id",
            "from_stop_id",
            "to_stop_id",
            "seat_type",
            "berth_type",
            name="uq_route_segment_price",
        ),
    )

    op.create_table(
        "trip_seats",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("trip_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("seat_id", postgresql.UUID(as_uuid=True), nullable=True, unique=True),
        sa.Column("status", seat_status_enum, nullable=True),
        sa.Column("booked_by_gender", gender_type_enum, nullable=True),
        sa.Column("price", sa.Numeric(10, 2), nullable=True),
        sa.Column("held_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("booking_id", postgresql.UUID(as_uuid=True), nullable=True, unique=True),
        sa.ForeignKeyConstraint(["trip_id"], ["trips.id"]),
        sa.ForeignKeyConstraint(["seat_id"], ["seats.id"]),
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"]),
    )

    op.create_table(
        "payments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=True),
        sa.Column("gateway_ref", sa.String(), nullable=True),
        sa.Column("payment_method", sa.String(), nullable=True),
        sa.Column("payment_status", payment_status_enum, nullable=True),
        sa.Column("booking_id", postgresql.UUID(as_uuid=True), nullable=True, unique=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"]),
    )

    op.create_table(
        "booking_passengers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("gender", gender_type_enum, nullable=True),
        sa.Column("trip_seat_id", postgresql.UUID(as_uuid=True), nullable=True, unique=True),
        sa.Column("booking_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "cancellation_status",
            passenger_cancellation_status_enum,
            server_default="active",
            nullable=False,
        ),
        sa.Column("refund_amount", sa.Numeric(10, 2), nullable=True),
        sa.ForeignKeyConstraint(["trip_seat_id"], ["trip_seats.id"]),
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"]),
    )


def downgrade() -> None:
    op.drop_table("booking_passengers")
    op.drop_table("payments")
    op.drop_table("trip_seats")
    op.drop_table("route_segment_prices")
    op.drop_table("bookings")
    op.drop_table("trip_operators")
    op.drop_table("seats")
    op.drop_table("trips")
    op.drop_table("route_stops")
    op.drop_table("boarding_points")
    op.drop_table("routes")
    op.drop_table("buses")
    op.drop_table("orgs")
    op.drop_table("stops")
    op.drop_table("users")

    passenger_cancellation_status_enum.drop(op.get_bind(), checkfirst=True)
    bus_status_enum.drop(op.get_bind(), checkfirst=True)
    payment_status_enum.drop(op.get_bind(), checkfirst=True)
    seat_status_enum.drop(op.get_bind(), checkfirst=True)
    berth_type_enum.drop(op.get_bind(), checkfirst=True)
    seat_type_enum.drop(op.get_bind(), checkfirst=True)
    boarding_stop_type_enum.drop(op.get_bind(), checkfirst=True)
    route_status_enum.drop(op.get_bind(), checkfirst=True)
    trip_status_enum.drop(op.get_bind(), checkfirst=True)
    org_approval_enum.drop(op.get_bind(), checkfirst=True)
    booking_status_enum.drop(op.get_bind(), checkfirst=True)
    bus_type_enum.drop(op.get_bind(), checkfirst=True)
    operator_type_enum.drop(op.get_bind(), checkfirst=True)
    gender_type_enum.drop(op.get_bind(), checkfirst=True)
    role_enum.drop(op.get_bind(), checkfirst=True)
