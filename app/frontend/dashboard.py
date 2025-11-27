import streamlit as st

from app.database.db import init_db, get_pending_emails, update_email_status, get_email_log_by_id
from app.backend.gmail.gmail_client import get_service, create_message, send_message
from app.config.config import GMAIL_USER
from app.database.db import get_pending_emails_for_user
from app.backend.gmail.gmail_client import get_service, create_message, send_message


def main():
    
    st.set_page_config(page_title="Email Support Dashboard", layout="wide")
    st.title("📨 AI Email Support Dashboard")

    init_db()
    
    current_user = st.session_state.get("user_id")
    if not current_user:
        st.error("You must be logged in to view this page.")
        st.stop()

    st.write(f"Logged in as: **{current_user}**")

    pending = get_pending_emails(current_user)

    if not pending:
        st.info("No pending emails. Worker hasn't logged anything yet.")
        return

    st.write(f"Pending emails: **{len(pending)}**")

    service = get_service()

    for row in pending:
        with st.expander(f"[{row['id']}] {row['from_email']} — {row['subject']}"):
            st.subheader("Incoming Email")
            st.code(row["body"] or "", language="text")

            st.subheader("AI Suggested Reply")
            reply_text = st.text_area(
                "Edit reply (optional)",
                value=row["suggested_reply"] or "",
                key=f"reply_{row['id']}",
                height=200,
            )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Approve & Send", key=f"send_{row['id']}"):
                    try:
                        msg = create_message(
                            to=row["from_email"],
                            subject=f"Re: {row['subject']}",
                            body_text=reply_text,
                        )
                        send_message(service, msg)
                        update_email_status(row["id"], "sent")
                        st.success("Reply sent and status updated to 'sent'.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to send: {e}")

            with col2:
                if st.button("❌ Skip (don't send)", key=f"skip_{row['id']}"):
                    update_email_status(row["id"], "skipped")
                    st.warning("Email marked as skipped.")
                    st.rerun()


if __name__ == "__main__":
    main()
