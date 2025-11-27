import google.generativeai as genai
import streamlit as st

# Configure Gemini
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

model = genai.GenerativeModel("gemini-2.0-flash")

def categorize_email(subject, body):
    prompt = f"""
Classify the following email into ONE category.

Categories:
- Complaint
- Order Issue
- Refund Request
- Technical Issue
- General Inquiry
- Other

Email Subject: {subject}
Email Body: {body}

Return ONLY the category name.
"""
    resp = model.generate_content(prompt)
    return resp.text.strip()


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
