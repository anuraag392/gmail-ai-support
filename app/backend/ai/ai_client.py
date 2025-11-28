import google.generativeai as genai
import streamlit as st
import json

# Configure Gemini
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

model = genai.GenerativeModel("gemini-2.0-flash")

def categorize_email(subject, body, sender):
    prompt = f"""
You are an advanced email classification AI. Your task is to categorize emails with extremely high accuracy.

FIRST, clean the message:
- remove signatures
- remove quoted replies
- remove forwarding history
- ignore disclaimers
- focus on the actual intent

SECOND, evaluate the sender domain:
- Is it from a real company?
- Does the domain exist?
- Is it a common spam domain (gmail/yahoo/outlook for "job offers")?
- Does it match the company mentioned inside the email?

THIRD, classify into EXACTLY ONE category:

1. Newsletter / Marketing Blast  
   - mass mailers, promotions, offers, digest emails  
   - contains "unsubscribe", "update preferences", tracking pixels

2. Sales Outreach / Lead Gen  
   - cold outreach  
   - sales pitch, demo request, SaaS product selling

3. Genuine Job Opportunity  
   ONLY IF:  
   - domain is corporate (example: @google.com, @tcs.com)  
   - message style is formal  
   - contains JD, compensation range, recruiter signature  

4. Fake Job Offer / Scam  
   IF:  
   - sender uses free email (gmail/yahoo) pretending to be a company  
   - no company domain  
   - promise very high salary  
   - asks for money, documents, registration fee  

5. Personal Message  
   - from an individual  
   - no marketing  
   - no sales pitch  
   - personal conversation style  

6. Customer Support Query  
   - refund, order issue, complaint, product question  
   (Your old categories will be handled at reply-generation stage.)

7. Internal Company Email  
   - if sender shares same domain as the user  
   - internal communication  

8. Auto-generated / System Notification  
   - password reset  
   - login alerts  
   - shipping updates  
   - invoices

9. Other  
   - doesn't fit any above category  

Return output ONLY as JSON:

{{
  "category": "<exact_category_name>",
  "confidence": "<0.00 to 1.00>",
  "is_legit_company": "<true/false>",
  "detected_sender_domain": "<domain>",
  "reason": "<short justification>"
}}

Email Subject: {subject}
Email Body: {body}

Return ONLY the category name.
"""
    resp = model.generate_content(prompt)
    return resp.text.strip()
    try:
        return json.loads(response)
    except:
        return {
            "category": "Other",
            "confidence": 0.3,
            "is_legit_company": False,
            "detected_sender_domain": "",
            "reason": "Could not parse AI response."
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
