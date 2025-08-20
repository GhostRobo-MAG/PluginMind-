#!/usr/bin/env python3
"""
PluginMind Environment Validation Script

Validates environment configuration and provides deployment readiness checks.
Ensures all required settings are present and properly configured.
"""

import os
import sys
import re
import base64
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import click
from urllib.parse import urlparse

# Add app to Python path
app_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(app_dir))


def validate_database_url(url: str) -> Tuple[bool, str]:
    """Validate database URL format and accessibility."""
    try:
        parsed = urlparse(url)
        if not parsed.scheme:
            return False, "Database URL missing scheme (postgresql:// or sqlite://)"
        
        if parsed.scheme not in ['postgresql', 'sqlite', 'postgresql+asyncpg', 'sqlite+aiosqlite']:
            return False, f"Unsupported database scheme: {parsed.scheme}"
        
        if parsed.scheme.startswith('postgresql'):
            if not parsed.hostname:
                return False, "PostgreSQL URL missing hostname"
            if not parsed.username:
                return False, "PostgreSQL URL missing username"
            if not parsed.password:
                return False, "PostgreSQL URL missing password"
            if not parsed.path or parsed.path == '/':
                return False, "PostgreSQL URL missing database name"
        
        return True, "Database URL format valid"
    
    except Exception as e:
        return False, f"Invalid database URL: {str(e)}"


def validate_jwt_secret(secret: str) -> Tuple[bool, str]:
    """Validate JWT secret format and strength."""
    if not secret:
        return False, "JWT secret is required"
    
    try:
        # Try to decode as base64
        decoded = base64.b64decode(secret)
        if len(decoded) < 32:
            return False, "JWT secret too short (minimum 32 bytes after base64 decode)"
        return True, f"JWT secret valid ({len(decoded)} bytes)"
    
    except Exception:
        # Check if it's a plain string (not recommended for production)
        if len(secret) < 32:
            return False, "JWT secret too short (minimum 32 characters)"
        return True, f"JWT secret valid (plain string, {len(secret)} chars)"


def validate_api_key(key: str, service: str) -> Tuple[bool, str]:
    """Validate API key format for different services."""
    if not key or key in ['your-key-here', 'test-key']:
        return False, f"{service} API key not set or using placeholder"
    
    # Service-specific validation patterns
    patterns = {
        'OpenAI': r'^sk-[A-Za-z0-9]{32,}$',
        'Grok': r'^xai-[A-Za-z0-9\-]{20,}$',
    }
    
    if service in patterns:
        if not re.match(patterns[service], key):
            return False, f"{service} API key format appears invalid"
    
    return True, f"{service} API key format valid"


def validate_cors_origins(origins: str) -> Tuple[bool, str]:
    """Validate CORS origins format."""
    if not origins:
        return False, "CORS origins not configured"
    
    origin_list = [origin.strip() for origin in origins.split(',')]
    
    for origin in origin_list:
        if not origin.startswith(('http://', 'https://')):
            return False, f"Invalid CORS origin format: {origin}"
    
    return True, f"CORS origins valid ({len(origin_list)} origins)"


def check_environment_requirements(env_type: str) -> List[Dict]:
    """Check environment-specific requirements."""
    checks = []
    
    # Required for all environments
    required_vars = [
        ('DATABASE_URL', validate_database_url),
        ('JWT_SECRET', validate_jwt_secret),
        ('CORS_ORIGINS', validate_cors_origins),
    ]
    
    # API keys (required for production, optional for development)
    api_key_vars = [
        ('OPENAI_API_KEY', lambda k: validate_api_key(k, 'OpenAI')),
        ('GROK_API_KEY', lambda k: validate_api_key(k, 'Grok')),
    ]
    
    # Environment-specific requirements
    if env_type == 'production':
        # Strict requirements for production
        required_vars.extend(api_key_vars)
        required_vars.append(('GOOGLE_CLIENT_ID', lambda x: (bool(x and x != 'test-client-id'), 'Google Client ID')))
    else:
        # More lenient for development
        for var, validator in api_key_vars:
            value = os.getenv(var, '')
            is_valid, message = validator(value)
            checks.append({
                'name': var,
                'status': 'warning' if not is_valid else 'success',
                'message': message if not is_valid else f"{var} configured",
                'required': False
            })
    
    # Check required variables
    for var_name, validator in required_vars:
        value = os.getenv(var_name, '')
        is_valid, message = validator(value)
        
        checks.append({
            'name': var_name,
            'status': 'success' if is_valid else 'error',
            'message': message,
            'required': True
        })
    
    return checks


@click.group()
def cli():
    """PluginMind Environment Validation CLI"""
    pass


