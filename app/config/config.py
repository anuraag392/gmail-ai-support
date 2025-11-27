import os
from dotenv import load_dotenv

load_dotenv()

# Gmail
GMAIL_USER = os.getenv("GMAIL_USER")  # your email, e.g. "you@gmail.com"

# Gemini API (free tier via Google AI Studio)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.0-flash"

# Polling
POLL_INTERVAL_SECONDS = 60  # time between checks

# Paths
CREDENTIALS_FILE = "credentials.json"      # from Google Cloud (Gmail API)
TOKEN_FILE = "token.json"                  # created after first auth
PROCESSED_IDS_FILE = "processed_ids.json"
DB_FILE = "app/database/database.db"

