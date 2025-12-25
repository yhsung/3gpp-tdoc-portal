#!/usr/bin/env python3
# Copyright 2024 3GPP TDoc Portal Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
3GPP TDoc Downloader, Extractor, and Converter

Downloads all TDoc ZIP files from 3GPP RAN1 meeting documents directory,
extracts them, and converts documents to HTML and Markdown using docling.
"""

import os
import re
import sys
import zipfile
import requests
from pathlib import Path
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from docling.document_converter import DocumentConverter
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed


BASE_URL = "https://www.3gpp.org/ftp/meetings_3gpp_sync/RAN1/Docs/"
ARTIFACTS_DIR = "artifacts"
DOWNLOAD_DIR = "artifacts/tdocs"
EXTRACT_DIR = "artifacts/extracted"
OUTPUT_DIR = "artifacts/output"
CHUNK_SIZE = 8192  # 8KB chunks for download
MAX_WORKERS = 4  # Number of parallel workers

# Supported document formats for conversion
SUPPORTED_FORMATS = {'.pdf', '.docx', '.doc', '.pptx', '.ppt', '.xlsx', '.xls'}


def create_directories():
    """Create all necessary directories if they don't exist."""
    Path(DOWNLOAD_DIR).mkdir(parents=True, exist_ok=True)
    Path(EXTRACT_DIR).mkdir(parents=True, exist_ok=True)
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    Path(f"{OUTPUT_DIR}/html").mkdir(parents=True, exist_ok=True)
    Path(f"{OUTPUT_DIR}/markdown").mkdir(parents=True, exist_ok=True)
    print(f"Download directory: {os.path.abspath(DOWNLOAD_DIR)}")
    print(f"Extract directory:  {os.path.abspath(EXTRACT_DIR)}")
    print(f"Output directory:   {os.path.abspath(OUTPUT_DIR)}")


def fetch_document_list(url):
    """Fetch the directory listing page and extract all TDoc links."""
    print(f"Fetching document list from: {url}")

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching document list: {e}")
        sys.exit(1)

    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all links that match the TDoc pattern (R1-XXXXXXX.zip)
    tdoc_pattern = r"(R1-\d{7}\.zip)$"
    links = []

    for link in soup.find_all('a', href=True):
        href = link['href']
        match = re.search(tdoc_pattern, href)
        if match:
            # Extract just the filename from the matched pattern
            filename = match.group(1)
            links.append(filename)

    print(f"Found {len(links)} TDoc files")
    return links


def download_file_worker(filename):
    """Worker function to download a single file (for parallel processing)."""
    filepath = os.path.join(DOWNLOAD_DIR, filename)

    # Skip if file already exists
    if os.path.exists(filepath):
        return {'filename': filename, 'status': 'skip', 'message': 'Already exists'}

    try:
        url = urljoin(BASE_URL, filename)
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))

        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    f.write(chunk)

        size_mb = total_size / (1024 * 1024) if total_size > 0 else os.path.getsize(filepath) / (1024 * 1024)
        return {'filename': filename, 'status': 'success', 'message': f'{size_mb:.2f} MB'}

    except requests.RequestException as e:
        # Remove partial file if download failed
        if os.path.exists(filepath):
            os.remove(filepath)
        return {'filename': filename, 'status': 'fail', 'message': str(e)}


def extract_file_worker(filename):
    """Worker function to extract a single file (for parallel processing)."""
    filepath = os.path.join(DOWNLOAD_DIR, filename)
    tdoc_name = Path(filename).stem
    extract_path = os.path.join(EXTRACT_DIR, tdoc_name)

    # Skip if download doesn't exist
    if not os.path.exists(filepath):
        return {'filename': filename, 'status': 'skip', 'message': 'Not downloaded'}

    # Skip if already extracted
    if os.path.exists(extract_path) and os.listdir(extract_path):
        return {'filename': filename, 'status': 'skip', 'message': 'Already extracted'}

    try:
        Path(extract_path).mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(filepath, 'r') as zip_ref:
            zip_ref.extractall(extract_path)

        return {'filename': filename, 'status': 'success', 'message': 'Extracted'}

    except zipfile.BadZipFile:
        return {'filename': filename, 'status': 'fail', 'message': 'Invalid ZIP file'}
    except Exception as e:
        return {'filename': filename, 'status': 'fail', 'message': str(e)}


def convert_document_worker(doc_info):
    """Worker function to convert a single document (for parallel processing)."""
    doc_path, tdoc_name, doc_filename = doc_info

    base_name = Path(doc_filename).stem
    output_base = f"{tdoc_name}_{base_name}"

    html_path = os.path.join(OUTPUT_DIR, "html", f"{output_base}.html")
    md_path = os.path.join(OUTPUT_DIR, "markdown", f"{output_base}.md")

    # Skip if already converted
    if os.path.exists(html_path) and os.path.exists(md_path):
        return {'filename': doc_filename, 'status': 'skip', 'message': 'Already converted'}

    try:
        # Initialize converter
        converter = DocumentConverter()

        # Convert document
        result = converter.convert(doc_path)

        # Export to HTML
        if not os.path.exists(html_path):
            html_content = result.document.export_to_html()
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

        # Export to Markdown
        if not os.path.exists(md_path):
            md_content = result.document.export_to_markdown()
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(md_content)

        return {'filename': doc_filename, 'status': 'success', 'message': 'Converted'}

    except Exception as e:
        return {'filename': doc_filename, 'status': 'fail', 'message': str(e)}




