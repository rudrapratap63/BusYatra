"""GraphQL Types - organization dashboard views."""

import strawberry
from typing import Optional

from app.graphql.types.bus import BusType
from app.graphql.types.route import RouteType
from app.graphql.types.user import OrgType


@strawberry.type
class OrgDetailType:
    """Organization details with dashboard-ready nested resources."""

    id: strawberry.ID
    name: Optional[str]
    email: str
    phone_num: Optional[str]
    approval_status: Optional[str]
    buses: list[BusType]
    routes: list[RouteType]


__all__ = ["OrgDetailType", "OrgType"]
