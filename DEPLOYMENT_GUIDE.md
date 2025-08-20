# PluginMind Deployment Guide

**Complete deployment guide for the PluginMind AI processing platform**

## 📋 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+ (or SQLite for development)
- Redis 7+ (optional, for caching)
- Docker & Docker Compose (recommended)

### 1. Clone and Setup

```bash
git clone <your-repo>
cd PluginMind/pluginmind_backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.template .env

# Edit configuration
nano .env  # Add your API keys and database URL

# Validate configuration
python scripts/validate_env.py validate
```

### 3. Database Setup

```bash
# Run database migrations
python scripts/manage_db.py upgrade

# Verify database connection
python scripts/validate_env.py check-services
```

### 4. Start Development Server

```bash
# Development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
gunicorn app.main:app --config gunicorn_conf.py
```

---

## 🐳 Docker Deployment (Recommended)

### Quick Docker Setup

```bash
# Copy Docker environment template
cp .env.docker .env

# Edit with your configuration
nano .env

# Start full stack
docker-compose up -d

# Check service health
docker-compose ps
curl http://localhost:8000/health
```

### Production Docker Deployment

```bash
# Production build
DOCKER_TARGET=production docker-compose up -d

# Scale services
docker-compose up -d --scale backend=3

# Monitor logs
docker-compose logs -f backend
```

---

## 🚀 Production Deployment

### Environment Setup

1. **Copy production environment template:**
```bash
cp .env.production .env.prod
```

2. **Configure required variables:**
```bash
# Database (PostgreSQL recommended)
DATABASE_URL=postgresql://user:pass@host:5432/pluginmind_prod

# AI Service API Keys
OPENAI_API_KEY=sk-proj-your-key-here
GROK_API_KEY=xai-your-key-here

# Authentication
GOOGLE_CLIENT_ID=your-id.apps.googleusercontent.com
JWT_SECRET=$(openssl rand -base64 32)

# Security
CORS_ORIGINS=https://yourdomain.com
TLS_ENABLED=true
```

3. **Validate production configuration:**
```bash
python scripts/validate_env.py validate --env-file .env.prod --strict
python scripts/validate_env.py security-check
```

### Database Migration

```bash
# Production database setup
export DATABASE_URL="postgresql://user:pass@host:5432/pluginmind_prod"

# Run migrations
python scripts/manage_db.py upgrade

# Verify migration
python scripts/manage_db.py current
```

### Application Deployment

#### Option 1: Docker Production
```bash
# Build and deploy with Docker
DOCKER_TARGET=production docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Health check
curl -f https://yourdomain.com/health
```

#### Option 2: Direct Deployment
```bash
# Install production dependencies
pip install -r requirements.txt gunicorn

# Run database migrations
python scripts/manage_db.py upgrade

# Start with Gunicorn
gunicorn app.main:app --config gunicorn_conf.py
```

---

## 🔧 Configuration Guide

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `postgresql://user:pass@host:5432/db` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-proj-...` |
| `GROK_API_KEY` | Grok API key | `xai-...` |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | `123.apps.googleusercontent.com` |
| `JWT_SECRET` | JWT signing secret (base64) | `base64-encoded-secret` |
| `CORS_ORIGINS` | Allowed origins (comma-separated) | `https://app.com,https://admin.com` |

### Optional Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `REDIS_URL` | Redis connection for caching | `memory` |
| `LOG_LEVEL` | Logging level | `info` |
| `WEB_CONCURRENCY` | Gunicorn workers | `4` |
| `RATE_LIMIT_REQUESTS_PER_MINUTE` | API rate limiting | `60` |

### Feature Flags

Enable/disable specific features:

```bash
FEATURE_DOCUMENT_SUMMARIZER=true
FEATURE_CHATBOT_BACKEND=true
FEATURE_SEO_GENERATOR=true
FEATURE_ANALYTICS_TRACKING=false
```

---

## 📊 Monitoring & Health Checks

### Health Check Endpoints

| Endpoint | Purpose | Description |
|----------|---------|-------------|
| `/health` | General health | Basic application status |
| `/ready` | Readiness probe | Database and dependencies |
| `/live` | Liveness probe | Application responsiveness |
| `/services` | AI services status | AI service registry health |

### Monitoring Setup

```bash
# Health check script
curl -f http://localhost:8000/health || exit 1

# Service status
curl -s http://localhost:8000/services | jq

# Database health
python scripts/validate_env.py check-services
```

### Logging Configuration

```bash
# Production logging
LOG_LEVEL=warning
LOG_FORMAT=json
LOG_FILE_ENABLED=true
LOG_FILE_PATH=/var/log/pluginmind/app.log

# OpenTelemetry monitoring
OTEL_ENABLED=true
OTEL_SERVICE_NAME=pluginmind-backend
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
```

