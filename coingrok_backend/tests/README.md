# Test Suite

This directory contains tests for the CoinGrok Backend API.

## Test Files

- `test_middleware.py` - Tests middleware configuration, order, CORS, and security headers
- `test_production_mode.py` - Tests production configuration requirements  
- `test_jwt_security.py` - **Comprehensive JWT authentication security tests**

## Running Tests

### Standalone
```bash
# Run middleware tests
python tests/test_middleware.py

# Run production config tests  
python tests/test_production_mode.py
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