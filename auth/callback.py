from fastapi import APIRouter, Request
import requests
import streamlit as st
from app.database.db import consume_oauth_state, save_user_tokens

router = APIRouter()

@router.get("/callback")
def oauth_callback(request: Request):
    """
    Step 2 of OAuth:
    Google redirects here after successful login.
    We exchange the code for tokens, fetch user info,
    store tokens, and redirect user back to Streamlit.
    """

    code = request.query_params.get("code")
    state = request.query_params.get("state")

    # Validate OAuth state
    if not consume_oauth_state(state):
        return {"error": "Invalid OAuth state."}

    # Exchange code for access/refresh tokens
    token_url = "https://oauth2.googleapis.com/token"

    data = {
        "code": code,
        "client_id": st.secrets["GOOGLE_CLIENT_ID"],
        "client_secret": st.secrets["GOOGLE_CLIENT_SECRET"],
        "redirect_uri": st.secrets["OAUTH_REDIRECT_URI"],
        "grant_type": "authorization_code",
    }

    token_resp = requests.post(token_url, data=data).json()

    access_token = token_resp["access_token"]
    refresh_token = token_resp.get("refresh_token", "")

    # Fetch user info (email, name)
    profile = requests.get(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    email = profile["email"]
    name = profile.get("name", email.split("@")[0])

    # Save tokens to DB
    save_user_tokens(
        user_id=email,
        access=access_token,
        refresh=refresh_token,
        expiry="",
        token_type="Bearer",
        scope=""
    )

    # Redirect user back to Streamlit app
    app_url = st.secrets["APP_URL"]
    redirect_url = f"{app_url}?login_success=1&user={email}"

    html = f"""
    <html>
        <head>
            <meta http-equiv="refresh" content="0; url={redirect_url}" />
        </head>
        <body>Redirecting back to the app...</body>
    </html>
    """

    return html
