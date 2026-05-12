"""
GraphQL Queries — User
REST equivalent: GET /me, GET /users/{id}

In GraphQL, queries are read operations.
The `info` parameter gives access to context (db, current_user, request).
"""

import strawberry
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db import models
from app.graphql.types.user import UserType, OrgType
from app.graphql.permissions import require_role


def _map_user(db_user: models.User) -> UserType:
    """
    Convert SQLAlchemy model → Strawberry type.
    Like a Pydantic .from_orm() but manual — gives full control.
    """
    return UserType(
        id=str(db_user.id),
        name=db_user.name,
        email=db_user.email,
        phone_num=db_user.phone_num,
        role=db_user.role.value if db_user.role else None,
        is_verified=db_user.is_verified,
    )


def _map_org(db_org: models.Org) -> OrgType:
    return OrgType(
        id=str(db_org.id),
        name=db_org.name,
        email=db_org.email,
        phone_num=db_org.phone_num,
        approval_status=db_org.approval_status.value if db_org.approval_status else None,
    )


@strawberry.type
class UserQuery:
    @strawberry.field(description="Get the currently authenticated user's profile.")
    async def me(self, info: strawberry.Info) -> Optional[UserType]:
        """
        REST equivalent: GET /me
        
        In GraphQL, the client picks which fields:
          query { me { name email role } }
        """
        current_user: models.User | None = info.context.get("current_user")
        if not current_user:
            return None
        return _map_user(current_user)

    @strawberry.field(description="Get a user by ID. Admin only.")
    async def user(self, info: strawberry.Info, id: strawberry.ID) -> Optional[UserType]:
        """REST equivalent: GET /users/{id}"""
        require_role(info, models.RoleEnum.admin)
        db: AsyncSession = info.context["db"]
        import uuid as uuid_mod
        result = await db.execute(
            select(models.User).where(models.User.id == uuid_mod.UUID(str(id)))
        )
        db_user = result.scalar_one_or_none()
        return _map_user(db_user) if db_user else None

    @strawberry.field(description="List all users. Admin only.")
    async def users(self, info: strawberry.Info) -> list[UserType]:
        """REST equivalent: GET /users"""
        require_role(info, models.RoleEnum.admin)
        db: AsyncSession = info.context["db"]
        result = await db.execute(select(models.User))
        return [_map_user(u) for u in result.scalars().all()]
