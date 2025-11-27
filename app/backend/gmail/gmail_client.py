import base64
import os.path
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from app.config.config import CREDENTIALS_FILE, TOKEN_FILE, GMAIL_USER

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


def get_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    service = build("gmail", "v1", credentials=creds)
    return service


def list_unread_messages(service, max_results=10):
    response = service.users().messages().list(
        userId="me", labelIds=["INBOX", "UNREAD"], maxResults=max_results
    ).execute()
    messages = response.get("messages", [])
    return messages


def get_message_details(service, msg_id):
    msg = service.users().messages().get(userId="me", id=msg_id, format="full").execute()

    headers = msg.get("payload", {}).get("headers", [])
    subject = next((h["value"] for h in headers if h["name"] == "Subject"), "")
    from_email = next((h["value"] for h in headers if h["name"] == "From"), "")

    body = ""
    payload = msg.get("payload", {})
    if "parts" in payload:
        for part in payload["parts"]:
            if part.get("mimeType") == "text/plain":
                data = part["body"].get("data")
                if data:
                    body = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
                    break
    else:
        data = payload.get("body", {}).get("data")
        if data:
            body = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

    return {
        "id": msg_id,
        "subject": subject,
        "from": from_email,
        "body": body,
    }


def create_message(to, subject, body_text):
    message = MIMEText(body_text)
    message["to"] = to
    message["from"] = GMAIL_USER
    message["subject"] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {"raw": raw}


def send_message(service, message):
    sent = (
        service.users()
        .messages()
        .send(userId="me", body=message)
        .execute()
    )
    return sent


def mark_as_read(service, msg_id):
    service.users().messages().modify(
        userId="me",
        id=msg_id,
        body={"removeLabelIds": ["UNREAD"]},
    ).execute()
def list_recent_messages(service, minutes=5, max_results=20):
    query = f"newer_than:{minutes}m"
    response = service.users().messages().list(
        userId="me",
        q=query,
        labelIds=["INBOX"],
        maxResults=max_results
    ).execute()
    return response.get("messages", [])
