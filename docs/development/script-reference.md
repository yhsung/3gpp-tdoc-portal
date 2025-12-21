# Script Reference

[← Back to Development](../README.md#-development)

## Overview

Complete API reference for `download_tdocs.py` - the main script for downloading, extracting, and converting 3GPP TDoc files.

## Script Architecture

```
download_tdocs.py
├── Configuration Constants
├── Utility Functions
│   ├── create_directories()
│   └── fetch_document_list()
├── Worker Functions (Parallel Processing)
│   ├── download_file_worker()
│   ├── extract_file_worker()
│   └── convert_document_worker()
└── Main Pipeline
    └── main()
```

## Configuration Constants

### `BASE_URL`
**Type:** `str`
**Default:** `"https://www.3gpp.org/ftp/meetings_3gpp_sync/RAN1/Docs/"`
**Purpose:** Base URL for 3GPP RAN1 document directory

### `MAX_WORKERS`
**Type:** `int`
**Default:** `4`
**Purpose:** Number of parallel worker processes
**Tuning:** Adjust based on CPU cores and network bandwidth

### `ARTIFACTS_DIR`
**Type:** `str`
**Default:** `"artifacts"`
**Purpose:** Base directory for all generated files

### `DOWNLOAD_DIR`
**Type:** `str`
**Default:** `"artifacts/tdocs"`
**Purpose:** Storage location for downloaded ZIP files

### `EXTRACT_DIR`
**Type:** `str`
**Default:** `"artifacts/extracted"`
**Purpose:** Storage location for extracted document contents

### `OUTPUT_DIR`
**Type:** `str`
**Default:** `"artifacts/output"`
**Purpose:** Storage location for converted HTML and Markdown files

## Functions

### `create_directories()`

**Purpose:** Initialize required directory structure

**Signature:**
```python
def create_directories() -> None
```

**Behavior:**
- Creates `DOWNLOAD_DIR` if not exists
- Creates `EXTRACT_DIR` if not exists
- Creates `OUTPUT_DIR/html` if not exists
- Creates `OUTPUT_DIR/markdown` if not exists
- Uses `os.makedirs(exist_ok=True)` - safe to call multiple times

**Example:**
```python
create_directories()
# Creates:
# artifacts/tdocs/
# artifacts/extracted/
# artifacts/output/html/
# artifacts/output/markdown/
```

---

### `fetch_document_list(url)`

**Purpose:** Scrape 3GPP website to retrieve list of TDoc ZIP files

**Signature:**
```python
def fetch_document_list(url: str) -> List[str]
```

**Parameters:**
- `url` (str): URL of 3GPP directory page to scrape

**Returns:**
- `List[str]`: List of TDoc filenames matching pattern `R1-XXXXXXX.zip`

**Behavior:**
1. Sends GET request to URL
2. Parses HTML with BeautifulSoup
3. Extracts all `<a>` tags
4. Filters links using regex pattern `r"(R1-\d{7}\.zip)$"`
5. Returns list of matching filenames

**Error Handling:**
- Raises `requests.RequestException` on network errors
- Raises `Exception` on HTTP errors (status code != 200)

**Example:**
```python
tdoc_files = fetch_document_list(BASE_URL)
# Returns: ['R1-2508300.zip', 'R1-2508301.zip', ...]
```

---

### `download_file_worker(filename)`

**Purpose:** Worker function to download a single TDoc ZIP file (for parallel processing)

**Signature:**
```python
def download_file_worker(filename: str) -> Dict[str, str]
```

**Parameters:**
- `filename` (str): Name of the file to download (e.g., `R1-2508300.zip`)

**Returns:**
- `Dict[str, str]` with keys:
  - `filename` (str): The filename that was processed
  - `status` (str): One of `'success'`, `'skip'`, `'fail'`
  - `message` (str): Status message (file size, error message, or skip reason)

**Behavior:**
1. Check if file already exists in `DOWNLOAD_DIR`
2. If exists: Return skip status
3. If not exists:
   - Download file from `BASE_URL + filename`
   - Save to `DOWNLOAD_DIR/filename`
   - Return success with file size
4. On error:
   - Remove partial file if exists
   - Return fail status with error message

**Skip Logic:**
```python
if os.path.exists(filepath):
    return {'filename': filename, 'status': 'skip', 'message': 'Already exists'}
```

**Example:**
```python
result = download_file_worker('R1-2508300.zip')
# Success: {'filename': 'R1-2508300.zip', 'status': 'success', 'message': '2.45 MB'}
# Skip: {'filename': 'R1-2508300.zip', 'status': 'skip', 'message': 'Already exists'}
# Fail: {'filename': 'R1-2508300.zip', 'status': 'fail', 'message': 'Connection timeout'}
```

---

### `extract_file_worker(filename)`

**Purpose:** Worker function to extract a single TDoc ZIP file (for parallel processing)

**Signature:**
```python
def extract_file_worker(filename: str) -> Dict[str, str]
```

**Parameters:**
- `filename` (str): Name of the ZIP file to extract

**Returns:**
- `Dict[str, str]` with keys:
  - `filename` (str): The filename that was processed
  - `status` (str): One of `'success'`, `'skip'`, `'fail'`
  - `message` (str): Status message (file count or error message)

**Behavior:**
1. Determine extraction path: `EXTRACT_DIR/{tdoc_id}/`
2. Check if directory exists and contains files
3. If already extracted: Return skip status
4. If not extracted:
   - Extract ZIP to extraction path
   - Count extracted files
   - Return success with file count
5. On error: Return fail status with error message

**Skip Logic:**
```python
if os.path.exists(extract_path) and os.listdir(extract_path):
    return {'filename': filename, 'status': 'skip', 'message': 'Already extracted'}
```

**Example:**
```python
result = extract_file_worker('R1-2508300.zip')
# Success: {'filename': 'R1-2508300.zip', 'status': 'success', 'message': 'Extracted 3 files'}
# Skip: {'filename': 'R1-2508300.zip', 'status': 'skip', 'message': 'Already extracted'}
```

---

### `convert_document_worker(doc_info)`

**Purpose:** Worker function to convert a single document to HTML and Markdown (for parallel processing)

**Signature:**
```python
def convert_document_worker(doc_info: Tuple[str, str, str]) -> Dict[str, str]
```

**Parameters:**
- `doc_info` (Tuple[str, str, str]): Tuple containing:
  - `tdoc_id` (str): TDoc identifier (e.g., `R1-2508300`)
  - `doc_filename` (str): Document filename (e.g., `proposal.docx`)
  - `doc_path` (str): Full path to document file

**Returns:**
- `Dict[str, str]` with keys:
  - `filename` (str): The document filename
  - `status` (str): One of `'success'`, `'skip'`, `'fail'`
  - `message` (str): Status message

**Behavior:**
1. Generate output filenames: `{tdoc_id}_{base_name}.{html|md}`
2. Check if both HTML and Markdown files exist
3. If both exist: Return skip status
4. If not:
   - Load document with docling
   - Export to HTML and Markdown
   - Save to output directories
   - Return success
5. On error: Return fail status with error message

**Skip Logic:**
```python
if os.path.exists(html_output_path) and os.path.exists(md_output_path):
    return {'filename': doc_filename, 'status': 'skip', 'message': 'Already converted'}
```

**Supported File Types:**
- PDF: `.pdf`
- Word: `.docx`, `.doc`
- PowerPoint: `.pptx`, `.ppt`
- Excel: `.xlsx`, `.xls`

**Example:**
```python
doc_info = ('R1-2508300', 'proposal.docx', '/path/to/proposal.docx')
result = convert_document_worker(doc_info)
# Success: {'filename': 'proposal.docx', 'status': 'success', 'message': 'Converted successfully'}
# Skip: {'filename': 'proposal.docx', 'status': 'skip', 'message': 'Already converted'}
```

---

### `main()`

**Purpose:** Orchestrate the complete three-phase pipeline

**Signature:**
```python
def main() -> None
```

**Behavior:**

**Phase 1: Download**
1. Fetch list of TDoc files from 3GPP server
2. Create ProcessPoolExecutor with `MAX_WORKERS` workers
3. Submit download tasks for all files
4. Track progress with tqdm progress bar
5. Collect statistics: success, skip, fail counts
6. Display summary

**Phase 2: Extract**
1. Find all downloaded ZIP files in `DOWNLOAD_DIR`
2. Create ProcessPoolExecutor with `MAX_WORKERS` workers
3. Submit extraction tasks for all files
4. Track progress with tqdm progress bar
5. Collect statistics: success, skip counts
6. Display summary

**Phase 3: Convert**
1. Scan all extracted directories for documents
2. Filter for supported file types (PDF, DOCX, PPTX, XLSX, etc.)
3. Create ProcessPoolExecutor with `MAX_WORKERS` workers
4. Submit conversion tasks for all documents
5. Track progress with tqdm progress bar
6. Collect statistics: success, skip, fail counts
7. Display summary

**Progress Display:**
```
Download Progress: 100%|██████████| 630/630 [05:23<00:00, 1.95file/s]
[OK] R1-2508300.zip - 2.45 MB
[SKIP] R1-2508301.zip - Already exists
[FAIL] R1-2508302.zip - Connection timeout
```

**Example Execution:**
```python
if __name__ == "__main__":
    main()
```

## Multi-Processing Details

### ProcessPoolExecutor

The script uses `concurrent.futures.ProcessPoolExecutor` for parallel processing:

```python
from concurrent.futures import ProcessPoolExecutor, as_completed

with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = {executor.submit(worker_func, item): item for item in items}

    for future in as_completed(futures):
        result = future.result()
        # Process result
```

### Worker Return Format

All worker functions return structured dictionaries:

```python
{
    'filename': str,   # File that was processed
    'status': str,     # 'success', 'skip', or 'fail'
    'message': str     # Human-readable status message
}
```

### Performance Tuning

**CPU-Bound Tasks:**
- Document conversion is CPU-intensive
- Recommended: `MAX_WORKERS = CPU_COUNT`

**Network-Bound Tasks:**
- Downloads are network-intensive
- Can increase `MAX_WORKERS` beyond CPU count
- Respect 3GPP server rate limits

**Example Tuning:**
```python
import os

# Set based on CPU cores
MAX_WORKERS = os.cpu_count()  # e.g., 8 for 8-core CPU

# Or set manually
MAX_WORKERS = 8
```

## Error Handling

All phases handle errors gracefully:
- Failed downloads remove partial files
- Failed extractions log error and continue
- Failed conversions log error and continue
- Progress continues even with failures
- Final summary shows success/fail counts

## File Naming Conventions

**Downloaded Files:**
- Pattern: `R1-XXXXXXX.zip`
- Location: `artifacts/tdocs/`

**Extracted Directories:**
- Pattern: `artifacts/extracted/R1-XXXXXXX/`
- Contents: Original ZIP structure preserved

**Converted Files:**
- Pattern: `{TDoc-ID}_{filename}.{html|md}`
- Example: `R1-2508300_proposal.html`, `R1-2508300_proposal.md`
- Location: `artifacts/output/html/` and `artifacts/output/markdown/`

---

**Navigation:**
- [← Getting Started](getting-started.md)
- [Documentation Home](../README.md)
- [→ Next: Configuration](configuration.md)

**Related:**
- [Multi-Processing Feature](../features/multi-processing.md)
- [Skip Logic Feature](../features/skip-logic.md)
- [Running Pipeline](../usage/running-pipeline.md)
