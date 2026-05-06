"""
GraphQL Types — Stop, BoardingPoint, Route, RouteStop
"""

import strawberry
from typing import Optional


@strawberry.type
class StopType:
    """A city/town stop on any route (e.g. Delhi, Agra, Jaipur)."""
    id: strawberry.ID
    name: Optional[str]
    city: Optional[str]
    state: Optional[str]


@strawberry.type
class BoardingPointType:
    """
    A specific pickup/drop location at a stop.
    e.g. Stop = Delhi, BoardingPoint = "ISBT Kashmere Gate"
    """
    id: strawberry.ID
    name: Optional[str]
    type: Optional[str]            # boarding / dropping / both
    stop: Optional[StopType]


@strawberry.type
class RouteStopType:
    """An ordered stop on a route with timing offsets."""
    id: strawberry.ID
    sequence_order: Optional[int]
    arrival_offset: Optional[int]   # minutes from departure
    departure_offset: Optional[int]
    stop: Optional[StopType]


@strawberry.type
class RouteType:
    """A route from source to destination, belonging to an org."""
    id: strawberry.ID
    status: Optional[str]
    source_stop: Optional[StopType]
    dest_stop: Optional[StopType]
    route_stops: list[RouteStopType]
