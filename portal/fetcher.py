"""Real 3GPP TDoc fetching, local artifact scanning, and download integration."""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import requests
import streamlit as st
from bs4 import BeautifulSoup

if TYPE_CHECKING:
    from portal.mock_data import TDoc

PROJECT_ROOT = Path(__file__).parent.parent
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
DOWNLOAD_DIR = ARTIFACTS_DIR / "tdocs"
EXTRACT_DIR = ARTIFACTS_DIR / "extracted"
MD_DIR = ARTIFACTS_DIR / "output" / "markdown"
HTML_DIR = ARTIFACTS_DIR / "output" / "html"

TDOC_PATTERN = re.compile(r"(R\d-\d{7})\.zip", re.IGNORECASE)
MEETING_PATTERN = re.compile(r"TSGR1_(\d+[a-z]*)", re.IGNORECASE)


def infer_meeting_from_url(url: str) -> str:
    """Parse meeting name from a 3GPP FTP URL.

    Examples:
        .../TSGR1_120/Docs/ → "RAN1 #120"
        .../TSGR1_119bis/Docs/ → "RAN1 #119bis"
    """
    match = MEETING_PATTERN.search(url)
    if match:
        return f"RAN1 #{match.group(1)}"
    return "RAN1"


def fetch_tdoc_ids(url: str, timeout: int = 30) -> list[str]:
    """Scrape a 3GPP FTP directory listing and return TDoc IDs (e.g. 'R1-2501001')."""
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    ids: list[str] = []
    for link in soup.find_all("a", href=True):
        match = TDOC_PATTERN.search(link["href"])
        if match:
            ids.append(match.group(1))
    return ids


def scan_local_artifacts() -> dict[str, dict]:
    """Return a mapping of TDoc ID → artifact info for locally converted documents.

    Scans artifacts/output/markdown/ for files named ``R?-XXXXXXX_*.md``.
    """
    result: dict[str, dict] = {}
    if not MD_DIR.exists():
        return result
    for md_file in MD_DIR.glob("*.md"):
        # Expected pattern: R1-XXXXXXX_sourcefile.md
        stem = md_file.stem
        sep = stem.find("_")
        if sep < 0:
            continue
        tdoc_id = stem[:sep]
        if not re.match(r"R\d-\d{7}$", tdoc_id):
            continue
        source_file = stem[sep + 1:]
        html_file = HTML_DIR / f"{stem}.html"
        # A TDoc may have multiple output files; keep the first one found.
        if tdoc_id not in result:
            result[tdoc_id] = {
                "md_path": str(md_file),
                "html_path": str(html_file),
                "source_file": source_file,
            }
    return result


@st.cache_data(ttl=3600, show_spinner=False)
def _cached_fetch_tdoc_ids(url: str) -> list[str]:
    return fetch_tdoc_ids(url)


def get_real_documents(url: str) -> list["TDoc"]:
    """Fetch real TDoc list from a 3GPP FTP URL and return TDoc objects.

    Documents that have been locally downloaded and converted are marked
    ``available=True`` with correct ``md_path``/``html_path``/``source_file``.
    Others are stub entries with just the ID and placeholder metadata.
    """
    from portal.mock_data import TDoc  # local import to avoid circular dependency

    tdoc_ids = _cached_fetch_tdoc_ids(url)
    meeting = infer_meeting_from_url(url)
    local = scan_local_artifacts()

    docs: list[TDoc] = []
    for tdoc_id in tdoc_ids:
        artifact = local.get(tdoc_id)
        if artifact:
            doc = TDoc(
                id=tdoc_id,
                title=tdoc_id,
                source_file=artifact["source_file"],
                file_type="docx",
                meeting=meeting,
                agenda_item="—",
                available=True,
                html_path=artifact["html_path"],
                md_path=artifact["md_path"],
            )
        else:
            doc = TDoc(
                id=tdoc_id,
                title=tdoc_id,
                source_file=tdoc_id,
                file_type="zip",
                meeting=meeting,
                agenda_item="—",
            )
        docs.append(doc)
    return docs


def _ensure_artifact_dirs() -> None:
    for d in (DOWNLOAD_DIR, EXTRACT_DIR, MD_DIR, HTML_DIR):
        d.mkdir(parents=True, exist_ok=True)


def download_and_convert_tdocs(tdoc_ids: list[str], base_url: str) -> dict[str, str]:
    """Download, extract, and convert the given TDoc IDs.

    Reuses the worker functions from ``download_tdocs`` (no subprocess needed).
    Returns a dict of ``{tdoc_id: status}`` where status is one of
    "downloaded", "extracted", "converted", "skipped", or an error message.
    """
    # Import worker functions from the top-level download script.
    sys.path.insert(0, str(PROJECT_ROOT))
    from download_tdocs import (  # type: ignore[import]
        convert_document_worker,
        download_file_worker,
        extract_file_worker,
    )

    _ensure_artifact_dirs()

    # Temporarily patch the module-level constants used by the workers.
    import download_tdocs as _dt
    _dt.DOWNLOAD_DIR = str(DOWNLOAD_DIR)
    _dt.EXTRACT_DIR = str(EXTRACT_DIR)
    _dt.OUTPUT_DIR = str(ARTIFACTS_DIR / "output")

    results: dict[str, str] = {}

    for tdoc_id in tdoc_ids:
        filename = f"{tdoc_id}.zip"

        # Phase 1 – download
        dl = download_file_worker(filename)
        if dl["status"] == "fail":
            results[tdoc_id] = f"download failed: {dl['message']}"
            continue

        # Phase 2 – extract
        ex = extract_file_worker(filename)
        if ex["status"] == "fail":
            results[tdoc_id] = f"extract failed: {ex['message']}"
            continue

        # Phase 3 – convert all documents inside the extracted folder
        extract_path = EXTRACT_DIR / tdoc_id
        if not extract_path.exists():
            results[tdoc_id] = "extract path missing"
            continue

        converted_any = False
        supported = {".pdf", ".docx", ".doc", ".pptx", ".ppt", ".xlsx", ".xls"}
        for root, _, files in (extract_path).walk() if hasattr(extract_path, "walk") else _walk(extract_path):
            for file in files:
                if Path(file).suffix.lower() in supported:
                    file_path = root / file if isinstance(root, Path) else Path(root) / file
                    cv = convert_document_worker((str(file_path), tdoc_id, file))
                    if cv["status"] in ("success", "skip"):
                        converted_any = True

        results[tdoc_id] = "converted" if converted_any else "no supported files found"

    # Bust the fetch cache so get_real_documents re-reads local artifacts.
    _cached_fetch_tdoc_ids.clear()

    return results


def _walk(path: Path):
    """Fallback os.walk wrapper that yields (Path, dirs, files) tuples."""
    import os
    for root, dirs, files in os.walk(path):
        yield Path(root), dirs, files
