import requests
from app.config.config import GEMINI_API_KEY

MODEL = "gemini-2.0-flash"
BASE_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"


def call_gemini(prompt: str) -> str:
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}

    data = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ]
    }

    resp = requests.post(BASE_URL, headers=headers, params=params, json=data, timeout=40)
    resp.raise_for_status()

    try:
        return resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    except:
        return ""
    

def classify_email(email_subject: str, email_body: str) -> str:
    prompt = f"""
You are an email classifier.

Classify the email into ONE category:
support, billing, sales, complaint, general.

Subject: {email_subject}
Body:
{email_body}

Return ONLY the category word.
"""
    label = call_gemini(prompt).lower().strip()

    for c in ["support", "billing", "sales", "complaint", "general"]:
        if c in label:
            return c

    return "general"


def generate_reply(subject, body, category, erp_data):
    prompt = f"""
You are an AI email support agent.

Email category: {category}

Customer email:
{body}

ERP DATA:
{erp_data}

Write a polite, short, professional reply with:
- Greeting
- Clear simple explanation
- Use ERP data when helpful
- Short sign-off
- No markdown, no formatting

Write the full email reply:
"""
    return call_gemini(prompt)
