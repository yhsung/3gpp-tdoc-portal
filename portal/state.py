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
SS_FETCH_URL = "fetch_url"
SS_FETCH_STATUS = "fetch_status"
SS_PENDING_PROMPT = "pending_prompt"

PROVIDER_MODELS = {
    "claude": ["claude-opus-4-5", "claude-sonnet-4-5"],
    "deepseek": ["deepseek-chat", "deepseek-reasoner"],
}

DEFAULT_PROVIDER = "deepseek"
DEFAULT_MODEL = "deepseek-chat"
DEFAULT_FETCH_URL = "https://www.3gpp.org/ftp/meetings_3gpp_sync/RAN1/Docs/"


def init_session_state() -> None:
    """Initialize session state with defaults. Safe to call on every rerun."""
    from portal import fetcher
    from portal.mock_data import get_mock_documents

    # Determine initial documents: try real fetch, fall back to mock.
    if SS_DOCS not in st.session_state:
        url = st.session_state.get(SS_FETCH_URL, DEFAULT_FETCH_URL)
        try:
            docs = fetcher.get_real_documents(url)
            fetch_status = f"Fetched {len(docs)} TDocs from 3GPP"
        except Exception as exc:  # noqa: BLE001
            docs = get_mock_documents()
            fetch_status = f"Fetch failed ({exc}); showing mock data"
        st.session_state[SS_DOCS] = docs
        st.session_state[SS_FETCH_STATUS] = fetch_status
    else:
        # Refresh local availability and titles on every rerun (no network call).
        fetcher.refresh_local_availability(st.session_state[SS_DOCS])

    defaults = {
        SS_SELECTED_DOC_IDS: set(),
        SS_ACTIVE_SESSION_ID: None,
        SS_SESSIONS: [],
        SS_CURRENT_MESSAGES: [],
        SS_DOC_FILTER: "",
        SS_MEETING_FILTER: "All",
        SS_LOADING: False,
        SS_ERROR: None,
        SS_LLM_PROVIDER: DEFAULT_PROVIDER,
        SS_LLM_MODEL: DEFAULT_MODEL,
        SS_FETCH_URL: DEFAULT_FETCH_URL,
        SS_FETCH_STATUS: "",
        SS_PENDING_PROMPT: None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
