"""GraphQL Mutations - Bus CRUD and seat layout generation."""

import uuid
from typing import Annotated, Optional, Union

import strawberry
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import models
from app.graphql.permissions import has_role
from app.graphql.queries.trip import _map_bus
from app.graphql.types.bus import BusType
from app.graphql.types.errors import AuthError, ForbiddenError, NotFoundError, ValidationError
from app.services.seat_layout import (
    SeatOverride,
    generate_seat_layout,
    validate_layout_dimensions,
)


@strawberry.input
class SeatOverrideInput:
    deck: int
    row_num: int
    col_num: int
    seat_number: Optional[str] = None
    seat_type: Optional[str] = None
    berth: Optional[str] = None
    is_available: Optional[bool] = None


@strawberry.input
class SeatLayoutInput:
    total_decks: int
    rows_per_deck: int
    cols_per_deck: int
    default_seat_type: str = "seater"
    default_berth: str = "none"
    overrides: Optional[list[SeatOverrideInput]] = None


@strawberry.input
class AddBusInput:
    plate_num: str
    layout: SeatLayoutInput
    bus_name: Optional[str] = None
    bus_type: Optional[str] = "non_ac"


@strawberry.input
class UpdateBusInput:
    bus_id: strawberry.ID
    bus_name: Optional[str] = strawberry.UNSET
    plate_num: Optional[str] = strawberry.UNSET
    bus_type: Optional[str] = strawberry.UNSET
    bus_status: Optional[str] = strawberry.UNSET
    layout: Optional[SeatLayoutInput] = strawberry.UNSET


BusMutationResult = Annotated[
    Union[BusType, AuthError, ForbiddenError, NotFoundError, ValidationError],
    strawberry.union("BusMutationResult"),
]


