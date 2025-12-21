# Web Application Implementation Plan for 3GPP TDoc Manager

## Overview
Build a full-stack web application to manage 3GPP TDoc files with download, extraction, conversion, document listing, and HTML viewing capabilities.

**Tech Stack:**
- Backend: FastAPI (async, WebSocket support)
- Frontend: Vue.js 3 with Vite
- Task Processing: FastAPI Background Tasks
- Database: SQLite with SQLAlchemy ORM
- Deployment: Docker Compose

## Architecture

```
┌─────────────────────────────────────────┐
│    Vue.js 3 Frontend (SPA)             │
│  - Document List with Search/Filter     │
│  - HTML Document Viewer                 │
│  - Task Monitor with Progress           │
└─────────────────────────────────────────┘
              ↓ HTTP + WebSocket
┌─────────────────────────────────────────┐
│    FastAPI Backend                      │
│  - REST API Endpoints                   │
│  - WebSocket for Real-time Updates      │
│  - Background Task Processing           │
└─────────────────────────────────────────┘
      ↓               ↓              ↓
 ┌────────┐    ┌──────────┐   ┌──────────┐
 │ SQLite │    │   File   │   │ In-Memory│
 │   DB   │    │  Storage │   │  Queue   │
 └────────┘    └──────────┘   └──────────┘
```

## Directory Structure

```
3gpp-tdoc-web/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app entry point
│   │   ├── config.py               # Configuration
│   │   ├── database.py             # Database setup
│   │   ├── models.py               # SQLAlchemy models
│   │   ├── schemas.py              # Pydantic schemas
│   │   ├── api/
│   │   │   ├── documents.py        # Document endpoints
│   │   │   ├── tdocs.py            # TDoc file endpoints
│   │   │   ├── tasks.py            # Task endpoints
│   │   │   └── websocket.py        # WebSocket handlers
│   │   ├── core/
│   │   │   ├── downloader.py       # Download logic (refactored)
│   │   │   ├── extractor.py        # Extract logic (refactored)
│   │   │   ├── converter.py        # Convert logic (refactored)
│   │   │   └── scraper.py          # 3GPP scraping
│   │   └── background/
│   │       └── tasks.py            # Background task manager
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── main.js
│   │   ├── App.vue
│   │   ├── router/index.js
│   │   ├── views/
│   │   │   ├── DocumentList.vue    # Main listing page
│   │   │   ├── DocumentViewer.vue  # HTML viewer
│   │   │   └── TaskMonitor.vue     # Task status page
│   │   ├── components/
│   │   │   ├── DocumentCard.vue
│   │   │   ├── ProgressBar.vue
│   │   │   ├── TaskStatus.vue
│   │   │   └── SearchFilter.vue
│   │   └── services/
│   │       └── api.js              # API client
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
├── docker-compose.yml
└── data/                            # Mounted volume
    ├── tdocs/
    ├── extracted/
    ├── output/
    └── db/
```

## Database Schema

### Tables

**1. tdoc_files** - Master table for TDoc ZIP files
```sql
- id (PRIMARY KEY)
- filename (VARCHAR, UNIQUE) - e.g., "R1-2508300.zip"
- tdoc_id (VARCHAR) - e.g., "R1-2508300"
- file_url (TEXT)
- file_size (BIGINT)
- download_status (VARCHAR) - pending/downloading/completed/failed
- extract_status (VARCHAR) - pending/extracting/completed/failed
- download_path, extract_path (TEXT)
- error_message (TEXT)
- created_at, updated_at, downloaded_at, extracted_at (TIMESTAMP)
```

**2. documents** - Individual documents within TDocs
```sql
- id (PRIMARY KEY)
- tdoc_file_id (FOREIGN KEY → tdoc_files)
- original_filename (VARCHAR) - e.g., "proposal.docx"
- file_type (VARCHAR) - pdf/docx/pptx/etc
- file_path (TEXT) - full path to original
- file_size (BIGINT)
- conversion_status (VARCHAR) - pending/converting/completed/failed
- html_path, markdown_path (TEXT)
- html_size, markdown_size (BIGINT)
- error_message (TEXT)
- created_at, updated_at, converted_at (TIMESTAMP)
```

**3. processing_tasks** - Task execution tracking
```sql
- id (PRIMARY KEY)
- task_id (VARCHAR, UNIQUE)
- task_type (VARCHAR) - download_all/extract_all/convert_all/process_all
- status (VARCHAR) - pending/running/completed/failed
- progress (INTEGER) - 0-100
- total_items, processed_items, failed_items, skipped_items (INTEGER)
- error_message (TEXT)
- started_at, completed_at, created_at (TIMESTAMP)
```

**4. task_logs** - Detailed task logs
```sql
- id (PRIMARY KEY)
- task_id (FOREIGN KEY → processing_tasks)
- log_level (VARCHAR) - INFO/WARNING/ERROR
- message (TEXT)
- metadata (JSON)
- timestamp (TIMESTAMP)
```

