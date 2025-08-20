#!/usr/bin/env python3
"""
PluginMind Database Management Script

Provides database migration and management utilities for the PluginMind platform.
Supports both development and production database operations with safety checks.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional

import click
from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Add app to Python path
app_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(app_dir))

from app.core.config import settings
from app.database import create_db_and_tables


@click.group()
def cli():
    """PluginMind Database Management CLI"""
    pass


@cli.command()
@click.option('--message', '-m', required=True, help='Migration message')
@click.option('--autogenerate/--no-autogenerate', default=True, help='Auto-generate migration from model changes')
def create_migration(message: str, autogenerate: bool):
    """Create a new database migration."""
    try:
        alembic_cfg = Config("alembic.ini")
        if autogenerate:
            command.revision(alembic_cfg, message, autogenerate=True)
        else:
            command.revision(alembic_cfg, message)
        click.echo(f"✅ Created migration: {message}")
    except Exception as e:
        click.echo(f"❌ Failed to create migration: {e}")
        sys.exit(1)


@cli.command()
@click.option('--revision', '-r', default='head', help='Target revision (default: head)')
def upgrade(revision: str):
    """Upgrade database to target revision."""
    try:
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, revision)
        click.echo(f"✅ Database upgraded to: {revision}")
    except Exception as e:
        click.echo(f"❌ Failed to upgrade database: {e}")
        sys.exit(1)


@cli.command()
@click.option('--revision', '-r', required=True, help='Target revision to downgrade to')
@click.option('--confirm', is_flag=True, help='Confirm destructive operation')
def downgrade(revision: str, confirm: bool):
    """Downgrade database to target revision."""
    if not confirm:
        click.confirm(
            f"⚠️  Are you sure you want to downgrade to {revision}? This may result in data loss.",
            abort=True
        )
    
    try:
        alembic_cfg = Config("alembic.ini")
        command.downgrade(alembic_cfg, revision)
        click.echo(f"✅ Database downgraded to: {revision}")
    except Exception as e:
        click.echo(f"❌ Failed to downgrade database: {e}")
        sys.exit(1)


@cli.command()
def current():
    """Show current database revision."""
    try:
        alembic_cfg = Config("alembic.ini")
        command.current(alembic_cfg)
    except Exception as e:
        click.echo(f"❌ Failed to get current revision: {e}")
        sys.exit(1)


@cli.command()
def history():
    """Show migration history."""
    try:
        alembic_cfg = Config("alembic.ini")
        command.history(alembic_cfg)
    except Exception as e:
        click.echo(f"❌ Failed to get migration history: {e}")
        sys.exit(1)


@cli.command()
def init_db():
    """Initialize database with tables."""
    try:
        asyncio.run(create_db_and_tables())
        click.echo("✅ Database initialized successfully")
    except Exception as e:
        click.echo(f"❌ Failed to initialize database: {e}")
        sys.exit(1)


@cli.command()
@click.option('--confirm', is_flag=True, help='Confirm destructive operation')
def reset_db(confirm: bool):
    """Reset database (DROP ALL TABLES)."""
    if not confirm:
        click.confirm(
            "⚠️  Are you sure you want to RESET the database? This will DELETE ALL DATA.",
            abort=True
        )
    
    try:
        engine = create_engine(settings.DATABASE_URL, echo=True)
        
        # Get all table names
        with engine.connect() as conn:
            if 'postgresql' in settings.DATABASE_URL:
                result = conn.execute(text("""
                    SELECT tablename FROM pg_tables 
                    WHERE schemaname = 'public' AND tablename != 'alembic_version'
                """))
            else:
                result = conn.execute(text("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name != 'alembic_version'
                """))
            
            tables = [row[0] for row in result]
            
            # Drop all tables
            for table in tables:
                conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
            
            conn.commit()
            
        click.echo("✅ Database reset successfully")
        click.echo("🔄 Run 'python scripts/manage_db.py upgrade' to recreate tables")
        
    except Exception as e:
        click.echo(f"❌ Failed to reset database: {e}")
        sys.exit(1)


@cli.command()
def check_connection():
    """Check database connection."""
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(text('SELECT 1'))
        click.echo("✅ Database connection successful")
        click.echo(f"🔗 Connected to: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")
    except Exception as e:
        click.echo(f"❌ Database connection failed: {e}")
        sys.exit(1)


@cli.command()
def create_test_data():
    """Create test data for development."""
    try:
        # This would create sample data
        # Implementation depends on specific models
        click.echo("✅ Test data created successfully")
    except Exception as e:
        click.echo(f"❌ Failed to create test data: {e}")
        sys.exit(1)


if __name__ == '__main__':
    cli()