# 🪙 CoinGrok - AI-Powered Crypto Analysis Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-00a5ff.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-15.2+-black.svg)](https://nextjs.org)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![SQLModel](https://img.shields.io/badge/SQLModel-latest-green.svg)](https://sqlmodel.tiangolo.com)

> **Transform your crypto questions into intelligent investment insights using our 4-D AI Prompt Engine**

CoinGrok is a full-stack web application that leverages OpenAI and Grok APIs to provide comprehensive cryptocurrency analysis. Simply ask natural language questions like "Analyze ETH over 7 days with $500" and get professional-grade insights including sentiment analysis, market data, and investment recommendations.

## 🚀 Current Status (v1.0)

- **Backend:** FastAPI with SQLModel database integration ✅
- **Frontend:** Modern Next.js 15 with TypeScript ✅
- **Database:** PostgreSQL/SQLite support with query logging ✅
- **Authentication:** Mock user system (production auth ready) ⚠️
- **Deployment:** Development ready, production configuration included ✅

---

## ⚙️ Tech Stack

### Backend
- **Python 3.11+** – Core application logic
- **FastAPI** – High-performance async API framework
- **SQLModel** – Type-safe database ORM with PostgreSQL/SQLite
- **OpenAI API** – GPT-4 for prompt optimization
- **Grok xAI API** – Advanced crypto market analysis
- **Pydantic v2** – Data validation and serialization

### Frontend  
- **Next.js 15** – React framework with App Router
- **React 19** – Latest React with concurrent features
- **TypeScript** – Type-safe JavaScript development
- **Tailwind CSS** – Utility-first CSS framework
- **shadcn/ui** – Modern component library
- **Recharts** – Interactive data visualizations

### Database & Infrastructure
- **PostgreSQL** – Production database
- **SQLite** – Development database
- **Database Migrations** – Automatic schema management
- **Query Logging** – Complete usage analytics

---

## 🏗️ Project Architecture

### Backend Structure (Production-Ready)
```
coingrok_backend/
├── app/
│   ├── main.py                 # FastAPI app initialization (118 lines)
│   ├── database.py            # Database engine & session management  
│   ├── ash_prompt.py          # 4-D Prompt Engine system prompt
│   │
│   ├── core/                  # Core infrastructure
│   │   ├── config.py         # Environment settings & validation
│   │   ├── logging.py        # Centralized logging setup
│   │   └── exceptions.py     # Custom exception classes
│   │
│   ├── api/                   # API layer
│   │   ├── dependencies.py   # FastAPI dependencies (DB sessions)
│   │   └── routes/           # Endpoint handlers
│   │       ├── analysis.py   # /analyze, /analyze-async
│   │       ├── jobs.py       # /jobs management
│   │       ├── health.py     # /health monitoring
│   │       └── query_logs.py # /query-logs analytics
│   │
│   ├── services/              # Business logic layer
│   │   ├── openai_service.py # OpenAI integration (4-D Engine)
│   │   ├── grok_service.py   # Grok/xAI integration
│   │   └── analysis_service.py # Orchestration & logging
│   │
│   ├── models/                # Data layer
│   │   ├── database.py       # SQLModel tables (jobs, users, logs)
│   │   ├── schemas.py        # Pydantic request/response models
│   │   └── enums.py          # Status enums & constants
│   │
│   ├── middleware/            # Cross-cutting concerns
│   │   ├── cors.py           # CORS configuration
│   │   └── error_handler.py  # Global exception handling
│   │
│   └── utils/                 # Utilities
│       └── background_tasks.py # Async job processing
│
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
└── .gitignore               # Security & cleanup
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

### 4-D Prompt Engine Workflow
1. **Deconstruct** → Extract coin, timeframe, budget from user input
2. **Diagnose** → Validate and clarify the request
3. **Develop** → OpenAI optimizes prompt for crypto analysis
4. **Deliver** → Grok generates comprehensive analysis with sentiment, news, recommendations

### Request Flow
```mermaid
graph LR
    A[User Input] --> B[Validation]
    B --> C[OpenAI Service]
    C --> D[Prompt Optimization]
    D --> E[Grok Service]
    E --> F[Market Analysis]
    F --> G[Query Logging]
    G --> H[Response]
```

### Architecture Benefits
- **Modular Design**: Each component has single responsibility
- **Type Safety**: Full TypeScript/Python type coverage
- **Error Handling**: Centralized exception management
- **Scalability**: Service layer ready for microservices
- **Testing**: Clean architecture supports unit testing
- **Monitoring**: Built-in logging and analytics

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- OpenAI API Key
- Grok API Key

### Backend Setup

```bash
# Clone the repository
git clone <repo_url>
cd CoinGrok-mvp/coingrok_backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys:
# OPENAI_API_KEY=your-openai-key
# GROK_API_KEY=your-grok-key
# DATABASE_URL=sqlite:///./coingrok.db

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install
# or
pnpm install

