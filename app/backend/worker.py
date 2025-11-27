import time
import re

from app.config.config import POLL_INTERVAL_SECONDS
from app.backend.gmail.gmail_client import (
    get_service,
    list_recent_messages,
    get_message_details,
    mark_as_read
)
from app.backend.ai.ai_client import classify_email, generate_reply
from app.backend.erp.erp_client import get_customer_data_from_erp
from store import load_processed_ids, save_processed_ids
from app.database.db import init_db, log_email


def extract_email_address(sender_str: str) -> str:
    import re as _re
    match = _re.search(r"<(.+?)>", sender_str)
    if match:
        return match.group(1)
    return sender_str


def is_no_reply(email: str) -> bool:
    email = email.lower()
    return (
        "noreply" in email
        or "no-reply" in email
        or "donotreply" in email
        or "do-not-reply" in email
        or "mailer-daemon" in email
        or "notification" in email
        or "auto" in email
    )


def clean_email_body(body: str) -> str:
    body = "\n".join([line for line in body.splitlines() if not line.strip().startswith(">")])
    body = re.split(r"On.*wrote:", body, flags=re.IGNORECASE)[0]
    body = body.strip()
    return body


def process_once():
    service = get_service()
    processed_ids = load_processed_ids()

    # only recent emails, e.g. last 10 minutes
    messages = list_recent_messages(service, minutes=10, max_results=20)
    if not messages:
        print("No recent emails.")
        return

    print(f"\n[WORKER] Found {len(messages)} recent messages.")

    for msg_meta in messages:
        msg_id = msg_meta["id"]

        if msg_id in processed_ids:
            continue

        details = get_message_details(service, msg_id)
        subject = details["subject"]
        raw_body = details["body"]
        raw_from = details["from"]

        sender_email = extract_email_address(raw_from)

        print(f"\n[WORKER] Processing {msg_id} from {sender_email} | Subject: {subject}")

        if is_no_reply(sender_email):
            print("[WORKER] Skipping no-reply/system email.")
            processed_ids.add(msg_id)
            save_processed_ids(processed_ids)
            continue

        body = clean_email_body(raw_body)

        # classify
        category = classify_email(subject, body)
        print("[WORKER] Category:", category)

        # ERP lookup
        erp_data = get_customer_data_from_erp(sender_email, body)

        # generate suggested reply
        suggested_reply = generate_reply(subject, body, category, erp_data)

        # log to DB as pending
        log_email(
            gmail_msg_id=msg_id,
            from_email=sender_email,
            subject=subject,
            body=body,
            category=category,
            suggested_reply=suggested_reply,
            status="pending",
        )
        print("[WORKER] Logged email as pending for review.")

        # mark as processed so we don't re-log
        processed_ids.add(msg_id)
        save_processed_ids(processed_ids)

        # you can decide whether to mark as read or not
        # mark_as_read(service, msg_id)


def main():
    print("Starting BACKGROUND WORKER (no auto-send, just logs)...")
    init_db()
    while True:
        try:
            process_once()
        except Exception as e:
            print("[WORKER] Error:", e)
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
