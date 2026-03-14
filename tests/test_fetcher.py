"""Tests for portal/fetcher.py."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests

# portal.fetcher imports streamlit; conftest.py injects the mock first.
from portal.fetcher import (
    fetch_tdoc_ids,
    get_real_documents,
    infer_meeting_from_url,
    scan_local_artifacts,
)


# ---------------------------------------------------------------------------
# infer_meeting_from_url
# ---------------------------------------------------------------------------

class TestInferMeetingFromUrl:
    def test_standard_meeting_number(self):
        url = "https://www.3gpp.org/ftp/tsg_ran/WG1_RL1/TSGR1_120/Docs/"
        assert infer_meeting_from_url(url) == "RAN1 #120"

    def test_bis_meeting(self):
        url = "https://www.3gpp.org/ftp/tsg_ran/WG1_RL1/TSGR1_119bis/Docs/"
        assert infer_meeting_from_url(url) == "RAN1 #119bis"

    def test_sync_url_without_meeting_returns_fallback(self):
        url = "https://www.3gpp.org/ftp/meetings_3gpp_sync/RAN1/Docs/"
        assert infer_meeting_from_url(url) == "RAN1"

    def test_empty_string_returns_fallback(self):
        assert infer_meeting_from_url("") == "RAN1"


# ---------------------------------------------------------------------------
# fetch_tdoc_ids
# ---------------------------------------------------------------------------

_HTML_WITH_TDOCS = """
<html><body>
  <a href="R1-2501001.zip">R1-2501001.zip</a>
  <a href="R1-2502034.zip">R1-2502034.zip</a>
  <a href="agenda.doc">agenda.doc</a>
  <a href="R1-2503218.zip">R1-2503218.zip</a>
