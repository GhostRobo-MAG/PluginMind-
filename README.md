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

## 🔄 How It Works

1. **User Input:**
   - Natural language: `Analyze ETH in 7d with $300`
   - Structured: `ETH 7d 300`

2. **Backend flow:**
   - **Deconstruct** – Parse coin, timeframe, budget
   - **Diagnose** – Validate and sanitize input
   - **Develop** – Use OpenAI to build an optimized AI prompt
   - **Deliver** – Send optimized prompt to Grok, aggregate results, return JSON

---

## 🛠️ How to Run Locally

### 1. Clone the repo
```bash
git clone <repo_url>
cd coingrok_backend
```

### 2. Create a virtual environment
```bash
python -m venv venv
```

### 3. Activate the virtual environment

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate
```

You should now see `(venv)` at the start of your terminal prompt.

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Set up environment variables

Create a file named `.env` inside the `app/` folder (or at project root if configured that way):

```env
OPENAI_API_KEY=your_openai_api_key
GROK_API_KEY=your_grok_api_key
```

> **Note:** Make sure `.env` is not committed (`.env` is listed in `.gitignore`).

### 6. Run the backend server
```bash
uvicorn main:app --reload
```

### 7. Test the API

Open Swagger UI in your browser: [http://localhost:8000/docs](http://localhost:8000/docs)

- `GET /health` → Should return `{"status": "ok"}`
- `POST /analyze` → Enter:
  ```json
  {
    "user_input": "Analyze BTC for the past 48 hours"
  }
  ```

You'll receive a JSON response with `optimized_prompt` and `analysis`.

### 8. Stopping work

- To stop the server: `Ctrl+C`
- To deactivate the virtual environment: `deactivate`

---

## 📂 Architecture

### Current (v0.1)
```
Frontend (planned)
       │
       ▼
Backend API (FastAPI async)
       │
       ├─ OpenAI (prompt refinement)
       │
       └─ Grok xAI (analysis)
```

### Next Steps:
- Frontend React app
- Secure endpoints (API key / JWT)
- Add monitoring and usage tracking

---

## 📄 Documentation

- prd/PRD-v1.2.md
- API Specification (coming soon )

---

## 🛠️ Future Features

- Toggle between "Simple" and "Pro" analysis modes
- Sentiment trend charts (7-day history)
- Downloadable PDF reports
- Save & compare previous analyses
- User authentication and saved queries

---

## 👤 Built by Alexandru G. Mihai

Aspiring Product Manager transitioning from automotive → tech.

This is my first hands-on product: learning Python and building a real app from scratch.
