import streamlit as st

def main():
    st.title("⚙️ Settings")

    if "user_id" not in st.session_state:
        st.error("Please log in first.")
        return

    st.subheader("User Settings")

    st.write(f"Logged in as: **{st.session_state.get('user_id')}**")

    st.info("Settings page placeholder. More features coming soon!")

    st.checkbox("Enable Email Notifications", value=True)
    st.checkbox("Enable AI Suggestions", value=True)
    st.checkbox("Dark Mode (Coming Soon)", value=False)
