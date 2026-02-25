"""Universal secrets helper — checks st.secrets first, falls back to env vars."""

import os

try:
    import streamlit as st
except ImportError:
    st = None


def get_secret(key, default=""):
    """Get secret from Streamlit secrets or environment variables."""
    if st is not None:
        try:
            val = st.secrets.get(key, "")
            if val:
                return val
        except Exception:
            pass
    return os.environ.get(key, default)
