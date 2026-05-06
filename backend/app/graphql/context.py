"""
GraphQL Context
Runs once per request and injects db session + current user into every resolver.

REST equivalent: FastAPI's Depends() on each route.
In GraphQL: one central context_getter for the whole schema.
"""

from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator

from app.api.deps import get_db
from app.db import models


async def get_current_user_from_request(
    request: Request,
    db: AsyncSession,
) -> models.User | None:
    """
    Extract and validate auth token from request headers.
    Returns the user object or None if not authenticated.
    
    TODO: Implement real JWT validation here.
    For now returns None (unauthenticated).
    """
    # Example: Bearer token check
    # auth_header = request.headers.get("Authorization", "")
    # if auth_header.startswith("Bearer "):
    #     token = auth_header[7:]
    #     user = await verify_jwt_and_get_user(token, db)
    #     return user
    return None


async def get_graphql_context(
    request: Request,
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
        "db": db,
        "current_user": current_user,
    }
