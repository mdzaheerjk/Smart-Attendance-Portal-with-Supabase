# Attendence/config.py
import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

## streamlit - secrets

def get_env(var_name: str, default=None):
    """
    Prefer Streamlit secrets if available, else environment variable.
    """
    try:
        # st.secrets may not exist outside streamlit runtime; guard it.
        if hasattr(st, "secrets") and st.secrets and var_name in st.secrets:
            return st.secrets[var_name]
    except Exception:
        # ignore streamlit secrets errors and fallback to env
        pass

    return os.getenv(var_name, default)
