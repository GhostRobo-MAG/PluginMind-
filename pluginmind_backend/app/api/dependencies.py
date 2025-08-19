"""
FastAPI dependencies for route handlers.

Provides reusable dependencies for database sessions, authentication,
and other common requirements across API endpoints.
"""

from typing import Annotated
from fastapi import Depends
from sqlmodel import Session
from app.database import get_session
from app.middleware.auth import UserDep, OptionalUserDep

# Database session dependency
SessionDep = Annotated[Session, Depends(get_session)]

# Export auth dependencies for easier imports
__all__ = ["SessionDep", "UserDep", "OptionalUserDep"]