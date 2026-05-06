"""
GraphQL Types — Trip & TripOperator
"""

import strawberry
from typing import Optional
from app.graphql.types.bus import BusType
from app.graphql.types.route import RouteType


@strawberry.type
class TripOperatorType:
    """Driver or conductor assigned to a trip."""
    id: strawberry.ID
    operator_type: Optional[str]  # driver / conductor


@strawberry.type
class TripType:
    """
    A specific scheduled journey of a bus on a route.
    REST equivalent: GET /trips/{id}
    
    Key power of GraphQL: the client can ask for nested data:
      trip { bus { busName } route { sourceStop { city } } }
    vs REST which would need 3 separate calls.
    """
    id: strawberry.ID
    departure_time: Optional[str]
    arrival_time: Optional[str]
    trip_status: Optional[str]
    bus: Optional[BusType]
    route: Optional[RouteType]
    trip_operator: Optional[TripOperatorType]
