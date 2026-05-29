import os

def get_api_key():
    """
    Retrieves the Google API Key from Streamlit Secrets.
    """
    try:
        import streamlit as st
        # Directly using st.secrets as requested
        return st.secrets["GOOGLE_API_KEY"]
    except (ImportError, KeyError, FileNotFoundError):
        # Fallback for CLI tools or local development
        return os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
