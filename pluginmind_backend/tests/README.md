# Test Suite

This directory contains tests for the PluginMind Backend API.

## Test Files

- `test_middleware.py` - Tests middleware configuration, order, CORS, and security headers
- `test_production_mode.py` - Tests production configuration requirements  
- `test_jwt_security.py` - **Comprehensive JWT authentication security tests**
- `test_rate_limit.py` - Tests dual enforcement rate limiting with IP extraction and token buckets
- `test_error_handling.py` - **Tests unified error handling system and exception mapping**
- `test_error_integration.py` - **Integration tests for complete error handling flow**
- `test_ai_service_registry.py` - **Comprehensive AI service registry and plugin system tests**

## Running Tests

### Standalone
```bash
# Run middleware tests
python tests/test_middleware.py

# Run production config tests  
python tests/test_production_mode.py

# Run error handling tests
python tests/test_error_handling.py

# Run error integration tests
python tests/test_error_integration.py

# Run rate limiting tests
python tests/test_rate_limit.py

# Run AI service registry tests
python tests/test_ai_service_registry.py
```

### With pytest (if installed)
```bash
pytest tests/
```

## Environment Requirements

Tests set their own environment variables for isolated testing:
- `DEBUG=true` for development mode testing
- `OPENAI_API_KEY`, `GROK_API_KEY`, `GOOGLE_CLIENT_ID` set to dummy values
- `DATABASE_URL` set to test SQLite database

## Test Coverage

### Middleware & Configuration
- ✅ Middleware execution order verification
- ✅ CORS behavior with allowed/blocked origins  
- ✅ Security headers presence
- ✅ Ambient JWT auth parsing (non-blocking)
- ✅ Protected route enforcement
- ✅ Production CORS_ORIGINS requirement
- ✅ Development mode fallbacks

### JWT Authentication Security
- ✅ Error message sanitization (prevents info disclosure)
- ✅ PII removal from debug logs
- ✅ Dynamic issuer discovery with fallback
- ✅ Enhanced configuration validation
- ✅ Attack vector prevention (algorithm confusion, token injection)
- ✅ Bearer-only token parsing validation

### Rate Limiting
- ✅ Token bucket algorithm implementation
- ✅ Dual enforcement (user + IP limits for authenticated users)
- ✅ Hardened IP extraction with IPv4/IPv6 validation
- ✅ Concurrent access and thread safety
- ✅ Rate limit headers and retry-after functionality
- ✅ Configuration override support

### Error Handling
- ✅ **Single source of truth exception mapping**
- ✅ **Unified error envelope format consistency**
- ✅ **Custom exception → HTTP status code mapping**
- ✅ **Correlation ID tracking in all responses**
- ✅ **Message sanitization and security validation**
- ✅ **HTTPException fallback handling**
- ✅ **Integration testing across all endpoints**

### AI Service Registry System
- ✅ **Service registration and discovery by type/capability**
- ✅ **Health checking system for all AI services**
- ✅ **Fallback mechanisms when primary services fail**
- ✅ **Service metadata management and validation**
- ✅ **Monitoring endpoints (/services, /services/health)**
- ✅ **Plugin architecture with mock service injection**
- ✅ **Service lifecycle management (register/unregister)**
- ✅ **Edge case handling (no services, failed health checks)**