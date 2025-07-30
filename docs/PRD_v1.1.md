#  Product Requirements Document (PRD)
## MVP for AI-Powered Crypto Analysis Platform

**Version:** v1.1  
**Prepared by:** Ghost (PM), July 2025  

---

## 1. Overview
A web-based crypto analytics platform that uses AI (via Grok API prompts) to evaluate any cryptocurrency in real time. The tool leverages Grok's native capabilities to analyze sentiment from X (Twitter), aggregate web-based crypto news, and return an investment verdict including price predictions and risk analysis. Prompt generation is powered by a backend LLM-based 4-D prompt engine for dynamic and adaptive query creation.

---

## 2. Goals
- Help retail investors make informed, data-backed decisions in seconds.  
- Build a modular prompt engine to flexibly scale analysis across coins.  
- Launch a working MVP in 6 weeks.  

---

## 3. Target Users
- Crypto traders and meme coin investors  
- Retail investors (beginner to intermediate)  
- Degens who want fast signals without doing research  

---

## 4. Core Features (MUST-HAVE for MVP)

###  Coin Input Form (frontend)
- Inputs: Coin name, timeframe (48h/7d), investment amount

###  4-D Prompt Engine (backend)
Implements a four-stage logic pipeline:
- **Deconstruct** - Parse user inputs, extract key entities (coin, timeframe, intent, filters)  
- **Diagnose** - Validate input clarity; resolve ambiguity or missing elements  
- **Develop** - Generate structured prompt using OpenAI API, adapting tone and format to user filters (e.g., risk-seeking vs conservative)  
- **Deliver** - Final prompt is sent to Grok’s xAI API  

###  AI Integration Layer
Uses Grok’s built-in tools:
- `x_keyword_search`, `x_semantic_search` for sentiment from X  
- `web_search`, `browse_page` for news, market data from CoinGecko/CMC  

**Fetches:**
- Sentiment summary  
- News highlights  
- Price, volume, volatility  
- Price prediction (2 weeks, 3 months)  
- Buy/sell recommendation  
- Risk score (1–10)  

⚠ Always includes disclaimer:  
_"This is not financial advice; trade at your own risk."_

###  Fallback Handling
Prompt templates include fallback conditions (e.g., no data → return "No notable news during timeframe")

###  Frontend Report Display
- Structured cards by category:  
  - Sentiment  
  - News  
  - Market Snapshot  
  - AI Verdict  
  - Risk Score  
- Optional: Filters for risk, volatility, or timeframe  

---

## 5. Backend Architecture Overview

**Pipeline:**
→ User Input → Coin, Timeframe, Budget, Optional Filters
→ 4-D Prompt Engine → Processes inputs into prompt via OpenAI
→ Grok API Call → Executes structured prompt using Grok tools
→ Parse Grok Response → Format for display
→ Render to Frontend → Display as analysis cards


**Stack Suggestion:**
- Python + FastAPI (backend)  
- OpenAI API (for prompt optimization)  
- Grok xAI API (for analysis)  
- Firebase or PostgreSQL (query logs / optional caching)  
- React (frontend)  
- Render or Railway (deployment)  

---

## 6. Database / Storage (Optional for MVP)
Log previous queries and results

**Table structure:**
- `queries`: id, coin, timeframe, budget, timestamp  
- `results`: query_id, prompt, grok_response, parsed_output  

---

## 7. Roadmap: Idea → MVP (6 Milestones)

**Milestones 0–1:**  
- Infrastructure setup, GitHub, Notion workspace, CLI version of app  
- Python fundamentals + OpenAI API prompt builder logic  

**Milestones 2:**  
- Backend scaffold (FastAPI), 4-D engine implementation  
- Prompt generation module, OpenAI connection  

**Milestones 3:**  
- Connect backend to Grok API  
- Test basic sentiment + news tool calls  

**Milestones 4:**  
- Frontend input form + result display (React or HTML)  
- Connect frontend to backend  

**Milestones 5:**  
- Bug fixes, UI polish  
- Add simple filters (e.g., timeframe, volatility)  
- Logging and caching (Firebase/Postgres)  

**Milestones 6:**  
- MVP Launch  
- Early user feedback (Reddit, X communities)  

---

## 8. Risks / Dependencies
- Grok API latency or access limits → Mitigate with fallback prompts and caching  
- OpenAI cost for LLM prompt generation → Monitor usage  
- User misunderstanding output as financial advice → Enforce disclaimers  
- Frontend performance with large Grok outputs → Use lazy loading/cards  

---

## 9. Next Steps
- Finalize prompt templates using the 4-D engine  
- Build CLI version of prompt → OpenAI → Grok flow  
- Set up Notion workspace with PM log + backlog  
- Build app backlog with Epics: “Prompt Engine”, “Frontend Form”, “Grok Connection”  

---

**End of Document – Version 1.1**