---

## 🔒 Security Best Practices

### 1. Environment Security

```bash
# Generate secure JWT secret
JWT_SECRET=$(openssl rand -base64 32 | base64)

# Restrict CORS origins
CORS_ORIGINS=https://yourdomain.com

# Enable security headers
SECURITY_HEADERS_ENABLED=true
CSP_ENABLED=true
```

### 2. TLS Configuration

```bash
# Enable TLS
TLS_ENABLED=true
TLS_CERT_PATH=/etc/ssl/certs/pluginmind.crt
TLS_KEY_PATH=/etc/ssl/private/pluginmind.key
```

### 3. Database Security

```bash
# Use PostgreSQL with SSL
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require

# Connection pooling limits
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
```

### 4. Rate Limiting

```bash
# Production rate limits
RATE_LIMIT_REQUESTS_PER_MINUTE=120
RATE_LIMIT_BURST_SIZE=20
RATE_LIMIT_STORAGE=redis
```

---

## 🚨 Troubleshooting

### Common Issues

#### Database Connection Error
```bash
# Check database connectivity
python scripts/validate_env.py check-services

# Verify database URL format
echo $DATABASE_URL

# Test direct connection
psql $DATABASE_URL -c "SELECT 1"
```

#### API Key Issues
```bash
# Validate API key configuration
python scripts/validate_env.py validate

# Test AI service connectivity
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models
```

#### Docker Issues
```bash
# Check container health
docker-compose ps

# View container logs
docker-compose logs backend

# Restart services
docker-compose restart backend
```

### Performance Issues

#### Slow Response Times
```bash
# Check database performance
python scripts/manage_db.py current

# Monitor resource usage
docker stats pluginmind-backend

# Review logs
tail -f /var/log/pluginmind/app.log
```

#### High Memory Usage
```bash
# Adjust worker configuration
WEB_CONCURRENCY=2
WORKER_CONNECTIONS=500

# Enable connection pooling
DATABASE_POOL_SIZE=5
```

---

## 🔄 Maintenance

### Database Maintenance

```bash
# Create database backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Run database migrations
python scripts/manage_db.py upgrade

# Check migration status
python scripts/manage_db.py current
```

### Log Rotation

```bash
# Configure log rotation
LOG_ROTATION_SIZE=100MB
LOG_RETENTION_DAYS=30

# Manual log cleanup
find /var/log/pluginmind -name "*.log" -mtime +30 -delete
```

### Health Monitoring

```bash
# Automated health checks
*/5 * * * * curl -f http://localhost:8000/health || echo "Health check failed"

# Service monitoring
*/1 * * * * docker-compose ps | grep -q "Up" || docker-compose restart
```

---

## 🏗️ Scaling

### Horizontal Scaling

```bash
# Scale backend instances
docker-compose up -d --scale backend=5

# Load balancer configuration
# Add nginx or traefik proxy configuration
```

### Database Scaling

```bash
# Read replicas
DATABASE_READ_URL=postgresql://user:pass@read-host:5432/db

# Connection pool optimization
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
```

### Caching

```bash
# Enable Redis caching
REDIS_URL=redis://redis-cluster:6379/0
CACHE_DEFAULT_TTL=3600
CACHE_AI_RESULTS_TTL=7200
```

---

## 📈 Performance Optimization

### Application Tuning

```bash
# Gunicorn optimization
WEB_CONCURRENCY=8
WORKER_CONNECTIONS=1000
MAX_REQUESTS=2000

# Request timeouts
REQUEST_TIMEOUT=60
AI_SERVICE_TIMEOUT=180
```

### Database Optimization

```bash
# Connection pool tuning
DATABASE_POOL_SIZE=15
DATABASE_POOL_TIMEOUT=30

# Query optimization
# Enable query logging and analysis
```

### Caching Strategy

```bash
# AI result caching
CACHE_AI_RESULTS_TTL=14400  # 4 hours

# User session caching
CACHE_USER_SESSION_TTL=28800  # 8 hours
```

---

## 🆘 Support

### Getting Help

1. **Check logs**: `/var/log/pluginmind/app.log`
2. **Validate environment**: `python scripts/validate_env.py validate --strict`
3. **Test services**: `python scripts/validate_env.py check-services`
4. **Security check**: `python scripts/validate_env.py security-check`

### Emergency Procedures

```bash
# Emergency restart
docker-compose restart backend

# Database rollback
python scripts/manage_db.py downgrade <previous-revision>

# Service health recovery
curl -X POST http://localhost:8000/admin/restart-services
```

---

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Gunicorn Configuration](https://docs.gunicorn.org/en/stable/settings.html)
- [Docker Compose Reference](https://docs.docker.com/compose/)

---

**PluginMind v1.0.0** - Production-ready AI processing platform