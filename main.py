import time
import re

from app.config.config import POLL_INTERVAL_SECONDS
from app.backend.gmail.gmail_client import (
    get_service,
    list_unread_messages,
    get_message_details,
    create_message,
    send_message,
    mark_as_read
)
from app.backend.ai.llm_client import classify_email, generate_reply
from app.backend.erp.erp_client import get_customer_data_from_erp
from store import load_processed_ids, save_processed_ids
from app.backend.gmail.gmail_client import list_recent_messages



def extract_email_address(sender_str: str) -> str:
    """
    Extract clean email from strings like:
    'Google <noreply@google.com>' or 'John Doe <abc@example.com>'
    """
    match = re.search(r"<(.+?)>", sender_str)
    if match:
        return match.group(1)
    return sender_str  # fallback


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


def process_once():
    service = get_service()
    processed_ids = load_processed_ids()

    messages = list_recent_messages(service, minutes=5, max_results=2)
    if not messages:
        print("No unread emails.")
        return

    print(f"\nFound {len(messages)} unread emails.")

    for msg_meta in messages:
        msg_id = msg_meta["id"]

        # skip if already processed
        if msg_id in processed_ids:
            continue

        details = get_message_details(service, msg_id)
        subject = details["subject"]
        raw_body = details["body"]
        body = clean_email_body(raw_body)
        raw_from = details["from"]

        print(f"\n------------------------------------------------")
        print(f"Processing email ID: {msg_id}")
        print("Raw sender:", raw_from)

        sender_email = extract_email_address(raw_from)
        print("Extracted email:", sender_email)

        # 1. skip no-reply addresses
        if is_no_reply(sender_email):
            print("🚫 Skipping NO-REPLY/System email:", sender_email)
            processed_ids.add(msg_id)
            save_processed_ids(processed_ids)
            continue

        print("\nEmail Subject:", subject)
        print("Email Body:\n", body)

        # 2. classify
        category = classify_email(subject, body)
        print("\nDetected Category:", category)

        # 3. ERP lookup (empty for now)
        erp_data = get_customer_data_from_erp(body)

        # 4. generate reply
        reply_text = generate_reply(subject, body, category, erp_data)

        print("\n🔵 Proposed Reply:\n")
        print(reply_text)
        print("\n------------------------------------------------")

        # 5. ask user before sending
        choice = input("Do you want to send this reply? (y/n): ").strip().lower()
        if choice != "y":
            print("❌ Skipped sending.")
            processed_ids.add(msg_id)
            save_processed_ids(processed_ids)
            continue

        # 6. send email
        reply_msg = create_message(sender_email, f"Re: {subject}", reply_text)
        send_message(service, reply_msg)
        print("✅ Reply sent!")

        # 7. mark as done
        mark_as_read(service, msg_id)
        processed_ids.add(msg_id)
        save_processed_ids(processed_ids)
def clean_email_body(body: str) -> str:
    """
    Remove quoted email threads, previous replies, signatures, and metadata.
    Keeps only the NEW message written by the other person.
    """

    # Remove lines starting with ">"
    body = "\n".join([line for line in body.splitlines() if not line.strip().startswith(">")])

    # Remove Gmail reply headers like:
    # "On Fri, 28 Nov 2025, Someone wrote:"
    body = re.split(r"On.*wrote:", body, flags=re.IGNORECASE)[0]

    # Remove signatures (common patterns)
    body = re.split(r"Thanks,|Regards,|Sincerely,|Best,", body)[0]

    # Trim whitespace
    body = body.strip()

    return body



def main():
    print("Starting Gmail AI Agent (ASK BEFORE REPLY)...")
    while True:
        try:
            process_once()
        except Exception as e:
            print("\n❌ Error:", e)
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
