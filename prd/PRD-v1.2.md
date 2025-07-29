# Product Requirements Document (PRD)
## MVP for AI-Powered Crypto Analysis Platform

**Version:** v1.2  
**Prepared by:** Alexandru G. Mihai (PM), July 2025

---

## 1. Overview

A web-based crypto analytics platform that uses AI (via Grok API prompts) to evaluate any cryptocurrency in real time. The backend now provides a stable **API v0.1 (async)** that supports health checks and crypto analysis requests. The tool leverages Grok's native capabilities to analyze sentiment from X (Twitter), aggregate web-based crypto news, and return an investment verdict including price predictions and risk analysis. Prompt generation is powered by a backend LLM-based 4-D prompt engine for dynamic and adaptive query creation.

## 2. Goals

- Help retail investors make informed, data-backed decisions in seconds
- Build a modular prompt engine to flexibly scale analysis across coins
- Launch a working MVP in 6 weeks
- **Current milestone:** Stable async backend endpoints (v0.1)

## 3. Target Users

- Crypto traders and meme coin investors
- Retail investors (beginner to intermediate)
- Degens who want fast signals without doing research

## 4. Core Features (MUST-HAVE for MVP)

### Frontend
- **Coin Input Form:**
  - Inputs: Coin name, timeframe (48h/7d), investment amount

### Backend
- **4-D Prompt Engine:**
  - Deconstruct, Diagnose, Develop, Deliver (OpenAI → Grok)
- **API Endpoints (v0.1):**
  - `/health` – health check
  - `/analyze` – async crypto analysis request
- **AI Integration Layer:**
  - OpenAI for prompt refinement
  - Grok for:
    - Sentiment summary
    - News highlights
    - Price, volume, volatility
    - Price prediction (2 weeks, 3 months)
    - Buy/sell recommendation
    - Risk score (1–10)
- **Error handling:**
  - Clear HTTP status codes for rate limits, timeouts, authentication errors
  - Logs every request
- **Frontend Report Display (Planned):**
  - Structured cards by category: Sentiment, News, Market Snapshot, AI Verdict, Risk Score
- **Fallback Handling:**
  - Prompt templates handle "no data" gracefully

## 5. Backend Architecture Overview (Updated)

### Pipeline (v0.1):
```
User Input → OpenAI Prompt Optimization → Grok Analysis → JSON Response
```

### Stack:
- **Backend:** Python + FastAPI (now async)
- **LLM:** OpenAI API (async client)
- **Analysis:** Grok xAI API (sync, wrapped in executor)
- **Logging:** Python logging
- **Frontend:** React (planned)
- **Deployment:** Render / Railway (planned)

### Endpoints:
- `/health`
- `/analyze`

## 6. Key Decisions (v1.2 Update)

### 1. Async Backend
- Migrated `/analyze` to `async def`
- Used `AsyncOpenAI` for non-blocking requests
- Kept Grok SDK synchronous and wrapped it with `run_in_executor`

**Why:** To prevent blocking during long API calls and prepare for scale.

### 2. Validation
- Used Pydantic model with `@validator` for input sanitation.

**Why:** Prevents empty or invalid user input.

### 3. Minimal Stable v0.1
- Deferred authentication, usage tracking, and cost monitoring to backlog.

**Why:** Focused on delivering a working base API quickly.

## 7. Database / Storage (Optional for MVP)

No change from v1.1. Logging only; persistence remains optional.

## 8. Roadmap (Updated)

### Completed (Week 2–3):
- ✅ Backend scaffold
- ✅ Async `/analyze` endpoint
- ✅ `/health` endpoint
- ✅ Prompt optimization integration (OpenAI)
- ✅ Grok analysis integration
- ✅ Structured error handling and logging

### Next:
- 🔄 Connect frontend input form
- 🔄 Add security/authentication to backend
- 🔄 Monitoring + optional caching

## 9. Risks / Dependencies

No change from v1.1 except:
- **Blocking Grok SDK:** Temporary fix with `run_in_executor`; will revisit if async SDK becomes available.

## 10. Next Steps

- Secure backend (API key or JWT)
- Use environment variables for keys
- Frontend connection
- Monitoring/cost tracking
- Expand error handling
- Unit and integration tests

---

**End of Document – Version 1.2**
