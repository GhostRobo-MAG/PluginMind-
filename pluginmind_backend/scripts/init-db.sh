#!/bin/bash
# PluginMind Database Initialization Script
# Executed by PostgreSQL container during first startup

set -e

echo "🗄️  Initializing PluginMind database..."

# Create database if it doesn't exist
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Create extensions if needed
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "citext";
    
    -- Grant permissions
    GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO $POSTGRES_USER;
    
    -- Create schemas for organization
    CREATE SCHEMA IF NOT EXISTS public;
    CREATE SCHEMA IF NOT EXISTS logs;
    
    -- Set default search path
    ALTER DATABASE $POSTGRES_DB SET search_path TO public, logs;
EOSQL

echo "✅ Database initialization complete!"