# Future Enhancements

[← Back to Planning](../README.md#-planning)

## Overview

This document outlines planned enhancements and future development roadmap for the 3GPP TDoc Portal project. Features are organized by priority and implementation timeline.

## Short-Term Enhancements

### 1. Command-Line Arguments

**Priority:** High
**Effort:** Low
**Timeline:** 1-2 days

**Description:**
Add command-line interface for runtime configuration.

**Features:**
- Custom artifacts directory
- Custom MAX_WORKERS
- Selective phase execution
- Verbose/quiet modes

**Example Usage:**
```bash
# Custom artifacts location
python download_tdocs.py --artifacts-dir /data/tdocs

# Custom worker count
python download_tdocs.py --workers 8

# Run specific phase
python download_tdocs.py --phase download
python download_tdocs.py --phase extract
python download_tdocs.py --phase convert

# Verbose output
python download_tdocs.py --verbose

# Quiet mode (no progress bars)
python download_tdocs.py --quiet
```

**Implementation:**
```python
import argparse

parser = argparse.ArgumentParser(description='3GPP TDoc Portal')
parser.add_argument('--artifacts-dir', default='artifacts', help='Artifacts directory')
parser.add_argument('--workers', type=int, default=4, help='Number of parallel workers')
parser.add_argument('--phase', choices=['download', 'extract', 'convert', 'all'], default='all')
parser.add_argument('--verbose', action='store_true', help='Verbose output')
parser.add_argument('--quiet', action='store_true', help='Quiet mode')
args = parser.parse_args()
```

### 2. Configuration File Support

**Priority:** Medium
**Effort:** Low
**Timeline:** 1-2 days

**Description:**
External configuration file for persistent settings.

**Format (config.ini):**
```ini
[paths]
artifacts_dir = /data/3gpp-tdocs
download_dir = %(artifacts_dir)s/tdocs
extract_dir = %(artifacts_dir)s/extracted
output_dir = %(artifacts_dir)s/output

[processing]
max_workers = 8
timeout = 30

[source]
base_url = https://www.3gpp.org/ftp/meetings_3gpp_sync/RAN1/Docs/

[logging]
log_file = %(artifacts_dir)s/pipeline.log
log_level = INFO
```

**Implementation:**
```python
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

ARTIFACTS_DIR = config['paths']['artifacts_dir']
MAX_WORKERS = config.getint('processing', 'max_workers')
BASE_URL = config['source']['base_url']
```

### 3. File Logging

**Priority:** High
**Effort:** Low
**Timeline:** 1 day

**Description:**
Persistent logging to file for debugging and auditing.

**Features:**
- Log all operations to file
- Configurable log level
- Rotation for large log files
- Separate error log

**Implementation:**
```python
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(
            'artifacts/pipeline.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        ),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info("Starting pipeline...")
logger.error(f"Download failed: {filename} - {error}")
```

### 4. Unit Tests

**Priority:** Medium
**Effort:** Medium
**Timeline:** 3-5 days

**Description:**
Comprehensive unit tests for all functions.

**Test Coverage:**
- `fetch_document_list()` - Web scraping
- `download_file_worker()` - Download logic
- `extract_file_worker()` - Extraction logic
- `convert_document_worker()` - Conversion logic
- Skip logic verification
- Error handling verification

**Implementation (pytest):**
```python
# test_download_tdocs.py

import pytest
from download_tdocs import fetch_document_list, download_file_worker

def test_fetch_document_list():
    """Test fetching document list."""
    files = fetch_document_list(BASE_URL)
    assert isinstance(files, list)
    assert len(files) > 0
    assert all(f.endswith('.zip') for f in files)
    assert all(f.startswith('R1-') for f in files)

def test_download_skip_existing(tmp_path):
    """Test skip logic for existing files."""
    # Create dummy file
    test_file = tmp_path / "R1-2508300.zip"
    test_file.write_text("test")

    result = download_file_worker("R1-2508300.zip")
    assert result['status'] == 'skip'
    assert 'Already exists' in result['message']
```

## Medium-Term Enhancements

### 5. Database Integration

**Priority:** High
**Effort:** High
**Timeline:** 1-2 weeks

**Description:**
SQLite database for metadata tracking and querying.

**Database Schema:**
- `tdoc_files` - TDoc ZIP metadata
- `documents` - Individual document metadata
- `processing_tasks` - Task tracking
- `task_logs` - Detailed logs

**Benefits:**
- Fast querying and filtering
- Metadata persistence
- Task history
- Statistics and reporting

**See:** [Web App Plan](web-app-plan.md) for full database schema

### 6. RESTful API

**Priority:** High
**Effort:** High
**Timeline:** 1-2 weeks

**Description:**
FastAPI-based REST API for programmatic access.

**Endpoints:**
- `GET /api/v1/documents` - List documents
- `GET /api/v1/documents/{id}` - Get document
- `GET /api/v1/documents/{id}/html` - Get HTML content
- `POST /api/v1/tasks/download` - Start download task
- `GET /api/v1/tasks/{id}` - Get task status

**Example:**
```python
import requests

# List documents
response = requests.get('http://localhost:8000/api/v1/documents')
documents = response.json()

# Start download task
response = requests.post('http://localhost:8000/api/v1/tasks/download')
task = response.json()
task_id = task['task_id']

# Check task status
response = requests.get(f'http://localhost:8000/api/v1/tasks/{task_id}')
status = response.json()
```

### 7. Web-Based Progress Monitoring

**Priority:** High
**Effort:** Medium
**Timeline:** 1 week

**Description:**
Real-time progress updates via WebSocket.

**Features:**
- Live progress bars
- Real-time status updates
- Task monitoring dashboard
- Error notifications

**Implementation:**
```python
# WebSocket endpoint
@app.websocket("/ws/tasks/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    await websocket.accept()
    while True:
        # Get task progress from database
        progress = get_task_progress(task_id)
        await websocket.send_json(progress)
        await asyncio.sleep(1)
```

### 8. Search and Filtering

**Priority:** Medium
**Effort:** Medium
**Timeline:** 1 week

**Description:**
Full-text search across converted documents.

**Features:**
- Search document content
- Filter by TDoc ID
- Filter by file type
- Filter by date range
- Advanced query syntax

**Technologies:**
- SQLite FTS5 (Full-Text Search)
- Or Elasticsearch for advanced search

**Implementation:**
```sql
-- Create FTS5 table
CREATE VIRTUAL TABLE documents_fts USING fts5(
    tdoc_id,
    filename,
    content
);

-- Search query
SELECT * FROM documents_fts
WHERE documents_fts MATCH '5G NR beamforming';
```

## Long-Term Vision

### 9. Web Application (Complete)

**Priority:** Highest
**Effort:** Very High
**Timeline:** 3-4 weeks

**Description:**
Full-stack web application for managing and viewing TDoc files.

**See:** [Web App Implementation Plan](web-app-plan.md) for complete specification

**Key Features:**
- Vue.js 3 frontend
- FastAPI backend
- Document viewer
- Task monitoring
- Search and filter
- RESTful API
- WebSocket real-time updates
- Docker deployment

**Architecture:**
```
Frontend (Vue.js) ←→ Backend (FastAPI) ←→ Database (SQLite)
                     ↓
               File Storage (artifacts/)
```

### 10. Advanced Document Processing

**Priority:** Medium
**Effort:** High
**Timeline:** 2-3 weeks

**Description:**
Enhanced document processing and analysis.

**Features:**
- **OCR**: Extract text from scanned PDFs
- **NLP**: Extract entities, keywords, summaries
- **Classification**: Auto-categorize documents
- **Relationship Mapping**: Link related documents
- **Diff Analysis**: Compare document versions

**Technologies:**
- Tesseract OCR
- spaCy or NLTK for NLP
- scikit-learn for classification

### 11. Collaborative Features

**Priority:** Low
**Effort:** High
**Timeline:** 2-3 weeks

**Description:**
Multi-user collaboration and annotation.

**Features:**
- User authentication
- Document annotations
- Comments and discussions
- Sharing and permissions
- Activity tracking

**Technologies:**
- OAuth2 authentication
- User management system
- Real-time collaboration (WebSocket)

### 12. Export and Reporting

**Priority:** Medium
**Effort:** Medium
**Timeline:** 1-2 weeks

**Description:**
Export data and generate reports.

**Features:**
- Export to various formats (PDF, DOCX, CSV)
- Custom report generation
- Statistics dashboards
- Data analytics
- Batch export

**Technologies:**
- Pandoc for format conversion
- Matplotlib/Plotly for visualizations
- ReportLab for PDF generation

### 13. Cloud Deployment

**Priority:** Low
**Effort:** Medium
**Timeline:** 1 week

**Description:**
Deploy to cloud platforms.

**Platforms:**
- AWS (EC2, S3, RDS)
- Google Cloud Platform
- Azure
- DigitalOcean

**Features:**
- Scalable infrastructure
- Load balancing
- Auto-scaling
- CDN for static files
- Backup and disaster recovery

### 14. Mobile Application

**Priority:** Low
**Effort:** Very High
**Timeline:** 4-6 weeks

**Description:**
Native mobile apps for iOS and Android.

**Features:**
- Document browsing
- Offline access
- Push notifications
- Mobile-optimized viewer

**Technologies:**
- React Native
- Flutter
- Or native (Swift/Kotlin)

## Implementation Priority Matrix

| Feature | Priority | Effort | Impact | Timeline |
|---------|----------|--------|--------|----------|
| Command-Line Arguments | High | Low | Medium | 1-2 days |
| File Logging | High | Low | High | 1 day |
| Configuration File | Medium | Low | Medium | 1-2 days |
| Unit Tests | Medium | Medium | High | 3-5 days |
| Database Integration | High | High | Very High | 1-2 weeks |
| RESTful API | High | High | Very High | 1-2 weeks |
| Web App (Complete) | Highest | Very High | Very High | 3-4 weeks |
| WebSocket Progress | High | Medium | High | 1 week |
| Search/Filter | Medium | Medium | High | 1 week |
| Advanced Processing | Medium | High | Medium | 2-3 weeks |
| Export/Reporting | Medium | Medium | Medium | 1-2 weeks |
| Collaborative Features | Low | High | Medium | 2-3 weeks |
| Cloud Deployment | Low | Medium | Medium | 1 week |
| Mobile App | Low | Very High | Low | 4-6 weeks |

## Contributing

Interested in implementing any of these features? See the [Contributing Guide](../development/contributing.md) for development workflow and guidelines.

## Feedback

Have suggestions for additional features? Please open an issue on [GitHub](https://github.com/yhsung/3gpp-tdoc-portal/issues) with the "enhancement" label.

---

**Navigation:**
- [← Planning Overview](../README.md#planning)
- [Documentation Home](../README.md)
- [→ Next: Web App Plan](web-app-plan.md)

**Related:**
- [Contributing Guide](../development/contributing.md)
- [System Overview](../architecture/overview.md)
- [Script Reference](../development/script-reference.md)
