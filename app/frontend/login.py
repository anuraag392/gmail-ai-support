import streamlit as st
import requests

def main():
    st.title("Gmail AI Support — Login")

    # Already logged in
    if "user_id" in st.session_state:
        st.success(f"Logged in as {st.session_state['user_id']}")
        return

    query = st.query_params

    if "login_success" in query and "user" in query:
        st.session_state["user_id"] = query["user"]
        st.success("Login successful! Redirecting...")
        st.experimental_rerun()

    if st.button("Sign in with Google"):
        resp = requests.get(st.secrets["APP_URL_BACKEND"] + "/auth/login")
        auth_url = resp.json()["auth_url"]
        st.markdown(
            f"<meta http-equiv='refresh' content='0; url={auth_url}'/>",
            unsafe_allow_html=True
        )
