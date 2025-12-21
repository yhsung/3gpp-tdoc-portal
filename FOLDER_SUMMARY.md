# 3GPP TDoc Portal - Folder Summary

## Project Overview
A comprehensive system for downloading, extracting, and converting 3GPP TDoc files from RAN1 meeting documents, with plans for a full-stack web application interface.

## Repository Structure

```
3gpp-tdoc-portal/
├── download_tdocs.py          # Main script for download/extract/convert pipeline
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
├── FOLDER_SUMMARY.md         # This file - comprehensive folder overview
├── specs/                     # Specification documents
│   └── web-app-implementation-plan.md  # Web application design plan
├── tdocs/                     # Downloaded TDoc ZIP files (git-ignored)
├── extracted/                 # Extracted document contents (git-ignored)
└── output/                    # Converted files (git-ignored)
    ├── html/                  # HTML converted documents
    └── markdown/              # Markdown converted documents
```

## Core Files

### `download_tdocs.py`
**Purpose:** Main executable script for the TDoc processing pipeline

**Key Features:**
- Multi-processing with 4 parallel workers using ProcessPoolExecutor
- Three-phase processing: Download → Extract → Convert
- Smart skip logic for already processed files
- Progress tracking with tqdm progress bars
- Support for PDF, DOCX, DOC, PPTX, PPT, XLSX, XLS formats

**Functions:**
- `create_directories()` - Initialize directory structure
- `fetch_document_list(url)` - Scrape 3GPP website for TDoc files
- `download_file_worker(filename)` - Download single TDoc ZIP file
- `extract_file_worker(filename)` - Extract ZIP archive
- `convert_document_worker(doc_info)` - Convert document to HTML/Markdown using docling
- `main()` - Orchestrate the full pipeline

**Configuration:**
- `BASE_URL` - 3GPP RAN1 documents directory
- `MAX_WORKERS` - Parallel processing workers (default: 4)
- `DOWNLOAD_DIR` - TDoc ZIP storage (default: "tdocs")
- `EXTRACT_DIR` - Extracted files location (default: "extracted")
- `OUTPUT_DIR` - Converted files location (default: "output")

### `requirements.txt`
**Dependencies:**
- `requests>=2.31.0` - HTTP library for downloads
- `beautifulsoup4>=4.12.0` - HTML parsing for web scraping
- `docling>=1.0.0` - Document conversion library
- `tqdm>=4.66.0` - Progress bars

### `README.md`
Comprehensive project documentation including:
- Installation instructions
- Usage guide
- Feature list
- Directory structure explanation
- Output file naming conventions

## Specifications

### `specs/web-app-implementation-plan.md`
**Purpose:** Complete technical specification for the web application

**Planned Tech Stack:**
- Backend: FastAPI (async, WebSocket support)
- Frontend: Vue.js 3 with Vite
- Database: SQLite with SQLAlchemy ORM
- Task Processing: FastAPI Background Tasks
- Deployment: Docker Compose

**Key Components:**
- REST API endpoints for document management
- WebSocket for real-time progress updates
- Document viewer for HTML files
- Task monitoring dashboard
- Search and filtering capabilities

**Database Schema:**
- `tdoc_files` - Master table for ZIP files
- `documents` - Individual documents within TDocs
- `processing_tasks` - Task execution tracking
- `task_logs` - Detailed task logs

## Data Directories (Git-Ignored)

### `tdocs/`
Contains downloaded TDoc ZIP files from 3GPP server.
- Files follow pattern: `R1-XXXXXXX.zip`
- Currently ~630+ files available
- Automatically skipped if already downloaded

### `extracted/`
Contains extracted contents of TDoc ZIP files.
- Organized by TDoc ID: `extracted/R1-XXXXXXX/`
- Preserves original directory structure
- May contain multiple document formats

### `output/`
Contains converted documents in two formats:

**`output/html/`**
- HTML versions with preserved layout
- Naming pattern: `{TDoc-ID}_{filename}.html`
- Example: `R1-2508300_proposal.html`

**`output/markdown/`**
- Markdown versions for text processing
- Naming pattern: `{TDoc-ID}_{filename}.md`
- Example: `R1-2508300_proposal.md`

## Development Workflow

### Current State
The project currently operates as a standalone Python script with:
- Complete download/extract/convert pipeline
- Multi-processing for performance
- Resume capability (skips processed files)
- Comprehensive error handling

### Future Development
Planned web application will add:
- Web-based UI for document browsing
- Real-time task monitoring
- Document search and filtering
- In-browser HTML document viewing
- RESTful API for programmatic access

## Usage

### Running the Script
```bash
# Install dependencies
pip install -r requirements.txt

# Run the complete pipeline
python download_tdocs.py
```

The script will:
1. Fetch list of TDoc files from 3GPP server
2. Download all ZIP files in parallel (4 workers)
3. Extract all downloaded files in parallel
4. Convert all documents to HTML and Markdown in parallel

### Output
- Download statistics (downloaded, skipped, failed)
- Extraction statistics (extracted, skipped)
- Conversion statistics (converted, skipped)
- Full paths to output directories

## Key Features

### Multi-Processing
- Parallel downloads using 4 worker processes
- Parallel extraction using 4 worker processes
- Parallel conversion using 4 worker processes
- Significantly faster than sequential processing

### Smart Skip Logic
- Downloads: Skip if file exists in `tdocs/`
- Extraction: Skip if directory exists in `extracted/` and is non-empty
- Conversion: Skip if both HTML and Markdown files exist in `output/`

### Error Handling
- Network errors during download are caught and logged
- Invalid ZIP files are handled gracefully
- Conversion errors don't stop the pipeline
- Failed downloads remove partial files

### Progress Tracking
- Real-time progress bars for each phase
- Status messages for each file (OK/SKIP/FAIL)
- Summary statistics at completion

## Source URLs
- 3GPP Documents: https://www.3gpp.org/ftp/meetings_3gpp_sync/RAN1/Docs/
- TDoc Pattern: `R1-XXXXXXX.zip` (7-digit number)

## Notes

- The script uses docling for high-quality document conversion
- Processing time varies based on document count and size
- Approximately 630+ TDoc files available as of December 2024
- Web scraping uses regex pattern to extract exact filenames
- All worker functions return structured result dictionaries for easy integration

## Future Enhancements

Based on the web application implementation plan:
1. Database integration for document metadata
2. RESTful API for document access
3. Real-time WebSocket updates for task progress
4. Vue.js frontend with document viewer
5. Docker containerization for easy deployment
6. Search and filtering capabilities
7. User authentication (optional)
8. Document versioning and history

## Git Configuration

### Ignored Files/Directories
The following are git-ignored to avoid committing large binary files:
- `tdocs/` - Downloaded ZIP files
- `extracted/` - Extracted document contents
- `output/` - Converted HTML and Markdown files
- `.vscode/` - Editor configuration
- `.claude/` - AI assistant workspace
- `__pycache__/` - Python bytecode
- `*.pyc` - Compiled Python files
- `.DS_Store` - macOS system files

Only source code, documentation, and configuration files are version-controlled.
