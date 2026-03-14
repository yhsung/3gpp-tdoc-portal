"""Session state key constants and initializer for the 3GPP TDoc Portal."""
import streamlit as st

# Session state keys
SS_DOCS = "docs"
SS_SELECTED_DOC_IDS = "selected_doc_ids"
SS_ACTIVE_SESSION_ID = "active_session_id"
SS_SESSIONS = "sessions"
SS_CURRENT_MESSAGES = "current_messages"
SS_DOC_FILTER = "doc_filter"
SS_MEETING_FILTER = "meeting_filter"
SS_LOADING = "loading"
SS_ERROR = "error"
SS_LLM_PROVIDER = "llm_provider"
SS_LLM_MODEL = "llm_model"

PROVIDER_MODELS = {
    "claude": ["claude-opus-4-5", "claude-sonnet-4-5"],
    "deepseek": ["deepseek-chat", "deepseek-reasoner"],
}

DEFAULT_PROVIDER = "claude"
DEFAULT_MODEL = "claude-opus-4-5"


def init_session_state() -> None:
    """Initialize session state with defaults. Safe to call on every rerun."""
    from portal.mock_data import get_mock_documents, get_mock_sessions

    defaults = {
        SS_DOCS: get_mock_documents(),
        SS_SELECTED_DOC_IDS: set(),
        SS_ACTIVE_SESSION_ID: None,
        SS_SESSIONS: get_mock_sessions(),
        SS_CURRENT_MESSAGES: [],
        SS_DOC_FILTER: "",
        SS_MEETING_FILTER: "All",
        SS_LOADING: False,
        SS_ERROR: None,
        SS_LLM_PROVIDER: DEFAULT_PROVIDER,
        SS_LLM_MODEL: DEFAULT_MODEL,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