@cli.command()
@click.option('--env-file', '-e', help='Environment file to load')
@click.option('--strict', is_flag=True, help='Strict validation mode')
def validate(env_file: Optional[str], strict: bool):
    """Validate current environment configuration."""
    
    # Load environment file if specified
    if env_file:
        from dotenv import load_dotenv
        if Path(env_file).exists():
            load_dotenv(env_file)
            click.echo(f"📁 Loaded environment from: {env_file}")
        else:
            click.echo(f"❌ Environment file not found: {env_file}")
            return
    
    # Detect environment type
    env_type = os.getenv('ENVIRONMENT', 'development').lower()
    click.echo(f"🔍 Validating {env_type} environment configuration")
    click.echo()
    
    # Run validation checks
    checks = check_environment_requirements(env_type)
    
    # Display results
    success_count = 0
    warning_count = 0
    error_count = 0
    
    for check in checks:
        status_icon = {
            'success': '✅',
            'warning': '⚠️ ',
            'error': '❌'
        }[check['status']]
        
        click.echo(f"{status_icon} {check['name']}: {check['message']}")
        
        if check['status'] == 'success':
            success_count += 1
        elif check['status'] == 'warning':
            warning_count += 1
        else:
            error_count += 1
    
    # Summary
    click.echo()
    click.echo("📊 Validation Summary:")
    click.echo(f"  ✅ Passed: {success_count}")
    if warning_count > 0:
        click.echo(f"  ⚠️  Warnings: {warning_count}")
    if error_count > 0:
        click.echo(f"  ❌ Errors: {error_count}")
    
    # Deployment readiness
    click.echo()
    if error_count == 0:
        if warning_count == 0:
            click.echo("🚀 Environment ready for deployment!")
        else:
            click.echo("⚠️  Environment has warnings but may be deployable")
    else:
        click.echo("❌ Environment not ready for deployment - fix errors first")
        sys.exit(1)


@cli.command()
@click.argument('environment', type=click.Choice(['development', 'staging', 'production']))
def template(environment: str):
    """Generate environment template for specific deployment type."""
    
    template_files = {
        'development': '.env.development',
        'staging': '.env.production',  # Use production template as base
        'production': '.env.production'
    }
    
    source_file = template_files[environment]
    target_file = f'.env.{environment}'
    
    if Path(source_file).exists():
        with open(source_file, 'r') as f:
            content = f.read()
        
        with open(target_file, 'w') as f:
            f.write(content)
        
        click.echo(f"✅ Environment template created: {target_file}")
        click.echo(f"📝 Edit {target_file} with your specific configuration")
    else:
        click.echo(f"❌ Template source not found: {source_file}")


@cli.command()
def check_services():
    """Check connectivity to external services."""
    click.echo("🔍 Checking external service connectivity...")
    
    # Database connectivity
    try:
        from app.core.config import settings
        from sqlalchemy import create_engine
        
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        click.echo("✅ Database: Connected successfully")
    except Exception as e:
        click.echo(f"❌ Database: Connection failed - {str(e)}")
    
    # Redis connectivity (if configured)
    redis_url = os.getenv('REDIS_URL')
    if redis_url:
        try:
            import redis
            r = redis.from_url(redis_url)
            r.ping()
            click.echo("✅ Redis: Connected successfully")
        except Exception as e:
            click.echo(f"❌ Redis: Connection failed - {str(e)}")
    
    click.echo()
    click.echo("🏥 Service health check completed")


@cli.command()
def security_check():
    """Perform security configuration check."""
    click.echo("🔒 Security Configuration Check")
    click.echo()
    
    security_issues = []
    
    # Check JWT secret strength
    jwt_secret = os.getenv('JWT_SECRET', '')
    if not jwt_secret or len(jwt_secret) < 32:
        security_issues.append("Weak JWT secret - use at least 32 characters")
    
    # Check debug mode in production
    if os.getenv('ENVIRONMENT') == 'production' and os.getenv('DEBUG', '').lower() == 'true':
        security_issues.append("Debug mode enabled in production - security risk")
    
    # Check CORS configuration
    cors_origins = os.getenv('CORS_ORIGINS', '')
    if '*' in cors_origins:
        security_issues.append("Wildcard CORS origins - potential security risk")
    
    # Check HTTPS enforcement
    if os.getenv('ENVIRONMENT') == 'production' and os.getenv('TLS_ENABLED', '').lower() != 'true':
        security_issues.append("TLS not enabled in production")
    
    if security_issues:
        click.echo("❌ Security issues found:")
        for issue in security_issues:
            click.echo(f"  - {issue}")
    else:
        click.echo("✅ No security issues detected")


if __name__ == '__main__':
    cli()