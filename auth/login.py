from fastapi import APIRouter
import uuid
import urllib.parse
import streamlit as st
from app.database.db import create_temp_oauth_state

router = APIRouter()

@router.get("/login")
def oauth_login():
    """
    Step 1 of OAuth:
    Generate a Google OAuth URL and return it to the frontend.
    """
    # Create a temporary state token to prevent CSRF
    state = str(uuid.uuid4())
    create_temp_oauth_state(state)

    client_id = st.secrets["GOOGLE_CLIENT_ID"]
    redirect_uri = st.secrets["OAUTH_REDIRECT_URI"]

    scopes = st.secrets["GMAIL_SCOPES"]
    scopes_encoded = urllib.parse.quote(scopes)

    auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope={scopes_encoded}"
        f"&access_type=offline"
        f"&prompt=consent"
        f"&state={state}"
    )

    return {"auth_url": auth_url}
