"""GraphQL Mutations - Organization registration."""

import re
from typing import Annotated, Union

import strawberry
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import models
from app.graphql.queries.user import _map_org
from app.graphql.types.errors import AuthError, ValidationError
from app.graphql.types.user import OrgType


EMAIL_PATTERN = re.compile(r"^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$", re.IGNORECASE)
PHONE_PATTERN = re.compile(r"^(?:\+91)?[6-9]\d{9}$")


@strawberry.input
class RegisterOrgInput:
    name: str
    email: str
    phone_num: str


RegisterOrgResult = Annotated[
    Union[OrgType, AuthError, ValidationError],
    strawberry.union("RegisterOrgResult"),
]


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _normalize_phone(phone_num: str) -> str:
    return re.sub(r"[\s()-]", "", phone_num.strip())


def _validate_register_org_input(input: RegisterOrgInput) -> ValidationError | None:
    name = input.name.strip()
    email = _normalize_email(input.email)
    phone_num = _normalize_phone(input.phone_num)

    if len(name) < 2:
        return ValidationError(message="Organization name must be at least 2 characters long")
    if len(name) > 120:
        return ValidationError(message="Organization name must be 120 characters or fewer")
    if not EMAIL_PATTERN.fullmatch(email):
        return ValidationError(message="Enter a valid organization email address")
    if not PHONE_PATTERN.fullmatch(phone_num):
        return ValidationError(
            message="Enter a valid Indian phone number, with optional +91 country code"
        )

    return None


@strawberry.type
class OrgMutation:
    @strawberry.mutation(description="Register an organization for the current user.")
    async def register_org(
        self,
        info: strawberry.Info,
        input: RegisterOrgInput,
    ) -> RegisterOrgResult:
        db: AsyncSession = info.context["db"]
        current_user: models.User | None = info.context.get("current_user")
        if not current_user:
            return AuthError(message="Authentication required")

        validation_error = _validate_register_org_input(input)
        if validation_error:
            return validation_error

        existing_owner_result = await db.execute(
            select(models.Org).where(models.Org.owner_user_id == current_user.id)
        )
        if existing_owner_result.scalar_one_or_none():
            return ValidationError(message="Current user already owns an organization")

        email = _normalize_email(input.email)
        existing_email_result = await db.execute(
            select(models.Org).where(models.Org.email == email)
        )
        if existing_email_result.scalar_one_or_none():
            return ValidationError(message="Organization email already registered")

        org = models.Org(
            name=input.name.strip(),
            email=email,
            phone_num=_normalize_phone(input.phone_num),
            owner_user_id=current_user.id,
            approval_status=models.OrgApprovalEnum.pending_approval,
        )
        current_user.role = models.RoleEnum.org_admin

        db.add(org)
        db.add(current_user)
        await db.commit()
        await db.refresh(org)
        return _map_org(org)
