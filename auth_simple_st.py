from dotenv import load_dotenv
from functools import wraps
import os

import streamlit as st

load_dotenv()

APP_EMAIL_ADDRESSES: str = os.getenv("APP_EMAIL_ADDRESSES", '')
APP_PASSWORD: str = os.getenv("APP_PASSWORD", '')


def is_credentialed(email_address: str, password: str) -> bool:
    allowed_email_addresses: list[str] = [email.strip() for email in APP_EMAIL_ADDRESSES.split(",") if email.strip()]
    return email_address in allowed_email_addresses and password == APP_PASSWORD


def require_login(func):
    """A decorator that can be placed atop any Streamlit function requiring a credentialed user to run"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not st.session_state.get("is_credentialed"):
            st.warning("Please log in to continue.")
            return
        return func(*args, **kwargs)
    return wrapper


def login():
    with st.form("Login"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Log in")

        if submit:
            if is_credentialed(email, password):
                st.session_state["is_credentialed"] = True
                st.session_state["user_email"] = email
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid email or password.")


def logout():
    if st.button("Log out"):
        st.session_state.clear()
        st.rerun()
