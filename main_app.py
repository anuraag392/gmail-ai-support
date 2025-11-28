import streamlit as st
from streamlit.web.server import Server

from auth.server import app as fastapi_app
from app.frontend.login import main as login_page
from app.frontend.dashboard import main as dashboard_page
from app.frontend.settings import main as settings_page

# mount FastAPI
Server.get_current()._register_app("/auth", fastapi_app)

def main():
    st.set_page_config(layout="wide")

    if "user_id" not in st.session_state:
        login_page()
        return

    page = st.sidebar.radio("Navigation", ["Dashboard", "Settings"])

    if page == "Dashboard":
        dashboard_page()
    else:
        settings_page()

if __name__ == "__main__":
    main()
