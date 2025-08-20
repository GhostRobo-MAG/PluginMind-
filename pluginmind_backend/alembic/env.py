"""
PluginMind Backend - Alembic Environment Configuration

Database migration environment setup for PluginMind AI processing platform.
Supports both PostgreSQL and SQLite with automatic schema detection.
"""

import asyncio
from logging.config import fileConfig
import os
import sys
from pathlib import Path

from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import AsyncEngine
from alembic import context

# Add the app directory to the Python path
app_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(app_dir))

# Import PluginMind models and configuration
from app.core.config import settings
from app.models.database import SQLModel

# Import all models to ensure they're registered with SQLModel
from app.models.database import (
    User,
    QueryLog,
    AnalysisResult,
    # Import any additional models as they're created
)

# Alembic Config object
config = context.config

# Interpret the config file for Python logging if present
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the database URL from environment
database_url = settings.DATABASE_URL
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)

# Set target metadata for autogenerate support
target_metadata = SQLModel.metadata


def get_url():
    """
    Get database URL from environment or configuration.
    Supports both sync and async database URLs.
    """
    url = os.getenv("DATABASE_URL", settings.DATABASE_URL)
    # Convert async URLs to sync for Alembic
    if url and url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql+asyncpg://", "postgresql://", 1)
    return url


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine,
    though an Engine is acceptable here as well. By skipping the Engine
    creation we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,  # Support SQLite
        compare_type=True,     # Compare column types
        compare_server_default=True,  # Compare server defaults
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Run migrations with the given connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_as_batch=True,  # Support SQLite
        compare_type=True,     # Compare column types
        compare_server_default=True,  # Compare server defaults
        # Include schemas in autogenerate
        include_schemas=True,
        # Custom naming convention
        render_item=render_item,
        # Process revision directives
        process_revision_directives=process_revision_directives,
    )

    with context.begin_transaction():
        context.run_migrations()


def render_item(type_, obj, autogen_context):
    """Custom rendering for migration items."""
    if type_ == "type" and hasattr(obj, "impl"):
        # Handle custom types
        return obj.impl.__class__.__name__
    return False


def process_revision_directives(context, revision, directives):
    """Process revision directives to customize migration generation."""
    if getattr(config.cmd_opts, "autogenerate", False):
        script = directives[0]
        if script.upgrade_ops.is_empty():
            directives[:] = []
            print("No changes detected - no migration created")


async def run_async_migrations():
    """
    Run migrations in async mode for databases that support it.
    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        do_run_migrations(connection)

    await connectable.dispose()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    In this scenario we need to create an Engine and associate a connection
    with the context. Supports both sync and async operations.
    """
    # Check if we're using an async engine
    database_url = get_url()
    if database_url and (
        database_url.startswith("postgresql+asyncpg://")
        or database_url.startswith("sqlite+aiosqlite://")
    ):
        # Run async migrations
        asyncio.run(run_async_migrations())
    else:
        # Run sync migrations
        configuration = config.get_section(config.config_ini_section)
        configuration["sqlalchemy.url"] = database_url

        connectable = engine_from_config(
            configuration,
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

        with connectable.connect() as connection:
            do_run_migrations(connection)


# Determine if we're running in offline or online mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()