"""Seat layout generation for BusYatra buses."""

from dataclasses import dataclass

from app.db import models


@dataclass(frozen=True)
class SeatOverride:
    deck: int
    row_num: int
    col_num: int
    seat_number: str | None = None
    seat_type: models.SeatTypeEnum | None = None
    berth: models.BerthTypeEnum | None = None
    is_available: bool | None = None


@dataclass(frozen=True)
class SeatSpec:
    seat_number: str
    seat_type: models.SeatTypeEnum
    berth: models.BerthTypeEnum
    deck: int
    row_num: int
    col_num: int
    is_available: bool


MAX_DECKS = 2
MAX_ROWS_PER_DECK = 30
MAX_COLS_PER_DECK = 6


def validate_layout_dimensions(
    total_decks: int,
    rows_per_deck: int,
    cols_per_deck: int,
) -> str | None:
    if total_decks < 1 or total_decks > MAX_DECKS:
        return f"totalDecks must be between 1 and {MAX_DECKS}"
    if rows_per_deck < 1 or rows_per_deck > MAX_ROWS_PER_DECK:
        return f"rowsPerDeck must be between 1 and {MAX_ROWS_PER_DECK}"
    if cols_per_deck < 1 or cols_per_deck > MAX_COLS_PER_DECK:
        return f"colsPerDeck must be between 1 and {MAX_COLS_PER_DECK}"
    return None


def generate_seat_layout(
    total_decks: int,
    rows_per_deck: int,
    cols_per_deck: int,
    default_seat_type: models.SeatTypeEnum = models.SeatTypeEnum.seater,
    default_berth: models.BerthTypeEnum = models.BerthTypeEnum.none,
    overrides: list[SeatOverride] | None = None,
) -> list[SeatSpec]:
    """
    Build physical seat specs from a compact layout config.

    Every grid position becomes a seat. Per-position overrides allow mixed
    seater/sleeper layouts and upper/lower berth assignments without changing
    the database schema.
    """
    dimension_error = validate_layout_dimensions(total_decks, rows_per_deck, cols_per_deck)
    if dimension_error:
        raise ValueError(dimension_error)

    overrides_by_position = {
        (override.deck, override.row_num, override.col_num): override
        for override in overrides or []
    }

    specs: list[SeatSpec] = []
    for deck in range(1, total_decks + 1):
        for row in range(1, rows_per_deck + 1):
            for col in range(1, cols_per_deck + 1):
                override = overrides_by_position.get((deck, row, col))
                seat_type = override.seat_type if override and override.seat_type else default_seat_type
                berth = override.berth if override and override.berth else default_berth
                is_available = (
                    override.is_available
                    if override and override.is_available is not None
                    else True
                )
                seat_number = (
                    override.seat_number
                    if override and override.seat_number
                    else _default_seat_number(deck, row, col, total_decks)
                )

                specs.append(
                    SeatSpec(
                        seat_number=seat_number,
                        seat_type=seat_type,
                        berth=berth,
                        deck=deck,
                        row_num=row,
                        col_num=col,
                        is_available=is_available,
                    )
                )

    return specs


def _default_seat_number(deck: int, row: int, col: int, total_decks: int) -> str:
    col_label = chr(ord("A") + col - 1)
    prefix = "" if total_decks == 1 else f"D{deck}-"
    return f"{prefix}{row}{col_label}"
