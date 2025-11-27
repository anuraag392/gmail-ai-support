import streamlit as st
import google_auth_oauthlib.flow
import google.oauth2.credentials
import google.auth.transport.requests
import requests
import json
from app.database.db import add_user, save_user_tokens


def make_flow():
    # Streamlit secrets
    CLIENT_ID = st.secrets["GOOGLE_CLIENT_ID"]
    CLIENT_SECRET = st.secrets["GOOGLE_CLIENT_SECRET"]
    REDIRECT_URI = st.secrets["REDIRECT_URI"]
    SCOPES = st.secrets["GMAIL_SCOPES"].split(",")

    client_config = {
        "web": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [REDIRECT_URI],
        }
    }

    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_config,
        scopes=SCOPES
    )

    flow.redirect_uri = REDIRECT_URI
    return flow


def main():
    st.title("🔐 Sign in with Google")

    # Check if URL contains ?code=xxx (Google redirect)
    query_params = st.query_params
    code = query_params.get("code", [None])
    if isinstance(code, list):
        code = code[0]

    if code:
        flow = make_flow()

        try:
            flow.fetch_token(code=code)
        except Exception as e:
            st.error(f"OAuth error: {e}")
            return

        credentials = flow.credentials

        # Get user info (Google profile)
        userinfo = requests.get(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            params={"alt": "json"},
            headers={"Authorization": f"Bearer {credentials.token}"},
        ).json()

        user_email = userinfo.get("email")
        user_name = userinfo.get("name", user_email)

        # Save user in DB
        add_user(user_id=user_email, name=user_name)

        # Save tokens in DB
        save_user_tokens(
            user_id=user_email,
            access=credentials.token,
            refresh=credentials.refresh_token,
            expiry=str(credentials.expiry),
            token_type=credentials.token_uri,
            scope=",".join(st.secrets["GMAIL_SCOPES"].split(",")),
        )

        # Log user into session
        st.session_state["user_id"] = user_email

        st.success(f"Logged in as {user_email}")
        st.info("Go to the Dashboard to continue.")
        return

    # If not logged in yet → show Google login button
    flow = make_flow()
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )

    st.write("Click below to log in:")
    st.link_button("🔑 Sign in with Google", auth_url)
