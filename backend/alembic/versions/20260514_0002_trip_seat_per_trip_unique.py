"""Allow the same physical seat across multiple trips.

Revision ID: 20260514_0002
Revises: 20260512_0001
Create Date: 2026-05-14
"""

from typing import Sequence, Union

from alembic import op


revision: str = "20260514_0002"
down_revision: Union[str, None] = "20260512_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("trip_seats_seat_id_key", "trip_seats", type_="unique")
    op.create_unique_constraint(
        "uq_trip_seat_trip_seat",
        "trip_seats",
        ["trip_id", "seat_id"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_trip_seat_trip_seat", "trip_seats", type_="unique")
    op.create_unique_constraint("trip_seats_seat_id_key", "trip_seats", ["seat_id"])
