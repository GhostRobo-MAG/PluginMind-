"""
Database connection and session management.

Provides SQLModel engine creation, session management, and database
initialization functions for the PluginMind Backend.
"""

from sqlmodel import SQLModel, Session, create_engine
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Create database engine with configuration from settings
engine = create_engine(
    settings.database_url,
    connect_args=settings.connect_args,
    echo=settings.debug,  # Log SQL queries in debug mode
)


def create_db_and_tables():
    """
    Create database tables if they don't exist.
    
    This function is called during application startup to ensure
    all required tables are present in the database.
    """
    try:
        # Import all models to register them with SQLModel metadata
        from app.models.database import User, AnalysisJob, QueryLog, AnalysisResult  # noqa: F401
        
        logger.info(f"Creating database tables: {list(SQLModel.metadata.tables.keys())}")
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        raise


def get_session():
    """
    Dependency to get database session.
    
    Provides a database session for FastAPI dependency injection.
    Sessions are automatically closed after request completion.
    
    Yields:
        Session: SQLModel database session
    """
    with Session(engine) as session:
        yield session