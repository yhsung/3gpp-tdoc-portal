"""Tests for portal/mock_data.py."""
from __future__ import annotations

from pathlib import Path

import pytest

from portal.mock_data import ChatSession, TDoc, get_mock_documents, get_mock_sessions


class TestTDocDataclass:
    def test_mock_content_defaults_to_empty_string(self):
        doc = TDoc(
            id="R1-9990001",
            title="Test Doc",
            source_file="test_doc",
            file_type="docx",
            meeting="RAN1 #99",
            agenda_item="1.1",
        )
        assert doc.mock_content == ""

    def test_available_false_when_md_file_missing(self, tmp_path, monkeypatch):
        monkeypatch.setattr("portal.mock_data.MD_DIR", tmp_path / "markdown")
        monkeypatch.setattr("portal.mock_data.HTML_DIR", tmp_path / "html")

        doc = TDoc(
            id="R1-9990001",
            title="Test Doc",
            source_file="test_doc",
            file_type="docx",
            meeting="RAN1 #99",
            agenda_item="1.1",
        )
        assert doc.available is False

    def test_available_true_when_md_file_exists(self, tmp_path, monkeypatch):
        md_dir = tmp_path / "markdown"
        md_dir.mkdir()
        (md_dir / "R1-9990001_test_doc.md").write_text("# content")

        monkeypatch.setattr("portal.mock_data.MD_DIR", md_dir)
        monkeypatch.setattr("portal.mock_data.HTML_DIR", tmp_path / "html")

        doc = TDoc(
            id="R1-9990001",
            title="Test Doc",
            source_file="test_doc",
            file_type="docx",
            meeting="RAN1 #99",
            agenda_item="1.1",
        )
        assert doc.available is True

    def test_html_path_auto_generated(self):
        doc = TDoc(
            id="R1-9990001",
            title="Test Doc",
            source_file="test_doc",
            file_type="docx",
            meeting="RAN1 #99",
            agenda_item="1.1",
        )
        assert doc.html_path.endswith("R1-9990001_test_doc.html")

    def test_md_path_auto_generated(self):
        doc = TDoc(
            id="R1-9990001",
            title="Test Doc",
            source_file="test_doc",
            file_type="docx",
            meeting="RAN1 #99",
            agenda_item="1.1",
        )
        assert doc.md_path.endswith("R1-9990001_test_doc.md")

    def test_explicit_html_path_not_overridden(self):
        doc = TDoc(
            id="R1-9990001",
            title="Test Doc",
            source_file="test_doc",
            file_type="docx",
            meeting="RAN1 #99",
            agenda_item="1.1",
            html_path="/custom/path.html",
        )
        assert doc.html_path == "/custom/path.html"


class TestGetMockDocuments:
    def test_returns_non_empty_list(self):
        docs = get_mock_documents()
        assert len(docs) > 0

    def test_all_items_are_tdoc_instances(self):
        docs = get_mock_documents()
        assert all(isinstance(d, TDoc) for d in docs)

    def test_ids_are_unique(self):
        docs = get_mock_documents()
        ids = [d.id for d in docs]
        assert len(ids) == len(set(ids))

    def test_all_docs_have_required_fields(self):
        for doc in get_mock_documents():
            assert doc.id
            assert doc.title
            assert doc.meeting
            assert doc.agenda_item


class TestGetMockSessions:
    def test_returns_list_of_chat_sessions(self):
        sessions = get_mock_sessions()
        assert all(isinstance(s, ChatSession) for s in sessions)

    def test_sessions_have_messages(self):
        sessions = get_mock_sessions()
        for session in sessions:
            assert len(session.messages) > 0

    def test_session_doc_ids_reference_known_docs(self):
        docs = get_mock_documents()
        doc_ids = {d.id for d in docs}
        for session in get_mock_sessions():
            for doc_id in session.doc_ids:
                assert doc_id in doc_ids
