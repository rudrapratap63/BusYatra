"""
GraphQL Mutations — User Profile
REST equivalent: PATCH /me

Mutations = write operations (create, update, delete).
They always have:
  1. An @strawberry.input class (the input shape)
  2. A resolver method that does the work and returns a type
"""

import strawberry
import re
from typing import Annotated, Optional, Union
from fastapi import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db import models
from app.graphql.types.user import UserType
from app.graphql.types.errors import AuthError, ValidationError
from app.graphql.queries.user import _map_user
from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import settings


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
    token: Optional[str] = None
    user: UserType


UpdateProfileResult = Annotated[
    Union[UserType, AuthError],
    strawberry.union("UpdateProfileResult"),
]

AuthResult = Annotated[
    Union[AuthPayload, ValidationError],
    strawberry.union("AuthResult"),
]

EMAIL_PATTERN = re.compile(r"^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$", re.IGNORECASE)
PHONE_PATTERN = re.compile(r"^(?:\+91)?[6-9]\d{9}$")
PASSWORD_SYMBOL_PATTERN = re.compile(r"[^A-Za-z0-9]")


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _normalize_phone(phone_num: str) -> str:
    return re.sub(r"[\s()-]", "", phone_num.strip())


def _validate_register_input(input: RegisterInput) -> ValidationError | None:
    email = _normalize_email(input.email)
    phone_num = _normalize_phone(input.phone_num)
    password = input.password

    if not EMAIL_PATTERN.fullmatch(email):
        return ValidationError(message="Enter a valid email address")

    if not PHONE_PATTERN.fullmatch(phone_num):
        return ValidationError(
            message="Enter a valid Indian phone number, with optional +91 country code"
        )

    if len(password) < 8:
        return ValidationError(message="Password must be at least 8 characters long")
    if len(password) > 128:
        return ValidationError(message="Password must be 128 characters or fewer")
    if not any(char.islower() for char in password):
        return ValidationError(message="Password must include a lowercase letter")
    if not any(char.isupper() for char in password):
        return ValidationError(message="Password must include an uppercase letter")
    if not any(char.isdigit() for char in password):
        return ValidationError(message="Password must include a number")
    if not PASSWORD_SYMBOL_PATTERN.search(password):
        return ValidationError(message="Password must include a symbol")

    if input.role not in (None, models.RoleEnum.user.value):
        return ValidationError(message="Role assignment is restricted to admins")

    return None


def _set_auth_cookie(info: strawberry.Info, token: str) -> None:
    response: Response = info.context["response"]
    response.set_cookie(
        key=settings.AUTH_COOKIE_NAME,
        value=token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        domain=settings.AUTH_COOKIE_DOMAIN,
        path="/",
    )


def _clear_auth_cookie(info: strawberry.Info) -> None:
    response: Response = info.context["response"]
    response.delete_cookie(
        key=settings.AUTH_COOKIE_NAME,
        domain=settings.AUTH_COOKIE_DOMAIN,
        path="/",
        samesite=settings.AUTH_COOKIE_SAMESITE,
        secure=settings.AUTH_COOKIE_SECURE,
        httponly=True,
    )


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
        validation_error = _validate_register_input(input)
        if validation_error:
            return validation_error

        email = _normalize_email(input.email)
        phone_num = _normalize_phone(input.phone_num)
        
        # Check if email is already taken
        result = await db.execute(select(models.User).where(models.User.email == email))
        if result.scalar_one_or_none():
            return ValidationError(message="Email already registered")

        hashed_pwd = hash_password(input.password)
        
        new_user = models.User(
            email=email,
            password_hash=hashed_pwd,
            phone_num=phone_num,
            name=input.name,
            role=models.RoleEnum.user,
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        token = create_access_token(data={"sub": str(new_user.id)})
        _set_auth_cookie(info, token)
        return AuthPayload(user=_map_user(new_user))

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
        _set_auth_cookie(info, token)
        return AuthPayload(user=_map_user(user))

    @strawberry.mutation(description="Logout the current user")
    async def logout(self, info: strawberry.Info) -> bool:
        _clear_auth_cookie(info)
        return True
