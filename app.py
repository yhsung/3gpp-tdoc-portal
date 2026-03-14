"""3GPP TDoc Portal — Streamlit three-column UI entry point."""
import os

from dotenv import load_dotenv

load_dotenv()

import streamlit as st

from portal import render_left_column, render_middle_column, render_right_column
from portal.state import init_session_state

st.set_page_config(
    page_title="3GPP TDoc Portal",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.title("📡 3GPP TDoc Portal")

# Warn if no API keys are configured
anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
deepseek_key = os.getenv("DEEPSEEK_API_KEY", "")
if not anthropic_key and not deepseek_key:
    st.warning(
        "No API keys detected. Add `ANTHROPIC_API_KEY` or `DEEPSEEK_API_KEY` to a `.env` file to enable chat.",
        icon="⚠️",
    )

init_session_state()

col_left, col_mid, col_right = st.columns([2, 4, 2], gap="medium")

render_left_column(col_left)
render_middle_column(col_mid)
render_right_column(col_right)