## API Endpoints

### Documents API (`/api/v1/documents`)
- `GET /api/v1/documents` - List documents (paginated, filterable)
- `GET /api/v1/documents/{id}` - Get document metadata
- `GET /api/v1/documents/{id}/html` - Serve HTML content
- `GET /api/v1/documents/{id}/markdown` - Serve Markdown content
- `GET /api/v1/documents/{id}/download` - Download original file

### TDocs API (`/api/v1/tdocs`)
- `GET /api/v1/tdocs` - List TDoc files (paginated)
- `GET /api/v1/tdocs/{id}` - Get TDoc metadata
- `GET /api/v1/tdocs/{id}/documents` - List documents in TDoc

### Tasks API (`/api/v1/tasks`)
- `POST /api/v1/tasks/download` - Start download task
- `POST /api/v1/tasks/extract` - Start extraction task
- `POST /api/v1/tasks/convert` - Start conversion task
- `POST /api/v1/tasks/process-all` - Start full pipeline
- `GET /api/v1/tasks/{task_id}` - Get task status
- `GET /api/v1/tasks/{task_id}/logs` - Get task logs

### Stats API (`/api/v1/stats`)
- `GET /api/v1/stats/overview` - Get overview statistics

### WebSocket
- `WS /ws/tasks/{task_id}` - Real-time task progress updates

## Implementation Steps

### Phase 1: Backend Setup (Priority: HIGH)

**1.1 Project Structure**
- Create backend directory structure
- Set up virtual environment
- Install dependencies: fastapi, uvicorn, sqlalchemy, requests, beautifulsoup4, docling, tqdm

**1.2 Database Setup**
- Create `models.py` with SQLAlchemy models (4 tables)
- Create `database.py` with database connection setup
- Create `schemas.py` with Pydantic request/response models
- Add Alembic for migrations

**1.3 Refactor Existing Code**
- Extract `download_file_worker` → `core/downloader.py`
  - Add database integration
  - Add progress callback parameter
  - Return structured result dict

- Extract `extract_file_worker` → `core/extractor.py`
  - Add database integration
  - Add progress callback

- Extract `convert_document_worker` → `core/converter.py`
  - Add database integration
  - Add progress callback

- Extract `fetch_document_list` → `core/scraper.py`
  - Keep existing functionality
  - Add database persistence option

**1.4 Background Task Manager**
- Create `background/tasks.py` with BackgroundTaskManager class
- Implement in-memory task queue
- Add progress tracking with WebSocket broadcasting
- Implement parallel processing using ProcessPoolExecutor (4 workers)

**1.5 API Implementation**
- Create `api/documents.py` - Document CRUD endpoints
- Create `api/tdocs.py` - TDoc file endpoints
- Create `api/tasks.py` - Task management endpoints
- Create `api/websocket.py` - WebSocket connection manager
- Create `main.py` - FastAPI app with all routes registered

### Phase 2: Frontend Development (Priority: HIGH)

**2.1 Project Setup**
- Initialize Vue 3 + Vite project
- Install dependencies: vue-router, axios, pinia
- Configure Vite for API proxy

**2.2 Core Services**
- Create `services/api.js` - Axios-based API client
- Create composable `useWebSocket.js` - WebSocket connection management

**2.3 State Management**
- Create Pinia store `stores/documents.js` - Document state
- Create Pinia store `stores/tasks.js` - Task state

**2.4 Views**
- Create `DocumentList.vue`
  - Paginated table/grid of documents
  - Search bar (TDoc ID, filename)
  - Filters (file type, status)
  - Click to view document

- Create `DocumentViewer.vue`
  - Iframe to display HTML content
  - Metadata sidebar
  - Download buttons (HTML/MD/original)
  - Previous/Next navigation

- Create `TaskMonitor.vue`
  - List of active tasks with progress bars
  - Task history
  - Start new task buttons
  - Real-time updates via WebSocket

**2.5 Components**
- Create `DocumentCard.vue` - Individual document display
- Create `ProgressBar.vue` - Animated progress indicator
- Create `TaskStatus.vue` - Task status badge
- Create `SearchFilter.vue` - Search and filter controls

**2.6 Routing**
- `/` - DocumentList
- `/view/:id` - DocumentViewer
- `/tasks` - TaskMonitor

### Phase 3: Integration (Priority: MEDIUM)

**3.1 WebSocket Integration**
- Connect TaskMonitor to WebSocket endpoint
- Update progress bars in real-time
- Handle connection errors and reconnection

**3.2 Background Task Processing**
- Implement download_all task with progress updates
- Implement extract_all task with progress updates
- Implement convert_all task with progress updates
- Implement process_all pipeline task
- Test parallel processing with 4 workers

**3.3 File Serving**
- Configure static file serving for HTML/MD files
- Add security checks for file path validation
- Test document viewing in iframe

### Phase 4: Docker Deployment (Priority: MEDIUM)

