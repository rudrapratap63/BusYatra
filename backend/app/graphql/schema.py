"""
GraphQL Root Schema
Combines all Query and Mutation classes into one schema.

This is like FastAPI's APIRouter.include_router() — we merge
all feature-specific query/mutation types here.
"""

import strawberry
from strawberry.fastapi import GraphQLRouter

from app.graphql.queries.user import UserQuery
from app.graphql.queries.trip import TripQuery
from app.graphql.queries.booking import BookingQuery
from app.graphql.mutations.user import UserMutation
from app.graphql.mutations.booking import BookingMutation
from app.graphql.mutations.org import OrgMutation
from app.graphql.mutations.bus import BusMutation


@strawberry.type
class Query(UserQuery, TripQuery, BookingQuery):
    """
    Root Query type — all read operations.
    
    Multiple inheritance lets us split queries across files (like routers)
    while combining them into one GraphQL root type.
    
    Available queries:
      - me, user, users           (from UserQuery)
      - searchTrips, trip, tripSeats  (from TripQuery)
      - myBookings, booking       (from BookingQuery)
    """
    pass


@strawberry.type
class Mutation(UserMutation, BookingMutation, OrgMutation, BusMutation):
    """
    Root Mutation type — all write operations.
    
    Available mutations:
      - updateProfile             (from UserMutation)
      - createBooking, cancelBooking  (from BookingMutation)
      - registerOrg               (from OrgMutation)
      - addBus, updateBus, removeBus  (from BusMutation)
    """
    pass


# The schema object — this is what FastAPI mounts
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)


def get_graphql_router(context_getter) -> GraphQLRouter:
    """
    Returns a mounted GraphQL router with context injection.
    
    context_getter is an async function that returns a dict with:
      - db: AsyncSession
      - current_user: User | None
      - request: Request
    """
    return GraphQLRouter(
        schema,
        context_getter=context_getter,
        # GraphiQL playground is enabled by default — visit /graphql in browser
    )
