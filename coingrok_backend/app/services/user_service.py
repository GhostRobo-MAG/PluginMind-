"""
User management service for authentication and profile management.

Handles user creation, lookup, and profile management for Google OAuth users
via Supabase integration.
"""

from typing import Optional
from sqlmodel import Session, select
from app.models.database import User
from app.core.logging import get_logger

logger = get_logger(__name__)


class UserService:
    """
    Service for user management operations.
    
    Handles user creation, lookup, and profile updates with proper
    duplicate prevention and default value initialization.
    """
    
    def get_or_create_user(
        self,
        session: Session,
        user_id: str,
        email: Optional[str] = None
    ) -> User:
        """
        Get existing user or create new user with default values.
        
        Looks up user by google_id first, then by email if provided.
        Creates new user with default subscription and usage limits if not found.
        
        Args:
            session: Database session
            user_id: User identifier from JWT token (usually from 'sub' claim)
            email: User email from JWT token (optional fallback)
            
        Returns:
            User: Existing or newly created user model
        """
        # Try to find user by google_id first
        statement = select(User).where(User.google_id == user_id)
        user = session.exec(statement).first()
        
        if user:
            logger.debug(f"Found existing user by google_id: {user_id}")
            return user
        
        # If not found by google_id and email provided, try by email
        if email:
            statement = select(User).where(User.email == email)
            user = session.exec(statement).first()
            
            if user:
                # Update existing user with google_id if missing
                if not user.google_id:
                    user.google_id = user_id
                    session.add(user)
                    session.commit()
                    session.refresh(user)
                    logger.info(f"Updated existing user with google_id: {email}")
                
                return user
        
        # Create new user with default values
        new_user = User(
            email=email or f"user_{user_id}@unknown.com",
            google_id=user_id,
            subscription_tier="free",
            queries_used=0,
            queries_limit=10,
            is_active=True
        )
        
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        
        logger.info(f"Created new user: {new_user.email} (google_id: {user_id})")
        return new_user
    
    def get_user_by_id(self, session: Session, user_id: str) -> Optional[User]:
        """
        Get user by google_id.
        
        Args:
            session: Database session
            user_id: Google user ID
            
        Returns:
            Optional[User]: User model if found, None otherwise
        """
        statement = select(User).where(User.google_id == user_id)
        return session.exec(statement).first()
    
    def increment_user_queries(self, session: Session, user: User) -> User:
        """
        Increment user's query count.
        
        Args:
            session: Database session
            user: User model to update
            
        Returns:
            User: Updated user model
        """
        user.queries_used += 1
        session.add(user)
        session.commit()
        session.refresh(user)
        
        logger.debug(f"Incremented queries for user {user.email}: {user.queries_used}/{user.queries_limit}")
        return user
    
    def check_query_limit(self, user: User) -> bool:
        """
        Check if user has exceeded query limit.
        
        Args:
            user: User model to check
            
        Returns:
            bool: True if user can make more queries, False if limit exceeded
        """
        return user.queries_used < user.queries_limit


# Global user service instance
user_service = UserService()