**4.1 Dockerfiles**
- Create `backend/Dockerfile`
  - Multi-stage build
  - Python 3.11+ base image
  - Install dependencies
  - Copy application code

- Create `frontend/Dockerfile`
  - Node.js base image
  - Build Vue app
  - Nginx to serve static files

**4.2 Docker Compose**
- Create `docker-compose.yml`
  - Service: frontend (Nginx)
  - Service: backend (FastAPI)
  - Volume: data (persistent storage)
  - Networks: bridge network

**4.3 Nginx Configuration**
- Serve frontend static files
- Proxy `/api` to backend
- Proxy `/ws` to backend WebSocket
- Serve `/files` for document access

### Phase 5: Testing & Refinement (Priority: LOW)

**5.1 Testing**
- Test download/extract/convert pipeline
- Test WebSocket real-time updates
- Test pagination and filtering
- Test document viewer with various file types
- Test error handling

**5.2 Performance**
- Optimize database queries with indexes
- Add caching for document list
- Test with large number of files

**5.3 UX Improvements**
- Add loading states
- Add error messages
- Add success notifications
- Improve responsive design

## Critical Files to Create

### Backend (Priority Order)

1. **`backend/app/models.py`** - Database models
   - Define SQLAlchemy models for 4 tables
   - Set up relationships and indexes

2. **`backend/app/core/downloader.py`** - Download logic
   - Refactor `download_file_worker` from download_tdocs.py
   - Add database updates
   - Add progress callback

3. **`backend/app/background/tasks.py`** - Task manager
   - BackgroundTaskManager class
   - Task queue and processing
   - WebSocket progress broadcasting

4. **`backend/app/api/tasks.py`** - Task API
   - Endpoints to start/monitor tasks
   - Integration with background manager

5. **`backend/app/main.py`** - FastAPI app
   - Application setup
   - Route registration
   - CORS configuration

### Frontend (Priority Order)

1. **`frontend/src/services/api.js`** - API client
   - Axios instance with base URL
   - API methods for all endpoints

2. **`frontend/src/views/DocumentList.vue`** - Main view
   - Document listing with pagination
   - Search and filters
   - Primary user interface

3. **`frontend/src/views/DocumentViewer.vue`** - Viewer
   - HTML document display in iframe
   - Metadata and controls

4. **`frontend/src/composables/useWebSocket.js`** - WebSocket
   - Connection management
   - Message handling
   - Reconnection logic

5. **`frontend/src/views/TaskMonitor.vue`** - Task monitoring
   - Active tasks display
   - Progress bars with real-time updates
   - Task controls

## Background Task Implementation (FastAPI Approach)

Since we're using FastAPI Background Tasks instead of Celery:

**Task Manager Pattern:**
```python
# backend/app/background/tasks.py

from concurrent.futures import ProcessPoolExecutor
import asyncio
from typing import Dict, Callable

class BackgroundTaskManager:
    def __init__(self, max_workers=4):
        self.executor = ProcessPoolExecutor(max_workers=max_workers)
        self.active_tasks: Dict[str, TaskInfo] = {}

    async def submit_task(self, task_id: str, func: Callable, *args):
        """Submit task to process pool"""
        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(self.executor, func, *args)
        self.active_tasks[task_id] = TaskInfo(future, ...)

    async def get_progress(self, task_id: str):
        """Get task progress from database"""
        # Query database for task progress
        pass
```

**Progress Updates:**
- Workers update database with progress
- WebSocket endpoint polls database and broadcasts
- Frontend receives real-time updates via WebSocket

## Data Migration

Create migration script to populate database from existing files:

```python
# scripts/migrate_existing_data.py

def migrate_existing_files():
    # 1. Scan tdocs/ directory → create tdoc_files records
    # 2. Scan extracted/ directory → create document records
    # 3. Scan output/ directory → update conversion status
```

## Key Design Decisions

1. **FastAPI Background Tasks vs Celery**: Simpler setup, no Redis needed, suitable for single-server deployment
2. **SQLite vs PostgreSQL**: Start with SQLite for simplicity, can migrate later
3. **WebSocket for Progress**: Real-time updates without polling
4. **Vue.js SPA**: Better UX with client-side routing and state management
5. **Docker Compose**: Easy deployment and service orchestration

## Success Criteria

- ✅ Users can view list of all TDoc documents
- ✅ Users can search/filter documents by name, type, status
- ✅ Users can view HTML-converted documents in browser
- ✅ Users can trigger download/extract/convert operations
- ✅ Users can monitor task progress in real-time
- ✅ System skips already processed files (resume capability)
- ✅ Application runs in Docker containers
- ✅ All existing download_tdocs.py functionality preserved

## Timeline Estimate

- Phase 1 (Backend): 3-4 days
- Phase 2 (Frontend): 3-4 days
- Phase 3 (Integration): 2 days
- Phase 4 (Docker): 1 day
- Phase 5 (Testing): 1-2 days

**Total: 10-13 days**
