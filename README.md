# PluginMind – Production-Ready AI SaaS Full Stack Template
### 🚀 Build & Launch AI SaaS Applications Faster

PluginMind is a **production-ready Full Stack template** for AI-powered SaaS products.  
It provides a secure, extensible foundation with **generic AI processing, plugin-style service registry, production infrastructure, and 107+ automated tests** – everything developers need to launch AI applications fast.

## 🧠 Background 

PluginMind evolved from **CoinGrok**, a crypto analysis tool, into a **generic AI processing platform**.  
Through strategic transformation, we generalized the crypto-specific system into a **flexible AI SaaS template** that supports multiple use cases.

The real value is in the **production-ready backend architecture** we built:


[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-00a5ff.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-15.2+-black.svg)](https://nextjs.org)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![SQLModel](https://img.shields.io/badge/SQLModel-latest-green.svg)](https://sqlmodel.tiangolo.com)  
- 🔌 **Generic AI Processing** → configurable workflows for document, chat, SEO, crypto, custom use cases.  
- 🛡️ **Secure Auth & Rate Limiting** → Google login, JWT, CORS, request limits.  
- 🗄️ **Production Infrastructure** → Docker, CI/CD, Alembic migrations, environment management.  
- 🧪 **107+ Automated Tests** → comprehensive coverage with CI/CD integration.  
- ⚡ **Plugin Architecture** → AI service registry with OpenAI, Grok, and extensible providers.

This transformation created **PluginMind: a universal AI SaaS template**.

## 🧩 Use Cases & Applications

PluginMind supports **multiple AI-powered SaaS applications**:
- 📝 **Document Summarizer** → AI-powered document analysis and summarization  
- 🤖 **AI Chatbot Backend** → conversational AI with context management  
- 🔍 **SEO Content Generator** → AI-driven content optimization and generation
- 📊 **Data Analyzer** → configurable AI analysis workflows
- 🎯 **Custom AI Processing** → flexible templates for any AI use case  

## Current Status (v2.0 - PluginMind Transformation Complete) ✨

- **Generic AI Processing:** Multi-use-case AI workflows (document, chat, SEO, crypto, custom) ✅
- **Production Infrastructure:** Docker multi-stage builds, Alembic migrations, CI/CD pipelines ✅
- **API Architecture:** Generic `/process` endpoint + backward-compatible legacy endpoints ✅
- **AI Service Registry:** Plugin-style architecture with OpenAI/Grok providers ✅
- **Prompt Template Engine:** Configurable 4-D methodology for all analysis types ✅
- **Authentication:** Google OAuth with JWT validation and user management ✅
- **Database System:** PostgreSQL/SQLite with flexible AnalysisResult model ✅
- **Error Handling:** Production-ready unified system with comprehensive coverage ✅
- **Testing Suite:** 107+ automated tests with CI/CD integration ✅
- **Rate Limiting:** Enhanced with Retry-After headers and dual limits ✅
- **Configuration:** Fail-fast validation with environment-driven settings ✅
- **Monitoring:** Service health endpoints and comprehensive logging ✅
- **Security:** Production-ready headers, CORS, request limits ✅
- **Template Ready:** Production template with comprehensive developer documentation ✅

### 🆕 Latest Release Highlights (v2.0 - PluginMind Transformation)

#### **🚀 Complete Transformation: CoinGrok → PluginMind** ✨ **NEW**
- **Generic AI Processing**: Transformed from crypto-specific to multi-use-case AI platform
- **Template Productization**: Production-ready developer template with full documentation
- **Branding Generalization**: Complete transformation across 38+ files and configurations
- **API Enhancement**: New `/process` endpoint supporting document, chat, SEO, crypto, custom workflows
- **Infrastructure Modernization**: Docker, Alembic migrations, enhanced CI/CD pipelines
- **Architecture Excellence**: Maintained FastAPI patterns while adding generic capabilities

#### **🧪 Enhanced Test Coverage & Reliability**
- **115 Total Tests**: 100% pass rate (114 passing, 1 skipped)
- **No API Keys Required**: Tests run in TESTING mode - works out-of-the-box
- **Service Registry Tests**: Complete coverage of plugin architecture (20 tests)
- **Integration Testing**: Service discovery, health checks, and endpoint validation
- **Mock Service Framework**: Comprehensive testing infrastructure
- **CI/CD Integration**: All tests pass in GitHub Actions without configuration

#### **⚙️ Production Configuration Validation**
- **Fail-Fast Startup**: Comprehensive validation of all environment variables at startup
- **Smart Validation Logic**: Debug vs production mode validation with appropriate defaults
- **Cross-Dependency Checks**: Validates related configuration variables together
- **Clear Error Messages**: Detailed validation errors with specific fix instructions
- **Testing Mode Support**: Relaxed validation for automated testing environments

#### **🔧 HTTP Client Configuration System**
- **Configurable Connection Pools**: Environment-driven max connections and keepalive settings
- **Granular Grok Timeouts**: Separate connect, read, write, and pool timeout configuration
- **Global OpenAI Timeouts**: Unified timeout settings for OpenAI API calls
- **Security Enhancements**: Bearer token redaction in logs with comprehensive header protection

#### ** Production Environment Consolidation**
- **Unified Configuration**: All settings moved from .env.example to production-ready .env
- **Environment Variable Organization**: Clearly structured sections for API keys, HTTP settings, and limits
- **Model Configuration**: Updated to use correct model names (gpt-5, grok-4-0709)
- **Production Security**: Sensitive information properly secured and documented

#### ** Complete CI/CD Test Integration**
- **100% Test Success**: All 107 tests passing in CI/CD pipeline (9 test suites)
- **AI Service Registry Tests**: 20 comprehensive tests for plugin architecture
- **HTTP Client Tests**: 10 comprehensive tests for configuration and security validation
- **Error Integration Tests**: 10 additional tests for complete error handling validation
- **CI Environment Fix**: Relative paths ensure tests work in both local and CI environments

#### **⚡ Enhanced Development Experience**
- **Database Integration**: Automatic test database initialization for integration tests
- **Cross-Platform Compatibility**: Tests run successfully on macOS, Linux, and Windows
- **Comprehensive Logging**: Security-focused logging with sensitive data redaction

---

## ⚙️ Tech Stack

### Backend
- **Python 3.11+** – Core application logic
- **FastAPI** – High-performance async API framework
- **SQLModel** – Type-safe database ORM with PostgreSQL/SQLite
- **AI Service Registry** – Plugin architecture for AI providers
- **OpenAI API** – GPT-4/5 for prompt optimization and generic AI processing
- **Grok xAI API** – Advanced AI analysis capabilities
- **Pydantic v2** – Data validation and serialization
- **google-auth** – Google ID token verification (RS256)
- **Alembic** – Database migrations and schema management
- **Docker** – Multi-stage containerization with production optimization

### Frontend  
- **Next.js 15** – React framework with App Router
- **React 19** – Latest React with concurrent features
- **TypeScript** – Type-safe JavaScript development
- **@react-oauth/google** – Official Google OAuth for React
- **Tailwind CSS** – Utility-first CSS framework
- **shadcn/ui** – Modern component library
- **Recharts** – Interactive data visualizations

### Database & Infrastructure
- **PostgreSQL** – Production database with flexible schema
- **SQLite** – Development database with same schema compatibility
- **Alembic Migrations** – Automatic schema management and versioning
- **Docker Compose** – Complete development environment orchestration
- **CI/CD Pipelines** – GitHub Actions with 100% test pass gates
- **Query Analytics** – Comprehensive usage tracking and analysis

---

## 🏗️ Project Architecture

### Repository Structure (Production-Ready PluginMind Template)
```
PluginMind/                          # Repository root - Production AI SaaS Template
├── .github/
│   └── workflows/                     # CI/CD automation with 100% test gates
│       ├── test.yml                   # Comprehensive test suite runner
│       ├── docker.yml                 # Docker build and validation
│       ├── feature-document.yml       # Document processing feature validation
│       ├── feature-chatbot.yml        # Chatbot backend feature validation
│       └── feature-seo.yml           # SEO generator feature validation
│
├── pluginmind_backend/                # Generic AI Processing Backend ✨ TRANSFORMED
│   ├── Dockerfile                     # Multi-stage production Docker build ✨ NEW
│   ├── docker-compose.yml            # Complete development orchestration ✨ NEW
│   ├── alembic.ini                   # Database migration configuration ✨ NEW
│   ├── alembic/                      # Database migration system ✨ NEW
│   │   ├── env.py                    # Migration environment setup
│   │   └── versions/                 # Migration version history
│   │       └── 001_initial_pluginmind_schema.py # Initial schema with AnalysisResult
│   │
│   ├── app/
│   │   ├── main.py                    # FastAPI app with generic AI service registry ✨
│   │   ├── database.py               # Database engine & session management  
│   │   ├── ash_prompt.py             # Generic 4-D Prompt Template Engine ✨ ENHANCED
│   │   │                             # → Configurable templates for document, chat, SEO, crypto, custom
│   │   │
│   │   ├── core/                     # Core infrastructure
│   │   │   ├── config.py            # Environment settings & comprehensive validation
│   │   │   ├── logging.py           # Centralized logging setup
│   │   │   └── exceptions.py        # PluginMind exception classes ✨ UPDATED
│   │   │
│   │   ├── api/                      # Generic API layer ✨ ENHANCED
│   │   │   ├── dependencies.py      # FastAPI dependencies (DB sessions)
│   │   │   ├── dependencies_rate_limit.py # Rate limiting with Retry-After headers
│   │   │   └── routes/              # Generic endpoint handlers ✨ ENHANCED
│   │   │       ├── analysis.py      # /process (generic), /analyze (legacy) ✨ NEW ENDPOINT
│   │   │       ├── users.py         # /me, /me/usage (user profiles)
│   │   │       ├── jobs.py          # /jobs management with UUID validation
│   │   │       ├── health.py        # /health, /services, /services/health ✨ ENHANCED
│   │   │       ├── query_logs.py    # /query-logs analytics
│   │   │       └── testing.py       # Testing utilities and endpoints
│   │   │
│   │   ├── services/                 # Generic AI Service Layer ✨ ENHANCED
│   │   │   ├── ai_service_interface.py  # Multi-use-case service registry ✨ ENHANCED
│   │   │   │                        # → Document, chat, SEO, crypto, custom service types
│   │   │   ├── service_initialization.py # Enhanced service registration ✨ ENHANCED
│   │   │   ├── openai_service.py    # OpenAI multi-capability implementation ✨ ENHANCED
│   │   │   ├── grok_service.py      # Grok multi-capability implementation ✨ ENHANCED
│   │   │   ├── analysis_service.py  # Generic orchestration with service discovery ✨ ENHANCED
│   │   │   └── user_service.py      # User management & usage tracking
│   │   │
│   │   ├── models/                   # Flexible data layer ✨ ENHANCED
│   │   │   ├── database.py          # AnalysisResult model for generic AI processing ✨ NEW
│   │   │   ├── schemas.py           # Generic request/response models ✨ ENHANCED
│   │   │   └── enums.py             # Status enums & constants
│   │   │
│   │   ├── middleware/               # Production middleware stack
│   │   │   ├── auth.py              # JWT validation & auth dependencies
│   │   │   ├── cors.py              # CORS configuration
│   │   │   ├── error_handler.py     # Unified PluginMind exception handling ✨
│   │   │   ├── security_headers.py  # Production HTTP security headers
│   │   │   ├── request_limits.py    # Request body size limits
│   │   │   └── correlation_id.py    # Request tracing with correlation IDs
│   │   │
│   │   └── utils/                    # Utilities
│   │       ├── background_tasks.py  # Async job processing
│   │       ├── http.py              # Resilient HTTP client with configurable pools
│   │       ├── rate_limit.py        # Token-bucket rate limiting + retry calculation
│   │       └── ip.py                # IP extraction utilities
│   │
│   ├── tests/                         # Comprehensive test suite (107+ tests) ✨
│   │   ├── test_ai_service_registry.py # AI service registry tests (20 tests) ✨ ENHANCED
│   │   │                            # → Multi-use-case service registration and discovery
│   │   │                            # → Document, chat, SEO, crypto service type validation
│   │   │                            # → Health checking and monitoring endpoints
│   │   │                            # → Generic analysis workflow testing
│   │   ├── test_error_handling.py    # Exception mapping & response format tests
│   │   ├── test_error_integration.py # API endpoint integration tests (10 tests)
│   │   ├── test_http_client.py      # HTTP client configuration tests (10 tests)
│   │   ├── test_config_validation.py # Environment validation tests ✨ NEW
│   │   ├── test_rate_limit.py       # Rate limiting behavior tests
│   │   ├── test_middleware.py       # Middleware functionality tests
│   │   ├── test_jwt_security.py     # JWT validation tests
│   │   ├── test_production_mode.py  # Production environment tests
│   │   └── conftest.py              # Shared test configuration and fixtures
│   │
│   ├── scripts/                      # Operations & deployment scripts ✨
│   │   ├── smoke_backend.sh          # Comprehensive production smoke tests
│   │   ├── smoke_errors.sh          # Error handling validation (7 scenarios)
│   │   ├── validate_env.py          # Environment configuration validator ✨ NEW
│   │   ├── manage_db.py             # Database management utilities ✨ NEW
│   │   └── init-db.sh               # Database initialization script ✨ NEW
│   │
│   ├── run_error_tests.py           # Test suite runner
│   ├── gunicorn_conf.py             # Production WSGI server configuration
│   ├── requirements.txt             # Python dependencies with production packages
│   └── SYSTEM_MAP.md                # Complete system architecture documentation ✨ NEW
│
├── frontend/                         # Next.js React application
│   ├── app/                         # Next.js 15 App Router
│   ├── components/                  # React components
│   ├── lib/                         # Utility functions
│   └── package.json                # Frontend dependencies
│
├── docs/                            # Project documentation
└── README.md                       # Project overview & setup guide
```

### Frontend Structure
```
frontend/
├── app/                      # Next.js 15 App Router
│   ├── page.tsx             # Landing page
│   ├── layout.tsx           # Root layout
│   ├── globals.css          # Global styles
│   └── analyze/
│       └── page.tsx         # Analysis interface
│
├── components/               # React components
│   ├── ui/                  # shadcn/ui components
│   ├── analysis-result.tsx  # Results display
│   ├── crypto-chart.tsx     # Price charts
│   └── market-insights.tsx  # Market data
│
├── lib/
│   └── utils.ts             # Utility functions
│
├── package.json             # Dependencies
└── tailwind.config.ts       # Styling config
```

## 🔄 How It Works

### Request Flow with Generic AI Processing
```mermaid
graph LR
    A[User Input + Analysis Type] --> B[Validation]
    B --> C[Prompt Template Engine]
    C --> D[AI Service Registry]
    D --> E[Service Discovery]
    E --> F[AI Service Processing]
    F --> G[Result Storage]
    G --> H[Response]
```

### Architecture Benefits
- **Generic AI Processing**: Supports document, chat, SEO, crypto, and custom workflows
- **Plugin Architecture**: AI services implement common interface for extensibility
- **Service Discovery**: Dynamic service selection by type and capability
- **Template Engine**: Configurable 4-D prompt methodology for all use cases
- **Health Monitoring**: Automatic health checks with comprehensive reporting
- **Modular Design**: Clean separation of concerns with single responsibility
- **Type Safety**: Full TypeScript/Python type coverage throughout
- **Error Handling**: Production-ready unified exception management
- **Scalability**: Service layer architecture ready for microservices
- **Testing**: Clean architecture with 107+ comprehensive tests
- **Database Flexibility**: Generic AnalysisResult model supporting varied content types
- **Production Ready**: Docker, CI/CD, migrations, monitoring, and deployment automation

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- OpenAI API Key
- Grok API Key


### 🔍 Generic AI Processing Endpoints

**Generic AI Processing (Primary Endpoint):**
```bash
curl -X POST "http://localhost:8000/process" \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Summarize this document: ...", "analysis_type": "document"}'
```

**Service Information:**
```bash
curl http://localhost:8000/services
# Response: Available AI services, analysis types, and endpoint information
```

**Service Health Monitoring:**
```bash
curl http://localhost:8000/services/health
# Response: Individual service health with overall system status
```

### 🧪 Testing the API

**No API Keys Required for Testing!** 🎉
```bash
# Tests run in TESTING mode - no real API keys needed
cd pluginmind_backend
TESTING=1 python -m pytest
# Expected: 115 tests (114 passed, 1 skipped) ✅
```

**Health Check:**
```bash
curl http://localhost:8000/health
# Response: {"status": "ok", "active_jobs": 0}
```

**Complete Test Suite:** ✨ **100% Pass Rate**
```bash
# Run full test suite - no configuration needed!
cd pluginmind_backend
TESTING=1 python -m pytest -v
# Expected: 115 tests total
# ✅ 114 passing tests
# ⏭️ 1 skipped (complex JWT mocking)

# Test Coverage by Module:
# ✅ AI Service Registry: 20 tests
# ✅ Configuration Validation: 7 tests  
# ✅ Error Handling: 22 tests
# ✅ Generic Processing: 10 tests
# ✅ Rate Limiting: 27 tests
# ✅ JWT Security: 5 tests
# ✅ HTTP Client: 10 tests
# ✅ Middleware & Integration: 14 tests

# Run specific test modules
python -m pytest tests/test_ai_service_registry.py -v
python -m pytest tests/test_generic_processing.py -v
python -m pytest tests/test_error_handling.py -v

# Run with coverage report
python -m pytest --cov=app --cov-report=term

# Test configuration validation at startup
OPENAI_API_KEY=invalid python -c "from app.main import app"
# Expected: Configuration validation error with clear fix instructions

# Run production smoke tests (7 scenarios)
chmod +x scripts/smoke_errors.sh
./scripts/smoke_errors.sh http://localhost:8000
# Expected output: 7/7 tests passed ✅
# ✅ Job not found error (404 + JOB_NOT_FOUND)
# ✅ Authentication required (401 + AUTHENTICATION_FAILED)  
# ✅ Invalid authentication token (401)
# ✅ Non-existent endpoint (404 + HTTP_EXCEPTION)
# ✅ Validation error - empty body (422 + INVALID_INPUT)
# ✅ Field length validation (422 + INVALID_INPUT)
# ✅ Health check endpoint (200)
```

**Generic AI Processing Examples:**
```bash
# Document Summarization
curl -X POST "http://localhost:8000/process" \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Summarize this research paper: ...", "analysis_type": "document"}'

# Chat/Conversation Processing
curl -X POST "http://localhost:8000/process" \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Help me plan a vacation to Japan", "analysis_type": "chat"}'

# SEO Content Generation
curl -X POST "http://localhost:8000/process" \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Create SEO content for digital marketing", "analysis_type": "seo"}'

# Legacy Crypto Analysis (Backward Compatible)
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Analyze Bitcoin over 7 days with $500"}'
```

**Async Processing:**
```bash
# Start background job
curl -X POST "http://localhost:8000/analyze-async" \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Deep analysis of market trends"}'

# Check results (use job_id from above)
curl http://localhost:8000/analyze-async/{job_id}
```

**API Documentation:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 📚 API Documentation

### Core Endpoints

#### `POST /process` ✨ **NEW - Primary Endpoint**
Generic AI processing with configurable analysis types
```json
{
  "user_input": "Your content or query here",
  "analysis_type": "document" // Options: document, chat, seo, crypto, custom
}
```

**Response:**
```json
{
  "analysis_type": "document",
  "optimized_prompt": "AI-optimized prompt for document processing...",
  "analysis_result": "Comprehensive analysis results based on type...",
  "system_prompt": "System prompt template used",
  "services_used": {
    "prompt_optimizer": {"name": "OpenAI", "provider": "OpenAI", "model": "gpt-4"},
    "analyzer": {"name": "OpenAI", "provider": "OpenAI", "model": "gpt-4"}
  },
  "metadata": {}
}
```

#### `POST /analyze` (Legacy - Backward Compatible)
Legacy crypto analysis endpoint (deprecated, use `/process` instead)
```json
{
  "user_input": "Analyze Bitcoin over 7 days with $500"
}
```

**Response:**
```json
{
  "optimized_prompt": "Professional crypto analysis prompt...",
  "analysis": "Comprehensive crypto market analysis..."
}
```

#### `POST /analyze-async`
Start background analysis job
```json
{
  "user_input": "Deep analysis of Ethereum market trends"
}
```

**Response:**
```json
{
  "job_id": "uuid-string",
  "status": "queued",
  "created_at": "2024-01-01T00:00:00Z",
  "message": "Analysis started. Use the job_id to check status."
}
```

#### `GET /analyze-async/{job_id}`
Check job status and retrieve results

#### `GET /services` ✨ **NEW**
Get AI service registry information and available analysis types

#### `GET /services/health` ✨ **NEW**
Individual AI service health monitoring with detailed status

#### `GET /health`
Health check with active job count

#### `GET /query-logs`
View recent query history (debugging)

### Error Handling

PluginMind implements a **production-ready unified error handling system** with consistent response format, comprehensive logging, and full CI/CD integration.

#### Error Response Format

All API errors return a standardized JSON envelope with consistent structure:

```json
{
  "error": {
    "message": "User-friendly error message",
    "code": "ERROR_CODE_CONSTANT", 
    "correlation_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479"
  }
}
```

#### Comprehensive Error Coverage

| HTTP Status | Error Code | Description | Handler |
|------------|------------|-------------|---------|
| 400 | `INVALID_INPUT` | Request validation failed | Custom exceptions |
| 401 | `AUTHENTICATION_FAILED` | Invalid or missing authentication | Custom exceptions |
| 404 | `JOB_NOT_FOUND` | Analysis job not found | Custom exceptions |
| 404 | `USER_NOT_FOUND` | User account not found | Custom exceptions |
| 404 | `HTTP_EXCEPTION` | Non-existent endpoints | **Routing-level handler** ✨ |
| 413 | `REQUEST_TOO_LARGE` | Request body exceeds 1MB limit | Middleware |
| 422 | `INVALID_INPUT` | **Validation errors (JSON/fields)** | **RequestValidationError handler** ✨ |
| 429 | `RATE_LIMIT_EXCEEDED` | Too many requests | **Rate limiter + Retry-After headers** ✨ |
| 429 | `QUERY_LIMIT_EXCEEDED` | User query limit reached | Custom exceptions |
| 500 | `INTERNAL_SERVER_ERROR` | **Unexpected exceptions** | **Generic exception handler** ✨ |
| 500 | `USER_ACCESS_FAILED` | User account operation failed | Custom exceptions |
| 500 | `DATABASE_ERROR` | Database operation failed | Custom exceptions |
| 502 | `AI_SERVICE_ERROR` | External AI service unavailable | Custom exceptions |
| 503 | `SERVICE_UNAVAILABLE` | Service temporarily unavailable | Custom exceptions |

#### 🚀 Latest Enhancements (v1.4 - Error Handling Final Touches)

**✨ New Exception Handlers:**
- **RequestValidationError Handler**: Converts FastAPI validation errors (422) to unified format
- **StarletteHTTPException Handler**: Ensures routing-level 404s use unified format  
- **Enhanced Generic Handler**: Safe, consistent 500 error responses for unexpected exceptions

**✨ Rate Limiting Improvements:**
- **Retry-After Headers**: Automatic calculation and inclusion in 429 responses
- **Enhanced RateLimitError**: Support for retry-after timing information
- **Dual Rate Limiting**: User-based and IP-based limits with proper header management

**✨ Validation Error Unification:**
- **Malformed JSON**: Invalid JSON syntax → unified 422 + INVALID_INPUT
- **Missing Fields**: Required field validation → unified 422 + INVALID_INPUT  
- **Field Constraints**: Length/type validation → unified 422 + INVALID_INPUT

#### Error Correlation & Debugging

Every error response includes a `correlation_id` for efficient debugging:

```bash
# Server logs with correlation tracking
2024-01-01 12:00:00 - ERROR - Job not found: invalid-job-id [correlation_id=f47ac10b]
2024-01-01 12:00:00 - WARNING - Validation error: missing field 'user_input' [correlation_id=a1b2c3d4]
```

#### Response Headers & Rate Limiting

**Standard Headers:**
```http
Content-Type: application/json
X-Request-ID: f47ac10b-58cc-4372-a567-0e02b2c3d479
```

**Rate Limiting Headers:**
```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
Retry-After: 120  # ✨ New: Seconds to wait before retry
```

#### Testing & Quality Assurance

**✅ Comprehensive Test Coverage:**
- **Unit Tests**: All exception types and handlers tested
- **Integration Tests**: Real API endpoint error scenarios  
- **Smoke Tests**: Live production validation (7/7 scenarios)

**✅ CI/CD Integration:**
- **Pre-merge**: All error tests run on every PR
- **Post-deploy**: Automated smoke tests validate production health
- **Coverage**: 422, 500, 429, 404, 401 scenarios fully tested

### Database Schema

#### AnalysisResult Table ✨ **NEW - Primary Model**
Flexible schema for generic AI processing results:
- `analysis_id`: UUID for external tracking
- `analysis_type`: Type of analysis (document, chat, seo, crypto, custom)
- `user_id`: User identifier for ownership tracking
- `user_input`: Original user input/query
- `result_data`: JSON storage for AI processing results and metadata
- `status`: PENDING → PROCESSING → COMPLETED/FAILED
- `created_at`, `updated_at`: Timestamp tracking

#### QueryLog Table (Legacy Analytics)
Tracks all user queries for analytics and billing:
- `user_id`: User identifier (nullable for anonymous usage)
- `user_input`: Original query
- `ai_result`: Final analysis result
- `response_time_ms`: Performance metrics
- `success`: Query completion status
- `openai_cost`, `grok_cost`, `total_cost`: Billing tracking

#### AnalysisJob Table (Async Processing)
Manages asynchronous job processing:
- `job_id`: UUID for external tracking
- `status`: queued → processing_openai → processing_grok → completed
- `optimized_prompt`: AI-generated prompt
- `analysis`: Final analysis result
- `user_id`: Links jobs to users
- `cost`: Total API cost for billing

#### User Table (Authentication & Usage)
User management and subscription tracking:
- `email`: User email address
- `google_id`: Google OAuth identifier
- `subscription_tier`: free, pro, premium
- `queries_used`, `queries_limit`: Usage tracking
- `is_active`: Account status

---

# 🔐 Phase 2: Authentication & User Management

> **Complete Google OAuth integration with Supabase, JWT-protected routes, and usage tracking**

## 🚀 Features Implemented

### **Authentication System**
- **Native Google ID Token Verification** - Direct Google OAuth with RS256 algorithm
- **google-auth Library** - Secure token validation using Google's public keys
- **Middleware Protection** - Route-level authentication with dependency injection
- **Auto User Creation** - First-time users automatically created with default settings

### **User Management**
- **Smart User Lookup** - Finds users by `google_id` or email with fallback logic
- **Usage Tracking** - Real-time query counting for billing and limits
- **Subscription Tiers** - Built-in support for `free`, `pro`, `premium` plans
- **Query Limits** - Automatic enforcement prevents API overuse

### **Protected API Endpoints**
```http
POST   /analyze        # 🔒 Protected - Analysis with usage tracking
GET    /me             # 🔒 Protected - User profile information
GET    /me/usage       # 🔒 Protected - Query usage statistics
```

## 🏗️ Authentication Architecture

### **Auth Flow**
```
Google OAuth → Google ID Token → FastAPI Verification → Protected Route
```

1. **Client** triggers Google OAuth via `@react-oauth/google`
2. **Google** returns ID token with user claims
3. **FastAPI** validates token using `google-auth` with RS256 verification
4. **Middleware** extracts user ID and provides `UserDep`/`OptionalUserDep`
5. **Routes** get authenticated user automatically

### **Tech Stack**
- **FastAPI Dependencies** - Clean dependency injection for auth
- **google-auth** - Google ID token verification with RS256
- **@react-oauth/google** - Official React Google OAuth integration
- **SQLModel** - Type-safe database operations
- **HTTPBearer** - Secure header-based authentication

## 📊 Auth API Usage Examples

### **Protected Analysis with Auto User Creation**
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Analyze BTC price trends"}'
```

### **Get User Profile**
```bash
curl -X GET "http://localhost:8000/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### **Check Usage Limits**
```bash
curl -X GET "http://localhost:8000/me/usage" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🎯 Key Components

| Component | Purpose | Location |
|-----------|---------|----------|
| **`auth.py`** | JWT validation & dependencies | `app/middleware/auth.py` |
| **`user_service.py`** | User CRUD operations | `app/services/user_service.py` |
| **`users.py`** | Profile & usage endpoints | `app/api/routes/users.py` |
| **`UserProfile`** | Response schema for `/me` | `app/models/schemas.py` |
| **`UserUsage`** | Response schema for `/me/usage` | `app/models/schemas.py` |

## 🔄 User Lifecycle

```mermaid
graph LR
    A[First API Call] --> B[JWT Validation]
    B --> C{User Exists?}
    C -->|No| D[Create User]
    C -->|Yes| E[Load User]
    D --> F[Check Limits]
    E --> F
    F --> G{Under Limit?}
    G -->|Yes| H[Process Request]
    G -->|No| I[Return 429 Error]
    H --> J[Increment Usage]
```

---

## 🚀 Production Deployment

### Docker Deployment ✨ **NEW**

**Quick Start with Docker:**
```bash
# Development with hot reload
cd pluginmind_backend
docker-compose up --build

# Production deployment
docker build --target production -t pluginmind-backend .
docker run -p 8000:8000 --env-file .env pluginmind-backend
```

**Multi-stage Docker Build:**
- **Development**: Python with hot reload and debugging tools
- **Production**: Optimized image with security enhancements
- **Testing**: Isolated environment for CI/CD pipelines

### Database Migrations ✨ **NEW**

**Initialize Database:**
```bash
# Create initial migration
alembic upgrade head

# Generate new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

### Environment Variables

**Backend (.env)**
```bash
# Required API Keys
OPENAI_API_KEY=your-openai-api-key
GROK_API_KEY=your-grok-api-key

# Database Configuration
DATABASE_URL=postgresql://user:pass@localhost:5432/pluginmind  # Production
# DATABASE_URL=sqlite:///./pluginmind.db  # Development

# Security & Performance
CORS_ORIGINS=https://pluginmind.vercel.app,https://your-domain.com
LOG_LEVEL=INFO
DEBUG=false

# Phase 2 Authentication (Required)
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com

# Optional: Supabase for user management
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE=your-supabase-service-role-key

# Optional Configuration
JOB_CLEANUP_HOURS=24
MAX_USER_INPUT_LENGTH=5000
```

**Frontend (.env)**
```bash
# Google OAuth Configuration
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Backend Configuration
NEXT_PUBLIC_BACKEND_URL=https://your-backend-domain.com

# Frontend Configuration
NEXT_PUBLIC_FRONTEND_URL=https://your-frontend-domain.com
```

### Deployment Options

#### Backend Deployment
**Render/Railway/Fly.io:**
```yaml
# render.yaml
services:
- type: web
  name: pluginmind-api
  env: python
  plan: starter
  buildCommand: pip install -r requirements.txt
  startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
  envVars:
  - key: OPENAI_API_KEY
    sync: false
  - key: GROK_API_KEY
    sync: false
```

**Docker:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app/ ./app/
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Frontend Deployment
**Vercel:**
```json
{
  "env": {
    "NEXT_PUBLIC_API_URL": "https://your-api-domain.com"
  },
  "build": {
    "env": {
      "NEXT_PUBLIC_API_URL": "https://your-api-domain.com"
    }
  }
}
```

### Database Setup
**Production PostgreSQL:**
```bash
# Using Supabase, Neon, or similar
DATABASE_URL=postgresql://username:password@host:5432/database
```

**Development SQLite:**
```bash
DATABASE_URL=sqlite:///./pluginmind.db
```

## Production Deployment

### Process Management with Gunicorn

The backend includes production-ready Gunicorn configuration with environment-driven settings:

```bash
# Start with Gunicorn (production)
cd pluginmind_backend
gunicorn app.main:app --config gunicorn_conf.py

# Key production features:
# - Environment-driven worker count and timeouts
# - Correlation ID access logging for request tracing
# - Graceful worker restarts and memory management
# - Production-optimized connection pools
```

**Environment Variables for Production:**
```bash
# Process Management
GUNICORN_WORKERS=4                    # CPU cores * 2 + 1
GUNICORN_TIMEOUT=300                  # 5min timeout (matches AI call budget)
GUNICORN_MAX_REQUESTS=1000           # Restart workers after N requests
GUNICORN_MAX_REQUESTS_JITTER=100     # Add randomness to prevent thundering herd

# HTTP Client Configuration ✨ NEW
HTTP_MAX_CONNECTIONS=100             # Maximum concurrent connections
HTTP_MAX_KEEPALIVE=10               # Maximum keepalive connections
HTTP_TIMEOUT_SECONDS=120             # Global timeout for OpenAI calls
HTTP_MAX_RETRIES=1                   # Retry failed requests once
HTTP_RETRY_BACKOFF_BASE=0.5         # Exponential backoff base

# Grok-Specific Granular Timeouts ✨ NEW
GROK_TIMEOUT_SECONDS=200            # Read timeout for Grok API
GROK_CONNECT_TIMEOUT=10.0           # Connection establishment timeout
GROK_WRITE_TIMEOUT=30.0             # Write timeout for request body
GROK_POOL_TIMEOUT=5.0               # Connection pool timeout

# Request Protection
BODY_MAX_BYTES=1000000              # Max request body size (1MB)
RATE_LIMIT_PER_MIN=60               # User rate limiting per minute
RATE_LIMIT_BURST=120                # User rate limiting burst capacity
RATE_LIMIT_IP_PER_MIN=300           # IP rate limiting per minute (authenticated users)
RATE_LIMIT_IP_BURST=600             # IP rate limiting burst capacity (authenticated users)
```

### Production Security Features

**HTTP Security Headers (Automatic):**
- Content Security Policy (CSP) with safe defaults
- X-Frame-Options: DENY (prevents clickjacking)
- X-Content-Type-Options: nosniff (MIME type protection)
- Strict-Transport-Security (HSTS) in production only
- X-Request-ID correlation headers for tracing

**Request Protection:**
- Body size limits (1MB default, configurable)
- Token-bucket rate limiting with IP/user-based tracking
- UUID validation for all job endpoints
- CORS configured for specific frontend domains only

**Application Security:**
- FastAPI docs/OpenAPI disabled in production (`DEBUG=false`)
- Graceful HTTP client connection management
- Structured logging with correlation IDs for request tracing
- Resilient HTTP calls with exponential backoff retry logic

### Health Monitoring

Production-ready health endpoints for container orchestration:

```bash
# Kubernetes/Docker health checks
GET /live     # Liveness probe (always returns 200)
GET /ready    # Readiness probe (checks dependencies)
GET /health   # Detailed health with active job count
GET /version  # Build info (name, version, git SHA)
```

### Quality Assurance Script

Run comprehensive smoke tests before deployment:

```bash
# Test all production features
chmod +x scripts/smoke_backend.sh

# Test against local development
BASE=http://localhost:8000 ./scripts/smoke_backend.sh

# Test against staging/production (with auth token)
BASE=https://api.pluginmind.com TOKEN=jwt_token ./scripts/smoke_backend.sh

# Tests include:
# ✅ Health endpoints and JSON responses
# ✅ Security headers (CSP, HSTS, X-Frame-Options)  
# ✅ CORS configuration and preflight requests
# ✅ Authentication flows (with/without tokens)
# ✅ Request size limits (413 for >1MB requests)
# ✅ Rate limiting (429 after multiple requests)
```

### Production Readiness Checklist

- [x] **Process Management**: Gunicorn with environment-driven configuration
- [x] **Security Headers**: CSP, HSTS, X-Frame-Options, request correlation
- [x] **Request Protection**: Size limits, rate limiting, input validation
- [x] **Resilient HTTP**: Retry logic, exponential backoff, graceful timeouts
- [x] **Health Monitoring**: Liveness, readiness, and detailed health endpoints
- [x] **Observability**: Correlation ID tracing, structured logging, performance metrics
- [x] **Quality Assurance**: Comprehensive smoke test script for pre-deployment validation
- [x] **Graceful Shutdown**: Proper cleanup of HTTP clients and background tasks
- [x] **Error Handling**: **Unified exception system with comprehensive coverage**
- [x] **Validation Errors**: **422 errors use consistent envelope format**  
- [x] **Rate Limiting**: **Enhanced with Retry-After headers and dual limits**
- [x] **Testing Coverage**: **7/7 smoke tests + comprehensive CI/CD pipeline**
- [x] **Production Validation**: **Automated post-deploy error scenario testing**
- [x] **HTTP Configuration**: **Environment-driven connection pools and granular timeouts** ✨ **NEW**
- [x] **Security Enhancements**: **Bearer token redaction and comprehensive header protection** ✨ **NEW**
- [x] **CI/CD Expansion**: **100% test success rate - all 107 tests passing** ✨ **NEW**
- [x] **Configuration Validation**: **Fail-fast startup with comprehensive environment validation** ✨ **NEW**
- [x] **AI Service Registry**: **Plugin architecture with service discovery and health monitoring** ✨ **NEW**

---

## ⚙️ Startup Configuration Validation (Fail-Fast)

PluginMind backend implements comprehensive configuration validation at startup to ensure production reliability and prevent runtime failures due to invalid configuration.

### What is Validated

**API Keys & Secrets:**
- `OPENAI_API_KEY`, `GROK_API_KEY`: Must be present and minimum 10 characters
- `GOOGLE_CLIENT_ID`: Must end with `.apps.googleusercontent.com`
- Cross-dependencies: `SUPABASE_ANON_KEY` required if `SUPABASE_URL` is set

**URLs & Endpoints:**
- `OPENAI_API_URL`, `GROK_API_URL`: Must be valid HTTP/HTTPS URLs
- `DATABASE_URL`: Must use supported schemes (postgresql, sqlite, mysql)

**CORS Security:**
- Production mode: Requires explicit `CORS_ORIGINS`, no wildcards allowed
- Debug mode: Allows wildcards, defaults to `http://localhost:3000` if omitted

**Numeric Ranges:**
- `HTTP_TIMEOUT_SECONDS`: 1-300 seconds
- `HTTP_MAX_CONNECTIONS`: 1-10,000 connections
- `RATE_LIMIT_PER_MIN`: 1-10,000 requests
- `RATE_LIMIT_BURST`: 1-20,000, must be ≥ `RATE_LIMIT_PER_MIN`
- `GROK_*_TIMEOUT`: Various ranges for connection, read, write timeouts

**Logical Consistency:**
- Model names (`OPENAI_MODEL`, `GROK_MODEL`) cannot be empty
- Rate limit burst must be greater than or equal to per-minute limit

### How to Interpret Errors

**✅ Successful startup:**
```bash
2024-01-15 10:00:00 - INFO - Starting PluginMind Backend API v2.0.0
2024-01-15 10:00:00 - INFO - Validating configuration...
2024-01-15 10:00:00 - INFO - Configuration validation passed
2024-01-15 10:00:00 - INFO - Application startup completed successfully
```

**❌ Configuration errors (server won't start):**
```bash
2024-01-15 10:00:00 - INFO - Starting PluginMind Backend API v2.0.0
2024-01-15 10:00:00 - INFO - Validating configuration...
2024-01-15 10:00:00 - ERROR - Configuration validation failed:
  - OPENAI_API_KEY is missing or too short (minimum 10 characters)
  - CORS_ORIGINS is required in production mode
  - HTTP_TIMEOUT_SECONDS must be 1-300, got: 500
  - RATE_LIMIT_BURST (50) must be >= RATE_LIMIT_PER_MIN (100)
```

### Common Fixes

| Error | Solution |
|-------|----------|
| **API key missing/too short** | Set valid API keys with minimum 10 characters |
| **Invalid URL format** | Ensure URLs start with `http://` or `https://` |
| **CORS required in production** | Set `CORS_ORIGINS=https://yourdomain.com` when `DEBUG=false` |
| **Numeric out of range** | Check .env.example for valid ranges |
| **Google Client ID format** | Must end with `.apps.googleusercontent.com` |
| **Database URL invalid** | Use `postgresql://`, `sqlite:///`, or `mysql://` schemes |

### Debug vs Production Mode

**Debug Mode (`DEBUG=true`):**
- CORS origins default to `http://localhost:3000` if omitted
- Wildcard (`*`) CORS origins allowed
- More lenient validation for development

**Production Mode (`DEBUG=false`):**
- Explicit CORS origins required
- No wildcard CORS origins allowed
- Strict validation for all configuration

### Testing Mode

Set `TESTING=1` to relax validation for automated tests. This provides safe defaults for missing secrets while still validating numeric ranges and formats.

---

## 🔧 Configuration Variables

The backend uses environment variables defined in `.env` for configuration. All variables are validated at startup.

### **Required Variables (Critical)**

| Variable | Description | Format | Example |
|----------|-------------|---------|---------|
| `OPENAI_API_KEY` | OpenAI API key (min 10 chars) | `sk-proj-...` | From OpenAI dashboard |
| `GROK_API_KEY` | Grok/xAI API key (min 10 chars) | `xai-...` | From x.ai dashboard |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | `*.apps.googleusercontent.com` | From Google Console |
| `GOOGLE_CLIENT_SECRET` | Google OAuth secret | `GOCSPX-...` | From Google Console |
| `SUPABASE_URL` | Supabase project URL | `https://*.supabase.co` | From Supabase dashboard |
| `SUPABASE_ANON_KEY` | Supabase anonymous key | `eyJ...` | From Supabase dashboard |
| `JWT_SECRET` | JWT signing secret | Base64 string | Generate with `openssl rand -base64 64` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://...` | From Supabase or your DB |

### **CORS & Security**

| Variable | Description | Production Value | Debug Value |
|----------|-------------|------------------|-------------|
| `CORS_ORIGINS` | Allowed frontend origins | `https://yourdomain.com` | `http://localhost:3000` |
| `DEBUG` | Debug mode | `false` | `true` |

### **Application Settings**

| Variable | Default | Description | Range |
|----------|---------|-------------|-------|
| `APP_NAME` | `PluginMind Backend API` | Application name | Any string |
| `APP_VERSION` | `2.0.0` | Version number | Semver format |
| `LOG_LEVEL` | `INFO` | Logging level | DEBUG/INFO/WARNING/ERROR |

### **AI Models & APIs**

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_MODEL` | `gpt-5` | OpenAI model name |
| `OPENAI_API_URL` | `https://api.openai.com/v1/chat/completions` | OpenAI endpoint |
| `GROK_MODEL` | `grok-4-0709` | Grok model name |
| `GROK_API_URL` | `https://api.x.ai/v1/chat/completions` | Grok endpoint |

### **Performance & Limits**

| Variable | Default | Description | Range |
|----------|---------|-------------|-------|
| `HTTP_TIMEOUT_SECONDS` | `120` | Global HTTP timeout | 1-300 |
| `HTTP_MAX_CONNECTIONS` | `100` | Max concurrent connections | 1-10,000 |
| `HTTP_MAX_KEEPALIVE` | `10` | Max keepalive connections | 1-10,000 |
| `RATE_LIMIT_PER_MIN` | `60` | Requests per minute per user | 1-10,000 |
| `RATE_LIMIT_BURST` | `120` | Burst capacity | ≥ `RATE_LIMIT_PER_MIN` |
| `MAX_USER_INPUT_LENGTH` | `500` | Max input characters | 1-50,000 |
| `BODY_MAX_BYTES` | `1000000` | Max request body size | 1MB default |

### **Grok-Specific Timeouts**

| Variable | Default | Description | Range |
|----------|---------|-------------|-------|
| `GROK_TIMEOUT_SECONDS` | `200` | Grok read timeout | 1-600 |
| `GROK_CONNECT_TIMEOUT` | `10.0` | Grok connection timeout | 0.1-60 |
| `GROK_WRITE_TIMEOUT` | `30.0` | Grok write timeout | 0.1-120 |
| `GROK_POOL_TIMEOUT` | `5.0` | Grok pool timeout | 0.1-30 |

### **Optional Variables**

| Variable | Default | Description |
|----------|---------|-------------|
| `TESTING` | `0` | Testing mode (use `1` for tests only) |
| `JOB_CLEANUP_HOURS` | `1` | Hours to keep completed jobs |
| `HTTP_MAX_RETRIES` | `1` | HTTP retry attempts |
| `JWT_ALGORITHM` | `HS256` | JWT algorithm |

---

## 📊 Monitoring & Analytics

### Built-in Logging
- Request/response timing with performance metrics
- Error tracking with categorization and stack traces
- API usage metrics and patterns
- Database query performance monitoring
- AI service health and performance tracking
- Service discovery and registry operations

### Query Analytics
Access `/query-logs` endpoint to monitor:
- User query patterns and trends
- Response times and performance bottlenecks
- Success/failure rates by endpoint
- Popular analysis types and usage insights

### Health Monitoring
- `/health` endpoint for uptime monitoring
- `/services` endpoint for AI service registry information
- `/services/health` endpoint for individual service health status
- Automatic cleanup of old jobs and data
- Database connection health checks
- Memory and resource usage tracking
- AI service availability and performance monitoring

## 🛣️ Roadmap

### ✅ Phase 1: Backend Infrastructure & DB (COMPLETE)
- [x] Replace wildcard CORS with secure configuration
- [x] Set up PostgreSQL using Supabase (infrastructure ready)
- [x] Create users and queries tables with usage tracking
- [x] Move job storage from RAM to database (SQLModel/SQLAlchemy)
- [x] Database schema optimized for Phase 2 (nullable user_id)
- [x] Authentication dependencies installed (JWT, Supabase, OAuth)
- [x] Security audit complete (secrets protected, .gitignore updated)

### ✅ Phase 2: Auth System (COMPLETE)
- [x] Native Google ID token verification with RS256 algorithm
- [x] Backend token validation using google-auth library
- [x] Frontend auth with @react-oauth/google integration
- [x] Secure /analyze route with UserDep authentication
- [x] Auto user registration and profile management (/me endpoint)
- [x] Usage tracking and query limit enforcement (/me/usage endpoint)
- [x] Token expiry detection and automatic cleanup
- [x] Protected routes with authentication middleware

### ✅ Phase 2.5: Error Handling & Testing (COMPLETE)
- [x] **Unified Error Handling System**: Single source of truth exception mapping
- [x] **RequestValidationError Handler**: 422 validation errors with unified format  
- [x] **StarletteHTTPException Handler**: 404 routing errors with unified format
- [x] **Enhanced Rate Limiting**: Retry-After headers and dual user/IP limits
- [x] **Generic Exception Handler**: Safe 500 error responses for unexpected exceptions
- [x] **Comprehensive Test Suite**: Unit, integration, and smoke tests (7/7 passing)
- [x] **CI/CD Integration**: Pre-merge testing and post-deploy validation
- [x] **Production Smoke Tests**: Live error scenario validation
- [x] **Correlation ID Tracking**: End-to-end request tracing for debugging
- [x] **Error Documentation**: Complete API error reference and troubleshooting guide

### ✅ Phase 2.7: HTTP Configuration & Production Readiness (COMPLETE)
- [x] **HTTP Client Configuration**: Environment-driven connection pools and timeout settings
- [x] **Granular Grok Timeouts**: Separate connect, read, write, and pool timeout configuration
- [x] **Security Enhancements**: Bearer token redaction and comprehensive header protection
- [x] **Production Environment**: Consolidated .env configuration with all required variables
- [x] **Model Configuration**: Updated to correct model names (gpt-5, grok-4-0709)
- [x] **CI/CD Test Expansion**: Added HTTP client tests (10 tests) and error integration tests (10 tests)
- [x] **Cross-Platform Compatibility**: Fixed CI environment issues with relative paths
- [x] **Database Integration**: Automatic test database initialization for integration tests
- [x] **Production Documentation**: Complete HTTP configuration and deployment guide

### ✅ Phase 2.8: Configuration Validation & Test Reliability (COMPLETE)
- [x] **Fail-Fast Configuration Validation**: Comprehensive startup validation with clear error messages
- [x] **Environment Variable Validation**: API keys, URLs, CORS, numeric ranges, and cross-dependencies
- [x] **Debug vs Production Mode**: Smart validation logic with appropriate defaults for each environment
- [x] **100% Test Success Rate**: All 107 tests now passing (fixed 7 originally failing tests, added 2 new tests)
- [x] **Enhanced IP Validation**: IPv6 zone ID rejection for improved rate limiting security
- [x] **Token Bucket Security**: Prevention of negative token consumption exploitation
- [x] **Error Handling Test Fixes**: Resolved authentication vs validation priority conflicts
- [x] **TestClient Improvements**: Proper exception handling for comprehensive test coverage
- [x] **Rate Limiting Enhancements**: Fixed async mock issues and invalid token handling
- [x] **Production Test Reliability**: Complete CI/CD pipeline with 100% test success rate

### ✅ Phase 2.9: AI Service Registry & Plugin Architecture (COMPLETE) ✨ **NEW**
- [x] **Plugin-Style AI Services**: Abstract AIService interface with concrete OpenAI/Grok implementations
- [x] **Service Discovery System**: Type and capability-based service selection and registration
- [x] **Health Monitoring Infrastructure**: Automatic health checks with comprehensive status reporting
- [x] **Service Metadata Management**: Complete service information tracking and validation
- [x] **Registry-Based Orchestration**: Analysis service uses registry for dynamic service discovery
- [x] **New Monitoring Endpoints**: `/services` and `/services/health` for operational insights
- [x] **Backward Compatibility**: Legacy service methods preserved for seamless migration
- [x] **Comprehensive Test Coverage**: 20 additional tests covering all registry functionality
- [x] **CI/CD Integration**: Registry tests included in automated pipeline
- [x] **GPT-5 API Compatibility**: Fixed parameter issues (max_completion_tokens, temperature handling)

### Phase 3: Business Features
- [ ] Subscription tiers (Free/Pro/Premium)
- [ ] Stripe payment integration
- [ ] Usage-based billing system
- [ ] Query limits enforcement
- [ ] User dashboard and analytics

### Phase 4: Scale & Performance
- [ ] Redis caching layer
- [ ] Rate limiting middleware
- [ ] API versioning strategy
- [ ] Microservices architecture
- [ ] Docker containerization

## 🙏 Acknowledgments

- **OpenAI** - GPT-5 for intelligent prompt optimization
- **Grok AI** - Advanced market analysis capabilities
- **FastAPI** - High-performance async API framework
- **Next.js** - React framework for production applications
- **SQLModel** - Type-safe database ORM with automatic API integration
- **Claude Anthropic** - Advanced assistant model

---

**Built with ❤️ by Alexandru G. Mihai** 

## 📬 Contact & Information

**PluginMind is a production-ready AI SaaS template featuring:**
- ✅ Generic AI processing for multiple use cases
- ✅ Production infrastructure (Docker, CI/CD, migrations)
- ✅ Complete authentication and user management
- ✅ 107+ automated tests with comprehensive coverage
- ✅ Comprehensive developer documentation and setup guides

For inquiries about the PluginMind template, contact:  
📧 **[mihai.gl.alexandru@gmail.com]**

Transform your AI idea into a production SaaS in days, not months.
