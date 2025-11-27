import streamlit as st

# Import pages
from app.frontend.dashboard import main as dashboard_page
from app.frontend.login import main as login_page
from app.frontend.settings import main as settings_page
from app.database.db import init_db

# Streamlit app config
st.set_page_config(
    page_title="AI Gmail Support App",
    layout="wide",
)

def main():
    init_db()
    st.sidebar.title("📌 Navigation")

    page = st.sidebar.radio(
        "Go to:",
        ("Login", "Dashboard", "Settings")
    )

    if page == "Login":
        login_page()

    elif page == "Dashboard":
        # Require login before dashboard
        if "user_id" not in st.session_state:
            st.error("Please log in first.")
            return
        dashboard_page()

    elif page == "Settings":
        if "user_id" not in st.session_state:
            st.error("Please log in first.")
            return
        settings_page()


if __name__ == "__main__":
    main()
