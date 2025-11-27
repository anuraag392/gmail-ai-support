import streamlit as st

def main():
    st.title("🔐 Login")

    st.info("This is the login page. Google OAuth will be added here soon.")

    # Temporary fake login button
    if st.button("Login as Test User"):
        st.session_state["user_id"] = "test_user_123"
        st.success("You are logged in!")
        st.rerun()
