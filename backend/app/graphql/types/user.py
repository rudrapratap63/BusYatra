"""
GraphQL Types — User & Org
Maps SQLAlchemy models → Strawberry types for GraphQL output.

Think of these like Pydantic models but for GraphQL responses.
The client can pick which fields they want from these types.
"""

import strawberry
from typing import Optional
import uuid


@strawberry.type
class UserType:
    """
    Represents a User in the GraphQL schema.
    
    REST equivalent: the JSON shape returned from GET /users/{id}
    But here, the client decides which fields to fetch!
    """
    id: strawberry.ID
    name: Optional[str]
    email: str
    phone_num: str
    role: Optional[str]
    is_verified: bool


@strawberry.type
class OrgType:
    """Organization / Bus Company."""
    id: strawberry.ID
    name: Optional[str]
    email: str
    phone_num: Optional[str]
    approval_status: Optional[str]
