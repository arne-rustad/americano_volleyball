# import os

import streamlit as st
# import streamlit_authenticator as stauth

# CREDENTIALS = {
#     "usernames": {
#         "plan": {"name": "osvb", "password": os.environ.get("APP_PASSWORD")},
#     }
# }

# COOKIE = {
#     "key": os.environ.get("APP_SECRET"),
#     "expiry_days": 30,
#     "name": "americano-volleyball"
# }


# def authenticate_streamlit():
#     """Set the authentication configuration."""

#     st.session_state.authenticator = stauth.Authenticate(
#         CREDENTIALS,
#         COOKIE["name"],
#         COOKIE["key"],
#         COOKIE["expiry_days"],
#     )
#     is_authenticated = st.session_state.authenticator.login()
#     st.write(is_authenticated)
#     if is_authenticated:
#         st.rerun()


def initialize_streamlit():
    """Initialize the streamlit session state."""
    if not st.session_state.session_id:
        with st.form("username_form"):
            st.markdown("### Define user")
            st.write(
                "Please enter your unique email address. The progress in this application will be stored to this email address."  # noqa E501
            )
            st.session_state.session_id = st.text_input(
                label="Enter your unique email",
                placeholder="example@gmail.no"
            )
            click = st.form_submit_button("Login")
            if click:
                st.rerun()

        st.stop()


def set_page_configs():
    st.set_page_config(
        page_title="Americano Volleyball App",
        # page_icon="frontend/assets/favicon.ico",
        layout="wide",
    )


# def render_user_info():
#     st.markdown(f'<p style="font-size:14px;margin-bottom:0px;bottom:0px"><b>User</b></p><p style="font-size:12px;margin-bottom:0px">{st.session_state.controller.state.session_id}</p>', unsafe_allow_html=True)  # noqa E501

def log_out():
    st.session_state.session_id = None


def at_start():
    set_page_configs()
    # st.session_state.setdefault("initialized", False)
    st.session_state.setdefault("session_id", None)
    # st.session_state.setdefault("authentication_status", None)

    # if not st.session_state["authentication_status"]:
    #     authenticate_streamlit()
    #     st.stop()

    initialize_streamlit()

    with st.sidebar:
        st.markdown(f"**Logged in as**: {st.session_state.session_id}")
        st.button("Logout", on_click=log_out)
        st.divider()
