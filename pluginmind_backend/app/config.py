import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROK_API_KEY = os.getenv("GROK_API_KEY")
GROK_API_URL = "https://api.x.ai/v1/chat/completions"

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./coingrok.db")

# For SQLite fallback in development
if DATABASE_URL.startswith("sqlite"):
    import sqlite3
    CONNECT_ARGS = {"check_same_thread": False}
else:
    CONNECT_ARGS = {}
