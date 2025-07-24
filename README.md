### CoinGrok MVP – AI-Powered Crypto Analysis Tool

CoinGrok is a crypto analytics MVP that leverages the **Grok xAI API** and **OpenAI** to dynamically generate investment insights based on user input. It uses a 4-D Prompt Engine (**Deconstruct → Diagnose → Develop → Deliver**) to convert simple user queries or form inputs into structured prompts and deliver AI-powered analysis.

---

## ⚙ Core Tech Stack

- **Python 3.10+** – backend logic and prompt engine  
- **FastAPI** *(planned)* – for backend API development  
- **OpenAI API** – for LLM-based prompt optimization  
- **Grok xAI API** – for sentiment, news, and market data  
- **VS Code** – dev environment  
- **GitHub** – version control  

---

##  How It Works (Current CLI Version)

1. The user inputs either:
   - A sentence like: `Analyze ETH in 7d with $300`
   - Or structured values like: `ETH 7d 300`

2. The 4-D Prompt Engine runs:
   - **Deconstruct**: Parses coin, timeframe, budget  
   - **Diagnose**: Validates and sanitizes input  
   - **Develop**: Builds an AI-ready prompt  
   - **Deliver**: Prints final prompt to simulate Grok input  

---

##  Example CLI Usage

python main.py


**Example query (sentence-style):**

Analyze ETH in 7d with $300


**Example query (form-style):**

ETH 7d 300


**Output:**

 Final Prompt:

You are an AI crypto assistant. Analyze ETH over the last 7d with an investment budget of $300.

Use Grok tools to return:

    Sentiment from X (Twitter)

    News overview from CoinGecko/CMC

    Market snapshot (price, volume, volatility)

    Buy/Sell Recommendation

    Risk Score (1–10)

Disclaimer: This is not financial advice.


---

##  Architecture Plan (WIP)

- Current: CLI-based prototype  
- Next steps:
  -  Frontend input form  
  -  Backend API (FastAPI)  
  -  Dynamic prompt engine  
  -  Grok + OpenAI integration  
  -  Display structured analysis cards  

---

##  [PRD v1.1 – Product Requirements Document](https://github.com/GhostRobo-MAG/CoinGrok-mvp/blob/main/PRD_v1.1.md)

---

##  Future Features

- Toggle between “Simple” and “Pro” analysis modes  
- Sentiment trend chart from past 7 days  
- Downloadable PDF reports  
- Save & compare previous analyses  
- User auth & saved queries (optional)

---

##  Built by Ghost

Aspiring Product Manager transitioning from automotive → tech.  
This is my first hands-on product: learning Python + building a real app.

---
