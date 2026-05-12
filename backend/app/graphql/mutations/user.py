"""
GraphQL Mutations — User Profile
REST equivalent: PATCH /me

Mutations = write operations (create, update, delete).
They always have:
  1. An @strawberry.input class (the input shape)
  2. A resolver method that does the work and returns a type
"""

import strawberry
from typing import Annotated, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db import models
from app.graphql.types.user import UserType
from app.graphql.types.errors import AuthError, ValidationError
from app.graphql.queries.user import _map_user
from app.core.security import hash_password, verify_password, create_access_token


@strawberry.input
class UpdateProfileInput:
    """
    REST equivalent: the request body for PATCH /me
    
    @strawberry.input = a read-only input type (can't be used as output).
    All fields are Optional so the client can update just what they want.
    """
    name: Optional[str] = strawberry.UNSET
    phone_num: Optional[str] = strawberry.UNSET


@strawberry.input
class RegisterInput:
    email: str
    password: str
    phone_num: str
    name: Optional[str] = None
    role: Optional[str] = "user"


@strawberry.input
class LoginInput:
    email: str
    password: str


@strawberry.type
class AuthPayload:
    token: str
    user: UserType


UpdateProfileResult = Annotated[
    Union[UserType, AuthError],
    strawberry.union("UpdateProfileResult"),
]

AuthResult = Annotated[
    Union[AuthPayload, ValidationError],
    strawberry.union("AuthResult"),
]


@strawberry.type
class UserMutation:
    @strawberry.mutation(description="Update the current user's profile.")
    async def update_profile(
        self,
        info: strawberry.Info,
        input: UpdateProfileInput,
    ) -> UpdateProfileResult:
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
            return AuthError(message="Authentication required")

        if input.name is not strawberry.UNSET:
            current_user.name = input.name
        if input.phone_num is not strawberry.UNSET:
            current_user.phone_num = input.phone_num

        db.add(current_user)
        await db.commit()
        await db.refresh(current_user)
        return _map_user(current_user)

    @strawberry.mutation(description="Register a new user")
    async def register(
        self,
        info: strawberry.Info,
        input: RegisterInput,
    ) -> AuthResult:
        db: AsyncSession = info.context["db"]
        
        # Check if email is already taken
        result = await db.execute(select(models.User).where(models.User.email == input.email))
        if result.scalar_one_or_none():
            return ValidationError(message="Email already registered")

        if input.role not in (None, models.RoleEnum.user.value):
            return ValidationError(message="Role assignment is restricted to admins")

        hashed_pwd = hash_password(input.password)
        
        new_user = models.User(
            email=input.email,
            password_hash=hashed_pwd,
            phone_num=input.phone_num,
            name=input.name,
            role=models.RoleEnum.user,
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        token = create_access_token(data={"sub": str(new_user.id)})
        return AuthPayload(token=token, user=_map_user(new_user))

    @strawberry.mutation(description="Login a user")
    async def login(
        self,
        info: strawberry.Info,
        input: LoginInput,
    ) -> AuthResult:
        db: AsyncSession = info.context["db"]
        
        result = await db.execute(select(models.User).where(models.User.email == input.email))
        user = result.scalar_one_or_none()
        
        if not user or not user.password_hash or not verify_password(input.password, user.password_hash):
            return ValidationError(message="Invalid email or password")
            
        token = create_access_token(data={"sub": str(user.id)})
        return AuthPayload(token=token, user=_map_user(user))
