"""Portal package — three-column Streamlit render functions."""
from __future__ import annotations

import uuid
from datetime import datetime

import streamlit as st

from portal.mock_data import ChatSession, TDoc
from portal.state import (
    PROVIDER_MODELS,
    SS_ACTIVE_SESSION_ID,
    SS_CURRENT_MESSAGES,
    SS_DOC_FILTER,
    SS_DOCS,
    SS_ERROR,
    SS_FETCH_STATUS,
    SS_FETCH_URL,
    SS_LOADING,
    SS_LLM_MODEL,
    SS_LLM_PROVIDER,
    SS_MEETING_FILTER,
    SS_PENDING_PROMPT,
    SS_SELECTED_DOC_IDS,
    SS_SESSIONS,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _selected_docs() -> list[TDoc]:
    ids = st.session_state[SS_SELECTED_DOC_IDS]
    return [d for d in st.session_state[SS_DOCS] if d.id in ids]


def _generate_title(messages: list[dict]) -> str:
    for msg in messages:
        if msg["role"] == "user":
            text = msg["content"]
            return text[:40] + ("..." if len(text) > 40 else "")
    return "Untitled session"


def _persist_session(messages: list[dict], doc_ids: set[str]) -> None:
    session_id = st.session_state[SS_ACTIVE_SESSION_ID]
    sessions: list[ChatSession] = st.session_state[SS_SESSIONS]
    now = datetime.now()
    for s in sessions:
        if s.session_id == session_id:
            s.messages = list(messages)
            s.doc_ids = list(doc_ids)
            s.last_updated = now
            s.title = _generate_title(messages)
            return
    # New session
    preview = messages[0]["content"][:80] if messages else ""
    sessions.insert(
        0,
        ChatSession(
            session_id=session_id or str(uuid.uuid4()),
            doc_ids=list(doc_ids),
            created_at=now,
            last_updated=now,
            title=_generate_title(messages),
            preview=preview,
            messages=list(messages),
        ),
    )


# ---------------------------------------------------------------------------
# Left column — Document list
# ---------------------------------------------------------------------------

def render_left_column(col: st.delta_generator.DeltaGenerator) -> None:
    with col:
        st.subheader("TDocs")

        # --- 3GPP Fetch controls ---
        st.text_input("Meeting URL", key=SS_FETCH_URL, placeholder="https://www.3gpp.org/ftp/…")

        fb1, fb2 = st.columns(2)
        with fb1:
            if st.button("Fetch TDocs", use_container_width=True):
                from portal import fetcher
                from portal.mock_data import get_mock_documents
                url = st.session_state[SS_FETCH_URL]
                fetcher._cached_fetch_tdoc_ids.clear()
                with st.spinner("Fetching from 3GPP…"):
                    try:
                        docs = fetcher.get_real_documents(url)
                        st.session_state[SS_DOCS] = docs
                        st.session_state[SS_FETCH_STATUS] = f"Fetched {len(docs)} TDocs"
                    except Exception as exc:  # noqa: BLE001
                        st.session_state[SS_DOCS] = get_mock_documents()
                        st.session_state[SS_FETCH_STATUS] = f"Fetch failed: {exc}"
                st.rerun()
        with fb2:
            selected_ids_for_dl: set[str] = st.session_state[SS_SELECTED_DOC_IDS]
            n_sel = len(selected_ids_for_dl)
            dl_label = f"Download ({n_sel})" if n_sel else "Download"
            if st.button(dl_label, use_container_width=True, disabled=n_sel == 0):
                from portal import fetcher
                base_url = st.session_state[SS_FETCH_URL]
                with st.spinner(f"Downloading {n_sel} TDoc(s)…"):
                    results = fetcher.download_and_convert_tdocs(list(selected_ids_for_dl), base_url)
                ok = sum(1 for v in results.values() if "converted" in v or "skipped" in v.lower())
                st.session_state[SS_FETCH_STATUS] = f"Download complete: {ok}/{n_sel} converted"
                # Refresh doc list to reflect new local availability
                try:
                    st.session_state[SS_DOCS] = fetcher.get_real_documents(base_url)
                except Exception:  # noqa: BLE001
                    pass
                st.rerun()

        if st.session_state.get(SS_FETCH_STATUS):
            st.caption(st.session_state[SS_FETCH_STATUS])

        st.divider()

        # --- Filters ---
        st.text_input(
            "Search", value=st.session_state[SS_DOC_FILTER], key=SS_DOC_FILTER, placeholder="Search by ID or title..."
        )

        all_docs: list[TDoc] = st.session_state[SS_DOCS]
        meetings = ["All"] + sorted({d.meeting for d in all_docs})
        meeting_idx = meetings.index(st.session_state[SS_MEETING_FILTER]) if st.session_state[SS_MEETING_FILTER] in meetings else 0
        st.selectbox("Meeting", options=meetings, index=meeting_idx, key=SS_MEETING_FILTER)

        # New Chat button
        if st.button("+ New Chat", use_container_width=True, type="primary"):
            st.session_state[SS_ACTIVE_SESSION_ID] = str(uuid.uuid4())
            st.session_state[SS_CURRENT_MESSAGES] = []
            st.session_state[SS_SELECTED_DOC_IDS] = set()
            st.rerun()

        st.divider()

        # --- Filtered document list ---
        filter_text = st.session_state[SS_DOC_FILTER].lower()
        meeting_filter = st.session_state[SS_MEETING_FILTER]

        filtered = [
            d for d in all_docs
            if (not filter_text or filter_text in d.id.lower() or filter_text in d.title.lower())
            and (meeting_filter == "All" or d.meeting == meeting_filter)
        ]

        selected_ids: set[str] = st.session_state[SS_SELECTED_DOC_IDS]

        with st.container(height=400):
            for doc in filtered:
                c1, c2 = st.columns([1, 6])
                with c1:
                    checked = st.checkbox(
                        f"Select {doc.id}",
                        key=f"chk_{doc.id}",
                        value=doc.id in selected_ids,
                        label_visibility="collapsed",
                    )
                    if checked:
                        selected_ids.add(doc.id)
                    else:
                        selected_ids.discard(doc.id)

                with c2:
                    label = f"**{doc.id}**  \n{doc.title}"
                    st.markdown(label)
                    if doc.available:
                        badge = "✅ local"
                    elif doc.file_type == "zip":
                        badge = "⬇️ remote"
                    else:
                        badge = "🔷 mock"
                    st.caption(f"{badge} · {doc.meeting} · {doc.agenda_item}")

                st.divider()


# ---------------------------------------------------------------------------
# Middle column — Chat
# ---------------------------------------------------------------------------

def render_middle_column(col: st.delta_generator.DeltaGenerator) -> None:
    with col:
        # --- Provider / Model selector ---
        p1, p2 = st.columns(2)
        with p1:
            provider_options = list(PROVIDER_MODELS.keys())
            chosen_provider = st.selectbox(
                "Provider",
                options=provider_options,
                key=SS_LLM_PROVIDER,
                format_func=lambda x: {"claude": "Claude (Anthropic)", "deepseek": "DeepSeek"}.get(x, x),
            )
        with p2:
            model_options = PROVIDER_MODELS[st.session_state[SS_LLM_PROVIDER]]
            # Reset model if it doesn't belong to the selected provider
            if st.session_state[SS_LLM_MODEL] not in model_options:
                st.session_state[SS_LLM_MODEL] = model_options[0]
            st.selectbox(
                "Model",
                options=model_options,
                key=SS_LLM_MODEL,
            )

        sel_docs = _selected_docs()
        n = len(sel_docs)

        if n == 0:
            st.subheader("Chat")
            st.info("Select one or more TDocs from the left to start a conversation.")
        else:
            st.subheader(f"Chat — {n} document{'s' if n > 1 else ''} in context")
            st.caption(" · ".join(f"`{d.id}`" for d in sel_docs))

        # --- Error display ---
        if st.session_state[SS_ERROR]:
            st.error(st.session_state[SS_ERROR])
            if st.button("Dismiss"):
                st.session_state[SS_ERROR] = None
                st.rerun()

        # --- Chat messages area ---
        messages: list[dict] = st.session_state[SS_CURRENT_MESSAGES]
        with st.container(height=480):
            for msg in messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        # --- Input ---
        is_loading = st.session_state[SS_LOADING]
        prompt = st.chat_input(
            "Ask about the selected documents...",
            disabled=is_loading or n == 0,
        )

        # Pick up a prompt that was deferred while downloading
        if not prompt:
            prompt = st.session_state.get(SS_PENDING_PROMPT)
            if prompt:
                st.session_state[SS_PENDING_PROMPT] = None

        if prompt:
            from portal import fetcher as _fetcher
            unavailable = [d for d in sel_docs if not d.available]
            if unavailable:
                base_url = st.session_state[SS_FETCH_URL]
                with st.spinner(f"Downloading {len(unavailable)} document(s)…"):
                    _fetcher.download_and_convert_tdocs(
                        [d.id for d in unavailable], base_url
                    )
                try:
                    st.session_state[SS_DOCS] = _fetcher.get_real_documents(base_url)
                except Exception:  # noqa: BLE001
                    pass
                st.session_state[SS_PENDING_PROMPT] = prompt
                st.rerun()
            else:
                _handle_chat_submit(prompt, sel_docs)


def _handle_chat_submit(prompt: str, sel_docs: list[TDoc]) -> None:
    from portal import rag

    messages: list[dict] = st.session_state[SS_CURRENT_MESSAGES]
    messages.append({"role": "user", "content": prompt})
    st.session_state[SS_LOADING] = True

    provider = st.session_state[SS_LLM_PROVIDER]
    model = st.session_state[SS_LLM_MODEL]
    prior_history = messages[:-1]  # exclude the just-appended user message

    with st.chat_message("assistant"):
        try:
            response_text = st.write_stream(
                rag.stream_response(
                    prompt=prompt,
                    docs=sel_docs,
                    history=prior_history,
                    provider=provider,
                    model=model,
                )
            )
        except Exception as exc:  # noqa: BLE001
            response_text = f"[Unexpected error: {exc}]"
            st.markdown(response_text)

    messages.append({"role": "assistant", "content": response_text})
    st.session_state[SS_LOADING] = False

    # Ensure session ID exists
    if not st.session_state[SS_ACTIVE_SESSION_ID]:
        st.session_state[SS_ACTIVE_SESSION_ID] = str(uuid.uuid4())

    _persist_session(messages, st.session_state[SS_SELECTED_DOC_IDS])
    st.rerun()


# ---------------------------------------------------------------------------
# Right column — Session history
# ---------------------------------------------------------------------------

def render_right_column(col: st.delta_generator.DeltaGenerator) -> None:
    with col:
        st.subheader("History")

        sessions: list[ChatSession] = st.session_state[SS_SESSIONS]

        if not sessions:
            st.caption("No sessions yet.")
        else:
            with st.container(height=580):
                for session in sessions:
                    is_active = session.session_id == st.session_state[SS_ACTIVE_SESSION_ID]
                    btn_type = "primary" if is_active else "secondary"
                    if st.button(
                        session.title,
                        key=f"hist_{session.session_id}",
                        use_container_width=True,
                        type=btn_type,
                    ):
                        st.session_state[SS_ACTIVE_SESSION_ID] = session.session_id
                        st.session_state[SS_CURRENT_MESSAGES] = list(session.messages)
                        st.session_state[SS_SELECTED_DOC_IDS] = set(session.doc_ids)
                        st.rerun()
                    doc_tags = " · ".join(f"`{d}`" for d in session.doc_ids)
                    st.caption(
                        f"{session.created_at:%b %d}  |  {len(session.messages) // 2} Q&A  |  {doc_tags}"
                    )

        st.divider()
        if st.button("Clear History", use_container_width=True):
            st.session_state[SS_SESSIONS] = []
            st.session_state[SS_ACTIVE_SESSION_ID] = None
            st.session_state[SS_CURRENT_MESSAGES] = []
            st.rerun()