@strawberry.type
class BusMutation:
    @strawberry.mutation(description="Add a bus and auto-generate seats from its layout.")
    async def add_bus(
        self,
        info: strawberry.Info,
        input: AddBusInput,
    ) -> BusMutationResult:
        db: AsyncSession = info.context["db"]
        current_user = _get_current_user(info)
        if not current_user:
            return AuthError(message="Authentication required")

        org_result = await _get_owned_org(db, current_user)
        if isinstance(org_result, (ForbiddenError, ValidationError)):
            return org_result
        org = org_result

        layout_error = _validate_layout_input(input.layout)
        if layout_error:
            return layout_error

        plate_num = _normalize_plate_num(input.plate_num)
        if not plate_num:
            return ValidationError(message="Plate number is required")

        existing_plate = await db.execute(select(models.Bus).where(models.Bus.plate_num == plate_num))
        if existing_plate.scalar_one_or_none():
            return ValidationError(message="Bus plate number already exists")

        try:
            bus_type = models.BusTypeEnum(input.bus_type or models.BusTypeEnum.non_ac.value)
        except ValueError:
            return ValidationError(message="Invalid bus type")

        bus = models.Bus(
            bus_name=input.bus_name.strip() if input.bus_name else None,
            org_id=org.id,
            plate_num=plate_num,
            bus_type=bus_type,
            bus_status=models.BusStatusEnum.active,
            total_decks=input.layout.total_decks,
            rows_per_deck=input.layout.rows_per_deck,
            cols_per_deck=input.layout.cols_per_deck,
        )
        db.add(bus)
        await db.flush()

        for seat in _build_seat_models(bus.id, input.layout):
            db.add(seat)

        await db.commit()
        await db.refresh(bus)
        return _map_bus(bus)

    @strawberry.mutation(description="Update a bus. Layout changes regenerate seats if no trips exist.")
    async def update_bus(
        self,
        info: strawberry.Info,
        input: UpdateBusInput,
    ) -> BusMutationResult:
        db: AsyncSession = info.context["db"]
        current_user = _get_current_user(info)
        if not current_user:
            return AuthError(message="Authentication required")

        try:
            bus_id = uuid.UUID(str(input.bus_id))
        except ValueError:
            return ValidationError(message="Invalid bus ID")

        bus = await _get_bus_for_current_user(db, current_user, bus_id)
        if isinstance(bus, (ForbiddenError, NotFoundError, ValidationError)):
            return bus

        if input.bus_name is not strawberry.UNSET:
            bus.bus_name = input.bus_name.strip() if input.bus_name else None
        if input.plate_num is not strawberry.UNSET:
            plate_num = _normalize_plate_num(input.plate_num)
            if not plate_num:
                return ValidationError(message="Plate number is required")
            existing_plate = await db.execute(
                select(models.Bus).where(
                    models.Bus.plate_num == plate_num,
                    models.Bus.id != bus.id,
                )
            )
            if existing_plate.scalar_one_or_none():
                return ValidationError(message="Bus plate number already exists")
            bus.plate_num = plate_num
        if input.bus_type is not strawberry.UNSET:
            try:
                bus.bus_type = models.BusTypeEnum(input.bus_type) if input.bus_type else None
            except ValueError:
                return ValidationError(message="Invalid bus type")
        if input.bus_status is not strawberry.UNSET:
            try:
                bus.bus_status = models.BusStatusEnum(input.bus_status) if input.bus_status else None
            except ValueError:
                return ValidationError(message="Invalid bus status")
        if input.layout is not strawberry.UNSET and input.layout is not None:
            layout_error = _validate_layout_input(input.layout)
            if layout_error:
                return layout_error
            if await _bus_has_trips(db, bus.id):
                return ValidationError(message="Cannot change seat layout after trips are scheduled")

            await db.execute(delete(models.Seat).where(models.Seat.bus_id == bus.id))
            bus.total_decks = input.layout.total_decks
            bus.rows_per_deck = input.layout.rows_per_deck
            bus.cols_per_deck = input.layout.cols_per_deck
            for seat in _build_seat_models(bus.id, input.layout):
                db.add(seat)

        db.add(bus)
        await db.commit()
        await db.refresh(bus)
        return _map_bus(bus)

    @strawberry.mutation(description="Remove a bus if it has no scheduled trips.")
    async def remove_bus(
        self,
        info: strawberry.Info,
        bus_id: strawberry.ID,
    ) -> BusMutationResult:
        db: AsyncSession = info.context["db"]
        current_user = _get_current_user(info)
        if not current_user:
            return AuthError(message="Authentication required")

        try:
            parsed_bus_id = uuid.UUID(str(bus_id))
        except ValueError:
            return ValidationError(message="Invalid bus ID")

        bus = await _get_bus_for_current_user(db, current_user, parsed_bus_id)
        if isinstance(bus, (ForbiddenError, NotFoundError, ValidationError)):
            return bus
        if await _bus_has_trips(db, bus.id):
            return ValidationError(message="Cannot remove a bus with scheduled trips")

        response = _map_bus(bus)
        await db.execute(delete(models.Seat).where(models.Seat.bus_id == bus.id))
        await db.delete(bus)
        await db.commit()
        return response


def _get_current_user(info: strawberry.Info) -> models.User | None:
    return info.context.get("current_user")


async def _get_owned_org(
    db: AsyncSession,
    current_user: models.User,
) -> models.Org | ForbiddenError | ValidationError:
    if not has_role(current_user, models.RoleEnum.org_admin, models.RoleEnum.admin):
        return ForbiddenError(message="Only organization admins can manage buses")

    if has_role(current_user, models.RoleEnum.admin):
        return ValidationError(message="Platform admins must act through an organization owner account")

    result = await db.execute(
        select(models.Org).where(models.Org.owner_user_id == current_user.id)
    )
    org = result.scalar_one_or_none()
    if not org:
        return ValidationError(message="Current user does not own an organization")
    if org.approval_status == models.OrgApprovalEnum.suspended:
        return ForbiddenError(message="Suspended organizations cannot manage buses")
    return org


