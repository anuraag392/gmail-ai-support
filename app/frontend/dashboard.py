import streamlit as st

from app.database.db import (
    init_db,
    get_pending_emails_for_user,
    log_email,
    update_email_status,
    get_email_log_by_id
)

from app.backend.gmail.gmail_client import get_gmail_service_for_user, create_reply_message, send_message
from app.config.config import GMAIL_USER
from app.database.db import get_pending_emails_for_user
from app.backend.gmail.gmail_client import fetch_unread_emails_for_user, create_reply_message
from app.backend.ai.ai_client import categorize_email, generate_reply

def main():
    
    st.set_page_config(page_title="Email Support Dashboard", layout="wide")
    st.title("📨 AI Email Support Dashboard")

    init_db()
    
    current_user = st.session_state.get("user_id")
    if not current_user:
        st.error("You must be logged in to view this page.")
        st.stop()

    st.write(f"Logged in as: **{current_user}**")
    
    
    if st.button("🔄 Fetch latest unread emails"):
        try:
            emails = fetch_unread_emails_for_user(current_user)

            if not emails:
                st.info("No new unread emails found.")
            else:
                for e in emails:
                    log_email(
                        user_id=current_user,
                        gmail_msg_id=e["gmail_msg_id"],
                        from_email=e["from_email"],
                        subject=e["subject"],
                        body=e["body"],
                        category=e["category"],
                        confidence=e["confidence"],
                        is_legit_company=e["is_legit"],
                        sender_domain=e["domain"],
                        reason=e["reason"],
                        suggested_reply="",   # AI reply coming next
                        status="pending"
                    )
                st.success(f"Fetched and stored {len(emails)} emails.")
            st.rerun()
    
        except Exception as ex:
            st.error(f"Error fetching emails: {ex}")
    

    pending = get_pending_emails_for_user(current_user)

    if not pending:
        st.info("No pending emails. Worker hasn't logged anything yet.")
        return

    st.write(f"Pending emails: **{len(pending)}**")

    service = get_gmail_service_for_user(current_user)

    for row in pending:
        with st.expander(f"[{row['id']}] {row['from_email']} — {row['subject']}"):
            st.subheader("Incoming Email")
            st.code(row["body"] or "", language="text")
            
            st.info(f"Category: **{row['category']}** ({row['confidence']*100:.1f}% confidence)")

            if row["is_legit_company"] == 1:
                st.success(f"Legit company domain: {row['sender_domain']}")
            else:
                st.warning(f"Suspicious domain: {row['sender_domain']}")

            st.caption(f"AI reasoning: {row['reason']}")
            
            
            

        # --- AI Suggested Reply ---
            st.subheader("AI Suggested Reply")
            ai_reply = st.text_area(
                "Edit the AI reply before sending:",
                value=row["suggested_reply"],
                height=200,
                key=f"reply_box_{row['id']}"
            )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Approve & Send", key=f"send_{row['id']}"):
                    try:
                        msg = create_reply_message(
                            to=row["from_email"],
                            subject=f"Re: {row['subject']}",
                            body_text=ai_reply,
                        )
                        send_message(current_user, msg)
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
