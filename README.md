# CoinGrok MVP – AI-Powered Crypto Analysis Tool

CoinGrok is a crypto analytics MVP that leverages **Grok xAI** and **OpenAI** to generate investment insights based on user input.

It uses a 4-D Prompt Engine (**Deconstruct → Diagnose → Develop → Deliver**) to transform simple user queries or form inputs into optimized prompts and deliver AI-powered crypto analysis.

---

## 🚀 Current Status (v0.1)

- **Backend:** FastAPI async API (running locally)
- **Endpoints:**
  - `GET /health` – health check
  - `POST /analyze` – async analysis flow (OpenAI + Grok)
- **Prompt Engine:** Connected to OpenAI for prompt optimization
- **Analysis:** Integrated with Grok xAI (wrapped in executor)
- **CLI version:** Still available for testing simple prompts

**Frontend:** Not implemented yet (planned).

---

## ⚙️ Tech Stack

- **Python 3.10+** – backend logic and prompt engine
- **FastAPI (async)** – backend API
- **OpenAI API (Async)** – LLM prompt optimization
- **Grok xAI API** – sentiment, news, and market analysis
- **VS Code** – development environment
- **GitHub** – version control

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