async def _get_bus_for_current_user(
    db: AsyncSession,
    current_user: models.User,
    bus_id: uuid.UUID,
) -> models.Bus | ForbiddenError | NotFoundError | ValidationError:
    org_result = await _get_owned_org(db, current_user)
    if isinstance(org_result, (ForbiddenError, ValidationError)):
        return org_result

    result = await db.execute(
        select(models.Bus)
        .where(models.Bus.id == bus_id, models.Bus.org_id == org_result.id)
        .options(selectinload(models.Bus.seats))
    )
    bus = result.scalar_one_or_none()
    if not bus:
        return NotFoundError(message="Bus not found")
    return bus


def _validate_layout_input(layout: SeatLayoutInput) -> ValidationError | None:
    dimension_error = validate_layout_dimensions(
        layout.total_decks,
        layout.rows_per_deck,
        layout.cols_per_deck,
    )
    if dimension_error:
        return ValidationError(message=dimension_error)

    try:
        models.SeatTypeEnum(layout.default_seat_type)
        models.BerthTypeEnum(layout.default_berth)
    except ValueError:
        return ValidationError(message="Invalid default seat type or berth")

    seen_positions: set[tuple[int, int, int]] = set()
    for override in layout.overrides or []:
        position = (override.deck, override.row_num, override.col_num)
        if position in seen_positions:
            return ValidationError(message="Duplicate seat override position")
        seen_positions.add(position)
        if override.deck < 1 or override.deck > layout.total_decks:
            return ValidationError(message="Seat override deck is outside the layout")
        if override.row_num < 1 or override.row_num > layout.rows_per_deck:
            return ValidationError(message="Seat override row is outside the layout")
        if override.col_num < 1 or override.col_num > layout.cols_per_deck:
            return ValidationError(message="Seat override column is outside the layout")
        if override.seat_type:
            try:
                models.SeatTypeEnum(override.seat_type)
            except ValueError:
                return ValidationError(message="Invalid override seat type")
        if override.berth:
            try:
                models.BerthTypeEnum(override.berth)
            except ValueError:
                return ValidationError(message="Invalid override berth")

    seat_numbers = [seat.seat_number for seat in _build_seat_specs(layout)]
    if len(seat_numbers) != len(set(seat_numbers)):
        return ValidationError(message="Seat numbers must be unique within a bus")

    return None


def _build_seat_models(bus_id: uuid.UUID, layout: SeatLayoutInput) -> list[models.Seat]:
    seat_specs = _build_seat_specs(layout)
    return [
        models.Seat(
            bus_id=bus_id,
            seat_number=seat.seat_number,
            seat_type=seat.seat_type,
            berth=seat.berth,
            deck=seat.deck,
            row_num=seat.row_num,
            col_num=seat.col_num,
            is_available=seat.is_available,
        )
        for seat in seat_specs
    ]


def _build_seat_specs(layout: SeatLayoutInput):
    return generate_seat_layout(
        total_decks=layout.total_decks,
        rows_per_deck=layout.rows_per_deck,
        cols_per_deck=layout.cols_per_deck,
        default_seat_type=models.SeatTypeEnum(layout.default_seat_type),
        default_berth=models.BerthTypeEnum(layout.default_berth),
        overrides=[
            SeatOverride(
                deck=override.deck,
                row_num=override.row_num,
                col_num=override.col_num,
                seat_number=override.seat_number.strip() if override.seat_number else None,
                seat_type=models.SeatTypeEnum(override.seat_type) if override.seat_type else None,
                berth=models.BerthTypeEnum(override.berth) if override.berth else None,
                is_available=override.is_available,
            )
            for override in layout.overrides or []
        ],
    )


async def _bus_has_trips(db: AsyncSession, bus_id: uuid.UUID) -> bool:
    result = await db.execute(
        select(func.count()).select_from(models.Trip).where(models.Trip.bus_id == bus_id)
    )
    return result.scalar_one() > 0


def _normalize_plate_num(plate_num: str | None) -> str:
    return plate_num.strip().upper() if plate_num else ""
