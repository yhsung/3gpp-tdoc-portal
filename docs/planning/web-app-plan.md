# Web Application Plan

[← Back to Planning](../README.md#-planning)

## Overview

This document provides a high-level overview of the web application development plan for the 3GPP TDoc Portal. For complete technical specifications, see the full implementation plan.

## Vision

Transform the command-line TDoc processing pipeline into a full-featured web application with:

- **Web-based UI** for document browsing and viewing
- **Real-time monitoring** of download/extract/convert tasks
- **Search and filtering** across all documents
- **RESTful API** for programmatic access
- **Docker deployment** for easy installation

## Architecture

### High-Level Design

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

## Technology Stack

### Backend
- **Framework**: FastAPI (Python)
  - Async support
  - WebSocket support
  - Automatic API documentation
  - Type validation with Pydantic

### Frontend
- **Framework**: Vue.js 3
  - Composition API
  - TypeScript support
  - Component-based architecture
- **Build Tool**: Vite
- **State Management**: Pinia
- **Routing**: Vue Router
- **HTTP Client**: Axios

### Database
- **Database**: SQLite
  - Lightweight, serverless
  - Easy deployment
  - Sufficient for single-server deployment
  - Can migrate to PostgreSQL later

### Task Processing
- **Approach**: FastAPI Background Tasks
  - Simpler than Celery
  - No additional dependencies (Redis)
  - Suitable for single-server deployment

### Deployment
- **Containerization**: Docker
- **Orchestration**: Docker Compose
  - Frontend container (Nginx)
  - Backend container (FastAPI)
  - Shared volume for artifacts

## Key Features

### 1. Document Management

**Document List View:**
- Paginated table/grid of all documents
- Columns: TDoc ID, Filename, Type, Size, Status, Date
- Search bar for filtering
- Sort by any column
- Bulk actions (download, export)

**Document Viewer:**
- Display HTML-converted documents in iframe
- Metadata sidebar (TDoc ID, file size, conversion date)
- Download buttons (original, HTML, Markdown)
- Previous/Next navigation
- Full-screen mode

### 2. Task Monitoring

**Task Dashboard:**
- List of active tasks with progress bars
- Task history with completion status
- Real-time updates via WebSocket
- Task details (start time, duration, items processed)

**Task Controls:**
- Start new download task
- Start extract task
- Start convert task
- Start full pipeline task
- Cancel running task (future)

### 3. Search and Filter

**Search Capabilities:**
- Search by TDoc ID
- Search by filename
- Search by document content (future)
- Advanced filters (file type, date range, status)

**Filter Options:**
- File type (PDF, DOCX, PPTX, XLSX)
- Conversion status (pending, completed, failed)
- Date range
- TDoc ID range

### 4. REST API

**Document Endpoints:**
```
GET    /api/v1/documents           # List documents (paginated)
GET    /api/v1/documents/{id}      # Get document metadata
GET    /api/v1/documents/{id}/html # Serve HTML content
GET    /api/v1/documents/{id}/md   # Serve Markdown content
GET    /api/v1/documents/{id}/download # Download original file
```

**TDoc Endpoints:**
```
GET    /api/v1/tdocs               # List TDoc files
GET    /api/v1/tdocs/{id}          # Get TDoc metadata
GET    /api/v1/tdocs/{id}/documents # List documents in TDoc
```

**Task Endpoints:**
```
POST   /api/v1/tasks/download      # Start download task
POST   /api/v1/tasks/extract       # Start extraction task
POST   /api/v1/tasks/convert       # Start conversion task
POST   /api/v1/tasks/process-all   # Start full pipeline
GET    /api/v1/tasks/{task_id}     # Get task status
GET    /api/v1/tasks/{task_id}/logs # Get task logs
```

**WebSocket:**
```
WS     /ws/tasks/{task_id}         # Real-time task updates
```

## Database Schema

### Core Tables

**1. tdoc_files** - Master table for TDoc ZIP files
```sql
- id (PRIMARY KEY)
- filename (VARCHAR, UNIQUE)
- tdoc_id (VARCHAR)
- file_url (TEXT)
- file_size (BIGINT)
- download_status (VARCHAR)
- extract_status (VARCHAR)
- created_at, updated_at (TIMESTAMP)
```

**2. documents** - Individual documents within TDocs
```sql
- id (PRIMARY KEY)
- tdoc_file_id (FOREIGN KEY)
- original_filename (VARCHAR)
- file_type (VARCHAR)
- file_path (TEXT)
- conversion_status (VARCHAR)
- html_path, markdown_path (TEXT)
- created_at, converted_at (TIMESTAMP)
```

**3. processing_tasks** - Task execution tracking
```sql
- id (PRIMARY KEY)
- task_id (VARCHAR, UNIQUE)
- task_type (VARCHAR)
- status (VARCHAR)
- progress (INTEGER)
- total_items, processed_items (INTEGER)
- created_at, completed_at (TIMESTAMP)
```

**4. task_logs** - Detailed task logs
```sql
- id (PRIMARY KEY)
- task_id (FOREIGN KEY)
- log_level (VARCHAR)
- message (TEXT)
- timestamp (TIMESTAMP)
```

## Implementation Phases

### Phase 1: Backend Development (1-2 weeks)
1. Set up FastAPI project structure
2. Create database models and schemas
3. Refactor existing code into core modules
4. Implement API endpoints
5. Implement background task manager
6. Add WebSocket support

### Phase 2: Frontend Development (1-2 weeks)
1. Set up Vue.js project
2. Create API client service
3. Implement document list view
4. Implement document viewer
5. Implement task monitor
6. Add search and filter UI

### Phase 3: Integration (3-5 days)
1. Connect frontend to backend API
2. Implement WebSocket integration
3. Test all features end-to-end
4. Fix bugs and polish UI

### Phase 4: Docker Deployment (1-2 days)
1. Create Dockerfiles for frontend and backend
2. Create docker-compose.yml
3. Configure Nginx for frontend
4. Test deployment locally
5. Write deployment documentation

### Phase 5: Testing & Documentation (2-3 days)
1. Comprehensive testing
2. Write user documentation
3. Write API documentation
4. Create deployment guide

**Total Estimated Timeline: 3-4 weeks**

## User Workflows

### Workflow 1: View Documents

1. User navigates to web application
2. Document list loads automatically
3. User uses search/filter to find documents
4. User clicks on document to view
5. Document viewer opens with HTML content
6. User can download HTML, Markdown, or original file

### Workflow 2: Process New TDocs

1. User navigates to task monitor
2. User clicks "Start Download Task"
3. Backend starts download in background
4. Progress bar updates in real-time via WebSocket
5. Upon completion, extraction and conversion start automatically
6. User receives notification when complete
7. New documents appear in document list

### Workflow 3: API Integration

Developer wants to integrate with their system:

```python
import requests

# List all documents
response = requests.get('http://localhost:8000/api/v1/documents')
documents = response.json()['items']

# Search for specific TDoc
response = requests.get('http://localhost:8000/api/v1/documents', params={
    'tdoc_id': 'R1-2508300'
})

# Download document HTML
doc_id = documents[0]['id']
html = requests.get(f'http://localhost:8000/api/v1/documents/{doc_id}/html').text

# Start processing task
task = requests.post('http://localhost:8000/api/v1/tasks/process-all').json()
task_id = task['task_id']

# Monitor task progress
while True:
    status = requests.get(f'http://localhost:8000/api/v1/tasks/{task_id}').json()
    if status['status'] == 'completed':
        break
    time.sleep(1)
```

## Deployment

### Docker Compose Setup

```yaml
version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./artifacts:/app/artifacts
    environment:
      - DATABASE_URL=sqlite:///artifacts/db/tdocs.db
```

### Running the Application

```bash
# Clone repository
git clone https://github.com/yhsung/3gpp-tdoc-portal.git
cd 3gpp-tdoc-portal

# Build and start services
docker-compose up -d

# Access application
open http://localhost
```

## Benefits Over CLI

### For End Users
- ✅ No Python installation required
- ✅ Graphical interface (easier to use)
- ✅ View documents in browser
- ✅ Real-time progress monitoring
- ✅ Search and filter documents
- ✅ No command-line knowledge needed

### For Developers
- ✅ RESTful API for integration
- ✅ Programmatic access to documents
- ✅ WebSocket for real-time updates
- ✅ Well-documented endpoints
- ✅ Database for complex queries

### For Administrators
- ✅ Easy deployment with Docker
- ✅ Web-based monitoring
- ✅ Task history and logging
- ✅ No manual file management
- ✅ Centralized access

## Full Technical Specification

For complete implementation details, including:
- Detailed API specifications
- Database schema with relationships
- Frontend component architecture
- Background task implementation
- Security considerations
- Testing strategy

**See:** [specs/web-app-implementation-plan.md](../../specs/web-app-implementation-plan.md)

## Contributing

Interested in contributing to the web application? See:
- [Contributing Guide](../development/contributing.md)
- [Future Enhancements](future-enhancements.md)
- [GitHub Repository](https://github.com/yhsung/3gpp-tdoc-portal)

---

**Navigation:**
- [← Future Enhancements](future-enhancements.md)
- [Documentation Home](../README.md)
- [Planning Overview](../README.md#planning)

**Related:**
- [System Overview](../architecture/overview.md)
- [Full Web App Spec](../../specs/web-app-implementation-plan.md)
- [Script Reference](../development/script-reference.md)
