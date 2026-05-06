"""
GraphQL Mutations — User Profile
REST equivalent: PATCH /me

Mutations = write operations (create, update, delete).
They always have:
  1. An @strawberry.input class (the input shape)
  2. A resolver method that does the work and returns a type
"""

import strawberry
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import models
from app.graphql.types.user import UserType
from app.graphql.queries.user import _map_user


@strawberry.input
class UpdateProfileInput:
    """
    REST equivalent: the request body for PATCH /me
    
    @strawberry.input = a read-only input type (can't be used as output).
    All fields are Optional so the client can update just what they want.
    """
    name: Optional[str] = strawberry.UNSET
    phone_num: Optional[str] = strawberry.UNSET


@strawberry.type
class UserMutation:
    @strawberry.mutation(description="Update the current user's profile.")
    async def update_profile(
        self,
        info: strawberry.Info,
        input: UpdateProfileInput,
    ) -> Optional[UserType]:
        """
        GraphQL mutation:
          mutation {
            updateProfile(input: { name: "Rudra Pratap" }) {
              id name email
            }
          }
        
        Notice: you also specify what fields you want BACK — same as queries!
        """
        db: AsyncSession = info.context["db"]
        current_user: models.User | None = info.context.get("current_user")
        if not current_user:
            return None

        if input.name is not strawberry.UNSET:
            current_user.name = input.name
        if input.phone_num is not strawberry.UNSET:
            current_user.phone_num = input.phone_num

        db.add(current_user)
        await db.commit()
        await db.refresh(current_user)
        return _map_user(current_user)