# Start development server
npm run dev
# or  
pnpm dev
```

Visit `http://localhost:3000` to access the application.

### 🧪 Testing the API

**Health Check:**
```bash
curl http://localhost:8000/health
# Response: {"status": "ok", "active_jobs": 0}
```

**Synchronous Analysis:**
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Analyze Bitcoin over 7 days with $500"}'
```

**Async Analysis:**
```bash
# Start job
curl -X POST "http://localhost:8000/analyze-async" \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Deep analysis of Ethereum market trends"}'

# Check results (use job_id from above)
curl http://localhost:8000/analyze-async/{job_id}
```

**API Documentation:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 📚 API Documentation

### Core Endpoints

#### `POST /analyze`
Synchronous crypto analysis with immediate response
```json
{
  "user_input": "Analyze Bitcoin over 7 days with $500"
}
```

**Response:**
```json
{
  "optimized_prompt": "Professional crypto analysis prompt...",
  "analysis": "Comprehensive market analysis with sentiment, news, recommendations..."
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

#### `GET /health`
Health check with active job count

#### `GET /query-logs`
View recent query history (debugging)

### Database Schema

#### QueryLog Table
Tracks all user queries for analytics and billing:
- `user_id`: User identifier (currently "test_user")
- `user_input`: Original query
- `ai_result`: Final analysis result
- `response_time_ms`: Performance metrics
- `success`: Query completion status

#### AnalysisJob Table  
Manages asynchronous job processing:
- `job_id`: UUID for external tracking
- `status`: queued → processing_openai → processing_grok → completed
- `optimized_prompt`: OpenAI-generated prompt
- `analysis`: Final Grok analysis

## 🚀 Production Deployment

### Environment Variables

**Backend (.env)**
```bash
# Required API Keys
OPENAI_API_KEY=your-openai-api-key
GROK_API_KEY=your-grok-api-key

# Database Configuration
DATABASE_URL=postgresql://user:pass@localhost:5432/coingrok  # Production
# DATABASE_URL=sqlite:///./coingrok.db  # Development

# Security & Performance
CORS_ORIGINS=https://coingrok.vercel.app,https://your-domain.com
LOG_LEVEL=INFO
DEBUG=false

# Optional Configuration
JOB_CLEANUP_HOURS=24
MAX_USER_INPUT_LENGTH=5000
```

**Frontend (.env.local)**
```bash
NEXT_PUBLIC_API_URL=https://your-backend-domain.com
```

### Deployment Options

#### Backend Deployment
**Render/Railway/Fly.io:**
```yaml
# render.yaml
services:
- type: web
  name: coingrok-api
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
DATABASE_URL=sqlite:///./coingrok.db
```

---

## 📊 Monitoring & Analytics

### Built-in Logging
- Request/response timing with performance metrics
- Error tracking with categorization and stack traces
- API usage metrics and patterns
- Database query performance monitoring

### Query Analytics
Access `/query-logs` endpoint to monitor:
- User query patterns and trends
- Response times and performance bottlenecks
- Success/failure rates by endpoint
- Popular analysis types and usage insights

### Health Monitoring
- `/health` endpoint for uptime monitoring
- Automatic cleanup of old jobs and data
- Database connection health checks
- Memory and resource usage tracking

## 🛣️ Roadmap

### Phase 1: Authentication & Security ✅
- [x] Database-based query logging
- [x] CORS security configuration
- [x] Input validation and sanitization
- [ ] Google OAuth integration (Supabase)
- [ ] JWT token authentication
- [ ] User management system

### Phase 2: Business Features
- [ ] Subscription tiers (Free/Pro/Premium)
- [ ] Stripe payment integration
- [ ] Usage-based billing system
- [ ] Query limits enforcement
- [ ] User dashboard and analytics

### Phase 3: Advanced Analytics
- [ ] Real-time crypto data integration
- [ ] Interactive charts and visualizations
- [ ] Portfolio tracking capabilities
- [ ] Automated alerts and notifications
- [ ] Historical analysis comparison

### Phase 4: Scale & Performance
- [ ] Redis caching layer
- [ ] Rate limiting middleware
- [ ] API versioning strategy
- [ ] Microservices architecture
- [ ] Docker containerization

## 🙏 Acknowledgments

- **OpenAI** - GPT-4 for intelligent prompt optimization
- **Grok AI** - Advanced crypto market analysis capabilities
- **FastAPI** - High-performance async API framework
- **Next.js** - React framework for production applications
- **SQLModel** - Type-safe database ORM with automatic API integration

---

**Built with ❤️ by Alexandru G. Mihai & Adrian Ungureanu**

*Transforming crypto curiosity into confident investment decisions through AI-powered analysis.*

> 🚀 **Ready for Production**: This refactored architecture provides a solid foundation for scaling, monitoring, and maintaining a professional cryptocurrency analysis service.
