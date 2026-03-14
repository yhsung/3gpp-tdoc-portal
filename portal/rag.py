"""Multi-provider LLM streaming integration for TDoc RAG Q&A."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Generator

from portal.mock_data import TDoc

SYSTEM_PROMPT = """\
You are an expert assistant for 3GPP standardization work, specializing in
Radio Access Network (RAN) Working Group 1 (WG1) technical documents (TDocs).

You have been provided with the content of one or more TDoc contributions.
Answer questions accurately based solely on the provided document content.
When referencing specific sections or claims, cite the TDoc ID (e.g., R1-2508300).
If the answer is not found in the provided documents, say so clearly rather
than speculating. Use correct 3GPP technical terminology.
"""

MAX_CHARS_PER_DOC = 8000


def build_context(docs: list[TDoc]) -> str:
    """Build a text context block from selected TDoc documents."""
    parts = []
    for doc in docs:
        md_path = Path(doc.md_path)
        if doc.available and md_path.exists():
            try:
                content = md_path.read_text(encoding="utf-8")[:MAX_CHARS_PER_DOC]
            except OSError:
                content = doc.mock_content
        else:
            content = doc.mock_content
        parts.append(f"--- TDoc {doc.id}: {doc.title} ---\n{content}")
    return "\n\n".join(parts)


def _build_openai_messages(context: str, history: list[dict], prompt: str) -> list[dict]:
    """Build message list for OpenAI-compatible APIs (including DeepSeek)."""
    messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]
    if context:
        messages.append({"role": "user", "content": f"Here are the TDoc documents for this session:\n\n{context}"})
        messages.append({"role": "assistant", "content": "I have reviewed the provided TDoc documents and am ready to answer questions about them."})
    for msg in history:
        messages.append(msg)
    messages.append({"role": "user", "content": prompt})
    return messages


def stream_response(
    prompt: str,
    docs: list[TDoc],
    history: list[dict],
    provider: str,
    model: str,
    max_tokens: int = 2048,
) -> Generator[str, None, None]:
    """Unified streaming generator across LLM providers."""
    context = build_context(docs)

    if provider == "claude":
        yield from _stream_claude(prompt, context, history, model, max_tokens)
    elif provider == "deepseek":
        yield from _stream_openai_compatible(
            prompt=prompt,
            context=context,
            history=history,
            model=model,
            max_tokens=max_tokens,
            api_key=os.getenv("DEEPSEEK_API_KEY", ""),
            base_url="https://api.deepseek.com",
        )
    else:
        yield f"[Error] Unknown provider: {provider}"


def _stream_claude(
    prompt: str,
    context: str,
    history: list[dict],
    model: str,
    max_tokens: int,
) -> Generator[str, None, None]:
    try:
        import anthropic
    except ImportError:
        yield "[Error] anthropic package not installed. Run: pip install anthropic"
        return

    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        yield "[Error] ANTHROPIC_API_KEY not set in environment."
        return

    # Build message list (context injected as priming exchange)
    messages: list[dict] = []
    if context:
        messages.append({"role": "user", "content": f"Here are the TDoc documents for this session:\n\n{context}"})
        messages.append({"role": "assistant", "content": "I have reviewed the provided TDoc documents and am ready to answer questions about them."})
    for msg in history:
        messages.append(msg)
    messages.append({"role": "user", "content": prompt})

    try:
        client = anthropic.Anthropic(api_key=api_key)
        with client.messages.stream(
            model=model,
            max_tokens=max_tokens,
            system=SYSTEM_PROMPT,
            messages=messages,
        ) as stream:
            for text in stream.text_stream:
                yield text
    except Exception as exc:  # noqa: BLE001
        yield f"\n\n[Error from Claude API: {exc}]"


def _stream_openai_compatible(
    prompt: str,
    context: str,
    history: list[dict],
    model: str,
    max_tokens: int,
    api_key: str,
    base_url: str,
) -> Generator[str, None, None]:
    try:
        from openai import OpenAI
    except ImportError:
        yield "[Error] openai package not installed. Run: pip install openai"
        return

    if not api_key:
        yield f"[Error] API key not set. Please add the key for {base_url} to your .env file."
        return

    messages = _build_openai_messages(context, history, prompt)

    try:
        client = OpenAI(api_key=api_key, base_url=base_url)
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content
    except Exception as exc:  # noqa: BLE001
        yield f"\n\n[Error from API ({base_url}): {exc}]"
