import base64
from email.message import EmailMessage
from typing import List, Dict

import streamlit as st
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

from app.database.db import get_user_tokens, save_user_tokens


def _build_creds_for_user(user_id: str) -> Credentials:
    row = get_user_tokens(user_id)
    if not row:
        raise RuntimeError(f"No tokens found for user {user_id}. Please log in again.")

    scopes = st.secrets["GMAIL_SCOPES"].split(",")

    creds = Credentials(
        token=row["access_token"],
        refresh_token=row["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=st.secrets["GOOGLE_CLIENT_ID"],
        client_secret=st.secrets["GOOGLE_CLIENT_SECRET"],
        scopes=scopes,
    )

    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Save refreshed tokens
            save_user_tokens(
                user_id=user_id,
                access=creds.token,
                refresh=creds.refresh_token,
                expiry=str(creds.expiry),
                token_type=creds.token_uri,
                scope=",".join(scopes),
            )
        else:
            raise RuntimeError("Invalid Gmail credentials and cannot refresh.")

    return creds


def get_gmail_service_for_user(user_id: str):
    creds = _build_creds_for_user(user_id)
    service = build("gmail", "v1", credentials=creds)
    return service


def _extract_header(headers, name: str, default: str = "") -> str:
    for h in headers:
        if h.get("name", "").lower() == name.lower():
            return h.get("value", default)
    return default


def _get_message_body(payload) -> str:
    """
    Extract plain text body from Gmail message payload.
    Tries text/plain first, falls back to snippet.
    """
    if "body" in payload and payload.get("mimeType", "").startswith("text/"):
        data = payload["body"].get("data")
        if data:
            return base64.urlsafe_b64decode(data).decode(errors="ignore")

    parts = payload.get("parts", [])
    for part in parts:
        if part.get("mimeType") == "text/plain":
            data = part["body"].get("data")
            if data:
                return base64.urlsafe_b64decode(data).decode(errors="ignore")

    # Fallback: return empty string; caller can use snippet if needed
    return ""


def fetch_unread_emails_for_user(user_id: str, max_results: int = 10) -> List[Dict]:
    """
    Fetch unread, non-promotions, non-social emails from INBOX for the given user.
    Returns a list of dicts with: gmail_msg_id, from_email, subject, body
    """
    service = get_gmail_service_for_user(user_id)

    query = "in:inbox is:unread -category:promotions -category:social"
    resp = service.users().messages().list(
        userId="me",
        q=query,
        maxResults=max_results
    ).execute()

    messages = resp.get("messages", [])
    results = []

    if not messages:
        return results

    for meta in messages:
        msg_id = meta["id"]
        msg = service.users().messages().get(
            userId="me",
            id=msg_id,
            format="full"
        ).execute()

        payload = msg.get("payload", {})
        headers = payload.get("headers", [])

        subject = _extract_header(headers, "Subject", "(no subject)")
        from_raw = _extract_header(headers, "From", "")

        # Extract email from "Name <email@domain>" format
        from_email = from_raw
        if "<" in from_raw and ">" in from_raw:
            from_email = from_raw.split("<")[-1].split(">")[0].strip()

        # Skip no-reply style addresses
        lowered = from_email.lower()
        if any(tag in lowered for tag in ["noreply", "no-reply", "donotreply", "do-not-reply", "mailer-daemon"]):
            continue

        body = _get_message_body(payload)
        if not body:
            body = msg.get("snippet", "")

        results.append(
            {
                "gmail_msg_id": msg_id,
                "from_email": from_email,
                "subject": subject,
                "body": body,
            }
        )

    return results


def create_reply_message(to: str, subject: str, body_text: str) -> dict:
    """
    Build a Gmail API message object (base64-encoded) ready to send.
    """
    message = EmailMessage()
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body_text)

    encoded = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {"raw": encoded}