</body></html>
"""

_HTML_NO_TDOCS = "<html><body><a href='readme.txt'>readme.txt</a></body></html>"


class TestFetchTdocIds:
    def _mock_response(self, html: str, status: int = 200) -> MagicMock:
        resp = MagicMock()
        resp.text = html
        resp.status_code = status
        resp.raise_for_status = MagicMock()
        if status >= 400:
            resp.raise_for_status.side_effect = requests.HTTPError(response=resp)
        return resp

    def test_parses_tdoc_ids_from_html(self):
        with patch("portal.fetcher.requests.get", return_value=self._mock_response(_HTML_WITH_TDOCS)):
            ids = fetch_tdoc_ids("https://example.com/Docs/")
        assert ids == ["R1-2501001", "R1-2502034", "R1-2503218"]

    def test_returns_empty_list_for_no_matching_links(self):
        with patch("portal.fetcher.requests.get", return_value=self._mock_response(_HTML_NO_TDOCS)):
            ids = fetch_tdoc_ids("https://example.com/Docs/")
        assert ids == []

    def test_raises_on_http_error(self):
        with patch("portal.fetcher.requests.get", return_value=self._mock_response("", status=404)):
            with pytest.raises(requests.HTTPError):
                fetch_tdoc_ids("https://example.com/Docs/")

    def test_raises_on_connection_error(self):
        with patch("portal.fetcher.requests.get", side_effect=requests.ConnectionError("unreachable")):
            with pytest.raises(requests.ConnectionError):
                fetch_tdoc_ids("https://example.com/Docs/")

    def test_ignores_non_zip_links_matching_id_pattern(self):
        html = '<a href="R1-2501001.docx">R1-2501001.docx</a>'
        with patch("portal.fetcher.requests.get", return_value=self._mock_response(html)):
            ids = fetch_tdoc_ids("https://example.com/")
        assert ids == []


# ---------------------------------------------------------------------------
# scan_local_artifacts
# ---------------------------------------------------------------------------

class TestScanLocalArtifacts:
    def test_returns_empty_dict_when_dir_missing(self, monkeypatch, tmp_path):
        nonexistent = tmp_path / "does_not_exist"
        monkeypatch.setattr("portal.fetcher.MD_DIR", nonexistent)
        assert scan_local_artifacts() == {}

    def test_finds_converted_document(self, monkeypatch, tmp_path):
        md_dir = tmp_path / "markdown"
        md_dir.mkdir()
        html_dir = tmp_path / "html"
        html_dir.mkdir()
        (md_dir / "R1-2501001_proposal.md").write_text("# content")
        (html_dir / "R1-2501001_proposal.html").write_text("<html/>")

        monkeypatch.setattr("portal.fetcher.MD_DIR", md_dir)
        monkeypatch.setattr("portal.fetcher.HTML_DIR", html_dir)

        result = scan_local_artifacts()
        assert "R1-2501001" in result
        assert result["R1-2501001"]["source_file"] == "proposal"
        assert result["R1-2501001"]["md_path"].endswith("R1-2501001_proposal.md")

    def test_ignores_files_without_tdoc_pattern(self, monkeypatch, tmp_path):
        md_dir = tmp_path / "markdown"
        md_dir.mkdir()
        (md_dir / "README.md").write_text("readme")
        (md_dir / "notes_extra.md").write_text("notes")

        monkeypatch.setattr("portal.fetcher.MD_DIR", md_dir)
        assert scan_local_artifacts() == {}

    def test_multiple_documents_for_different_tdocs(self, monkeypatch, tmp_path):
        md_dir = tmp_path / "markdown"
        md_dir.mkdir()
        (md_dir / "R1-2501001_doc_a.md").write_text("")
        (md_dir / "R1-2502034_doc_b.md").write_text("")

        monkeypatch.setattr("portal.fetcher.MD_DIR", md_dir)
        monkeypatch.setattr("portal.fetcher.HTML_DIR", tmp_path / "html")

        result = scan_local_artifacts()
        assert set(result.keys()) == {"R1-2501001", "R1-2502034"}

    def test_keeps_first_file_when_tdoc_has_multiple_outputs(self, monkeypatch, tmp_path):
        md_dir = tmp_path / "markdown"
        md_dir.mkdir()
        # Two output files for the same TDoc (e.g. from a multi-file ZIP)
        (md_dir / "R1-2501001_file1.md").write_text("")
        (md_dir / "R1-2501001_file2.md").write_text("")

        monkeypatch.setattr("portal.fetcher.MD_DIR", md_dir)
        monkeypatch.setattr("portal.fetcher.HTML_DIR", tmp_path / "html")

        result = scan_local_artifacts()
        assert len(result) == 1
        assert "R1-2501001" in result


# ---------------------------------------------------------------------------
# get_real_documents
# ---------------------------------------------------------------------------

class TestGetRealDocuments:
    def test_returns_tdoc_list_with_correct_ids(self, monkeypatch):
        monkeypatch.setattr("portal.fetcher._cached_fetch_tdoc_ids", lambda url: ["R1-2501001", "R1-2502034"])
        monkeypatch.setattr("portal.fetcher.scan_local_artifacts", lambda: {})

        docs = get_real_documents("https://example.com/Docs/")
        assert len(docs) == 2
        assert docs[0].id == "R1-2501001"
        assert docs[1].id == "R1-2502034"

    def test_available_false_when_no_local_artifacts(self, monkeypatch):
        monkeypatch.setattr("portal.fetcher._cached_fetch_tdoc_ids", lambda url: ["R1-2501001"])
        monkeypatch.setattr("portal.fetcher.scan_local_artifacts", lambda: {})

        docs = get_real_documents("https://example.com/Docs/")
        assert docs[0].available is False

    def test_available_true_when_local_artifact_exists(self, monkeypatch, tmp_path):
        md_file = tmp_path / "R1-2501001_proposal.md"
        md_file.write_text("# content")
        artifact = {
            "R1-2501001": {
                "md_path": str(md_file),
                "html_path": str(tmp_path / "R1-2501001_proposal.html"),
                "source_file": "proposal",
            }
        }
        monkeypatch.setattr("portal.fetcher._cached_fetch_tdoc_ids", lambda url: ["R1-2501001"])
        monkeypatch.setattr("portal.fetcher.scan_local_artifacts", lambda: artifact)

        docs = get_real_documents("https://example.com/TSGR1_120/Docs/")
        assert docs[0].available is True
        assert docs[0].source_file == "proposal"

    def test_meeting_inferred_from_url(self, monkeypatch):
        monkeypatch.setattr("portal.fetcher._cached_fetch_tdoc_ids", lambda url: ["R1-2501001"])
        monkeypatch.setattr("portal.fetcher.scan_local_artifacts", lambda: {})

        docs = get_real_documents("https://www.3gpp.org/ftp/tsg_ran/WG1_RL1/TSGR1_120/Docs/")
        assert docs[0].meeting == "RAN1 #120"

    def test_returns_empty_list_when_no_tdocs_found(self, monkeypatch):
        monkeypatch.setattr("portal.fetcher._cached_fetch_tdoc_ids", lambda url: [])
        monkeypatch.setattr("portal.fetcher.scan_local_artifacts", lambda: {})

        docs = get_real_documents("https://example.com/Docs/")
        assert docs == []


# ---------------------------------------------------------------------------
# download_and_convert_tdocs
# ---------------------------------------------------------------------------

class TestDownloadAndConvertTdocs:
    def _make_worker_result(self, status: str, message: str = "") -> dict:
        return {"status": status, "message": message}

    def test_reports_download_failure(self, monkeypatch, tmp_path):
        monkeypatch.setattr("portal.fetcher.DOWNLOAD_DIR", tmp_path / "tdocs")
        monkeypatch.setattr("portal.fetcher.EXTRACT_DIR", tmp_path / "extracted")
        monkeypatch.setattr("portal.fetcher.MD_DIR", tmp_path / "markdown")
        monkeypatch.setattr("portal.fetcher.HTML_DIR", tmp_path / "html")
        monkeypatch.setattr("portal.fetcher.ARTIFACTS_DIR", tmp_path)

        import download_tdocs as _dt
        monkeypatch.setattr(_dt, "DOWNLOAD_DIR", str(tmp_path / "tdocs"))
        monkeypatch.setattr(_dt, "EXTRACT_DIR", str(tmp_path / "extracted"))
        monkeypatch.setattr(_dt, "OUTPUT_DIR", str(tmp_path / "output"))

        with patch("download_tdocs.download_file_worker", return_value=self._make_worker_result("fail", "Connection refused")):
            from portal.fetcher import download_and_convert_tdocs
            results = download_and_convert_tdocs(["R1-2501001"], "https://example.com/Docs/")

        assert "download failed" in results["R1-2501001"]

    def test_reports_converted_on_success(self, monkeypatch, tmp_path):
        # Set up a fake extracted folder with a supported file
        extract_dir = tmp_path / "extracted"
        tdoc_folder = extract_dir / "R1-2501001"
        tdoc_folder.mkdir(parents=True)
        (tdoc_folder / "proposal.docx").write_bytes(b"fake docx")

        monkeypatch.setattr("portal.fetcher.DOWNLOAD_DIR", tmp_path / "tdocs")
        monkeypatch.setattr("portal.fetcher.EXTRACT_DIR", extract_dir)
        monkeypatch.setattr("portal.fetcher.MD_DIR", tmp_path / "markdown")
        monkeypatch.setattr("portal.fetcher.HTML_DIR", tmp_path / "html")
        monkeypatch.setattr("portal.fetcher.ARTIFACTS_DIR", tmp_path)

        import download_tdocs as _dt
        monkeypatch.setattr(_dt, "DOWNLOAD_DIR", str(tmp_path / "tdocs"))
        monkeypatch.setattr(_dt, "EXTRACT_DIR", str(extract_dir))
        monkeypatch.setattr(_dt, "OUTPUT_DIR", str(tmp_path / "output"))

        with patch("download_tdocs.download_file_worker", return_value=self._make_worker_result("success")), \
             patch("download_tdocs.extract_file_worker", return_value=self._make_worker_result("success")), \
             patch("download_tdocs.convert_document_worker", return_value=self._make_worker_result("success")):
            from portal.fetcher import download_and_convert_tdocs
            results = download_and_convert_tdocs(["R1-2501001"], "https://example.com/Docs/")

        assert results["R1-2501001"] == "converted"
