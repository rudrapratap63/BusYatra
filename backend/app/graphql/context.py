"""
GraphQL Context
Runs once per request and injects db session + current user into every resolver.

REST equivalent: FastAPI's Depends() on each route.
In GraphQL: one central context_getter for the whole schema.
"""

from fastapi import Request, Response, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator

from app.api.deps import get_db
from app.db import models


import jwt
import uuid
from sqlalchemy import select
from app.core.config import settings

async def get_current_user_from_request(
    request: Request,
    db: AsyncSession,
) -> models.User | None:
    """
    Extract and validate auth token from the auth cookie.
    Returns the user object or None if not authenticated.
    """
    token = request.cookies.get(settings.AUTH_COOKIE_NAME)
    auth_header = request.headers.get("Authorization", "")
    if not token and auth_header.startswith("Bearer "):
        token = auth_header[7:]
    if not token:
        return None

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id:
            result = await db.execute(select(models.User).where(models.User.id == uuid.UUID(user_id)))
            return result.scalar_one_or_none()
    except (ValueError, jwt.PyJWTError):
        return None
    return None


async def get_graphql_context(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    The context getter — called once per GraphQL request.
    Returns a dict accessible in every resolver via `info.context`.
    
    Usage in resolvers:
        db = info.context["db"]
        current_user = info.context["current_user"]   # None if not logged in
        request = info.context["request"]
    """
    current_user = await get_current_user_from_request(request, db)
    return {
        "request": request,
        "response": response,
        "db": db,
        "current_user": current_user,
    }