def main():
    """Main function to orchestrate the download, extract, and conversion process."""
    print("=" * 70)
    print("3GPP TDoc Downloader, Extractor, and Converter")
    print("=" * 70)

    create_directories()

    # Fetch list of documents
    tdoc_files = fetch_document_list(BASE_URL)

    if not tdoc_files:
        print("No TDoc files found!")
        sys.exit(1)

    print(f"\nTotal files to process: {len(tdoc_files)}\n")

    download_success = 0
    download_skip = 0
    download_fail = 0
    extract_success = 0
    extract_skip = 0
    convert_success = 0
    convert_skip = 0

    # Phase 1: Download all files
    print("=" * 70)
    print("PHASE 1: DOWNLOADING FILES")
    print(f"Using {MAX_WORKERS} parallel workers")
    print("=" * 70)

    with tqdm(total=len(tdoc_files), desc="Download Progress", unit="file") as pbar:
        with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(download_file_worker, filename): filename
                      for filename in tdoc_files}

            for future in as_completed(futures):
                result = future.result()
                if result['status'] == 'success':
                    download_success += 1
                    pbar.write(f"[OK] {result['filename']} - {result['message']}")
                elif result['status'] == 'skip':
                    download_skip += 1
                    pbar.write(f"[SKIP] {result['filename']} - {result['message']}")
                else:
                    download_fail += 1
                    pbar.write(f"[FAIL] {result['filename']} - {result['message']}")

                pbar.update(1)

    # Phase 2: Extract all files
    print("\n" + "=" * 70)
    print("PHASE 2: EXTRACTING FILES")
    print(f"Using {MAX_WORKERS} parallel workers")
    print("=" * 70)

    with tqdm(total=len(tdoc_files), desc="Extract Progress", unit="file") as pbar:
        with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(extract_file_worker, filename): filename
                      for filename in tdoc_files}

            for future in as_completed(futures):
                result = future.result()
                if result['status'] == 'success':
                    extract_success += 1
                    pbar.write(f"[OK] {result['filename']} - {result['message']}")
                elif result['status'] == 'skip':
                    extract_skip += 1
                    pbar.write(f"[SKIP] {result['filename']} - {result['message']}")
                else:
                    pbar.write(f"[FAIL] {result['filename']} - {result['message']}")

                pbar.update(1)

    # Phase 3: Convert all files
    print("\n" + "=" * 70)
    print("PHASE 3: CONVERTING FILES")
    print(f"Using {MAX_WORKERS} parallel workers")
    print("=" * 70)

    # Collect all documents to convert
    all_documents = []
    for filename in tdoc_files:
        tdoc_name = Path(filename).stem
        extract_path = os.path.join(EXTRACT_DIR, tdoc_name)

        if not os.path.exists(extract_path):
            continue

        # Find all documents in the extracted folder
        for root, _, files in os.walk(extract_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = Path(file).suffix.lower()
                if file_ext in SUPPORTED_FORMATS:
                    all_documents.append((file_path, tdoc_name, file))

    print(f"Found {len(all_documents)} documents to convert\n")

    if all_documents:
        with tqdm(total=len(all_documents), desc="Convert Progress", unit="doc") as pbar:
            with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
                futures = {executor.submit(convert_document_worker, doc_info): doc_info
                          for doc_info in all_documents}

                for future in as_completed(futures):
                    result = future.result()
                    if result['status'] == 'success':
                        convert_success += 1
                        pbar.write(f"[OK] {result['filename']}")
                    elif result['status'] == 'skip':
                        convert_skip += 1
                        pbar.write(f"[SKIP] {result['filename']} - {result['message']}")
                    else:
                        pbar.write(f"[FAIL] {result['filename']} - {result['message']}")

                    pbar.update(1)

    # Summary
    print("\n" + "=" * 70)
    print("PROCESSING SUMMARY")
    print("=" * 70)
    print(f"Total TDoc files:        {len(tdoc_files)}")
    print(f"\nPhase 1 - Download:")
    print(f"  Downloaded:            {download_success}")
    print(f"  Skipped (exists):      {download_skip}")
    print(f"  Failed:                {download_fail}")
    print(f"\nPhase 2 - Extraction:")
    print(f"  Extracted:             {extract_success}")
    print(f"  Skipped (exists):      {extract_skip}")
    print(f"\nPhase 3 - Conversion:")
    print(f"  Total documents:       {len(all_documents)}")
    print(f"  Converted:             {convert_success}")
    print(f"  Skipped (exists):      {convert_skip}")
    print(f"\nOutput locations:")
    print(f"  Downloads:             {os.path.abspath(DOWNLOAD_DIR)}")
    print(f"  Extracted:             {os.path.abspath(EXTRACT_DIR)}")
    print(f"  HTML:                  {os.path.abspath(OUTPUT_DIR)}/html")
    print(f"  Markdown:              {os.path.abspath(OUTPUT_DIR)}/markdown")
    print("=" * 70)


if __name__ == "__main__":
    main()
