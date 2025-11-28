import google.generativeai as genai
import streamlit as st
import json

# Configure Gemini
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

model = genai.GenerativeModel("gemini-2.0-flash")

def categorize_email(subject, body, sender):
    prompt = f"""
You are an advanced classification AI. Return STRICT JSON only.

Your job:
- Clean the email
- Detect if sender domain is legit or suspicious
- Classify email into one category

Allowed categories:
1. Newsletter / Marketing Blast
2. Sales Outreach / Lead Gen
3. Genuine Job Opportunity
4. Fake Job Offer / Scam
5. Personal Message
6. Support Query
7. Internal Company Email
8. Auto-generated / System Notification
9. Other

Return STRICT JSON only:

{{
  "category": "<category>",
  "confidence": 0.0,
  "is_legit_company": false,
  "detected_sender_domain": "<domain>",
  "reason": "<short reason>"
}}

DO NOT RETURN ANY TEXT OUTSIDE JSON.
Subject: {subject}
Sender: {sender}
Body: {body}
"""

    response = model.generate_content(prompt).text.strip()

    import json
    # Try to fix when model wraps JSON in extra text
    try:
        # Find first '{' and last '}'
        start = response.find("{")
        end = response.rfind("}") + 1
        clean_json = response[start:end]

        parsed = json.loads(clean_json)
        return parsed

    except Exception as e:
        return {
            "category": "Other",
            "confidence": 0.0,
            "is_legit_company": False,
            "detected_sender_domain": "",
            "reason": f"JSON parsing failed: {str(e)}"
        }


def generate_reply(category, subject, body, sender):
    prompt = f"""
Write a professional, friendly, human-like email reply.

Category: {category}
Sender Email: {sender}
Subject: {subject}
Customer Message: {body}

Rules:
- Be brief but helpful.
- Sound human, empathetic, professional.
- Add relevant information based on the email type.
- Do NOT mention AI.
- Do NOT hallucinate information.
"""

    resp = model.generate_content(prompt)
    return resp.text.strip()
