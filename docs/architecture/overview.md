# System Architecture Overview

[← Back to Documentation](../README.md)

## Purpose

The 3GPP TDoc Portal is designed as a high-performance document processing pipeline that downloads, extracts, and converts 3GPP technical documents.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│              3GPP TDoc Portal                       │
│                                                     │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    │
│  │  Phase 1 │ →  │  Phase 2 │ →  │  Phase 3 │    │
│  │ Download │    │ Extract  │    │ Convert  │    │
│  └──────────┘    └──────────┘    └──────────┘    │
│       ↓               ↓               ↓           │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    │
│  │ 4 Workers│    │ 4 Workers│    │ 4 Workers│    │
│  │ Parallel │    │ Parallel │    │ Parallel │    │
│  └──────────┘    └──────────┘    └──────────┘    │
└─────────────────────────────────────────────────────┘
         ↓               ↓               ↓
    artifacts/      artifacts/      artifacts/
      tdocs/        extracted/       output/
```

## Core Components

### 1. Web Scraper
**Module:** `fetch_document_list()`
- Scrapes 3GPP RAN1 documents directory
- Extracts TDoc file listings using regex
- Returns list of filenames to process

### 2. Download Engine
**Module:** `download_file_worker()`
- Downloads ZIP files in parallel (4 workers)
- Streaming downloads with chunked writes
- Smart skip logic for existing files
- Automatic cleanup on failure

### 3. Extraction Engine
**Module:** `extract_file_worker()`
- Extracts ZIP archives in parallel
- Preserves directory structure
- Validates ZIP integrity
- Skips already extracted files

### 4. Conversion Engine
**Module:** `convert_document_worker()`
- Converts documents using Docling
- Parallel processing (4 workers)
- Exports to HTML and Markdown
- Supports multiple document formats

### 5. Progress Monitoring
**Technology:** tqdm
- Real-time progress bars
- Per-file status updates
- Summary statistics
- Three-phase tracking

## Technology Stack

**Core:**
- **Language:** Python 3.11+
- **Concurrency:** ProcessPoolExecutor (multiprocessing)
- **HTTP:** requests library
- **HTML Parsing:** BeautifulSoup4
- **Document Conversion:** Docling
- **Progress:** tqdm

**Supported Formats:**
- PDF documents
- Microsoft Word (DOCX, DOC)
- Microsoft PowerPoint (PPTX, PPT)
- Microsoft Excel (XLSX, XLS)

## Processing Pipeline

### Phase 1: Download
1. Scrape 3GPP website for TDoc listings
2. Create download tasks for each file
3. Execute downloads in parallel (4 workers)
4. Track progress and handle errors
5. Skip existing files automatically

### Phase 2: Extract
1. Scan downloaded ZIP files
2. Create extraction tasks
3. Execute extractions in parallel (4 workers)
4. Validate ZIP integrity
5. Skip already extracted archives

### Phase 3: Convert
1. Scan extracted documents
2. Filter by supported formats
3. Create conversion tasks
4. Execute conversions in parallel (4 workers)
5. Export to HTML and Markdown
6. Skip already converted documents

## Design Decisions

### Multi-Processing over Multi-Threading
**Rationale:** Document conversion is CPU-intensive
- Python GIL limits multi-threading effectiveness
- ProcessPoolExecutor provides true parallelism
- Each worker runs in separate process

### Three-Phase Pipeline
**Rationale:** Clear separation of concerns
- Download → Extract → Convert
- Each phase can be rerun independently
- Easy to debug and maintain
- Enables resume capability

### Smart Skip Logic
**Rationale:** Enable resumption and avoid redundant work
- Check file existence before processing
- Validate completeness (both HTML and MD for conversion)
- Graceful handling of partial failures

### Worker Pool Size (4)
**Rationale:** Balance between performance and resource usage
- Most modern CPUs have 4+ cores
- Avoids overwhelming the system
- Good balance for network I/O and CPU work

## Data Flow

```
3GPP Website
    ↓
fetch_document_list()
    ↓
TDoc File List
    ↓
download_file_worker() × 4
    ↓
artifacts/tdocs/*.zip
    ↓
extract_file_worker() × 4
    ↓
artifacts/extracted/R1-*/
    ↓
convert_document_worker() × 4
    ↓
artifacts/output/{html,markdown}/
```

## Scalability Considerations

**Current Limitations:**
- Single machine execution
- Fixed worker count (4)
- Sequential phase execution
- No distributed processing

**Future Improvements:**
- Configurable worker count
- Distributed task processing
- Phase parallelization
- Cloud storage integration

## Error Handling Strategy

1. **Network Errors:** Retry with cleanup
2. **ZIP Errors:** Skip and log
3. **Conversion Errors:** Skip and continue
4. **File System Errors:** Propagate and halt

---

**Navigation:**
- [← Documentation Home](../README.md)
- [→ Directory Structure](directory-structure.md)

**Related:**
- [Multi-Processing Details](../features/multi-processing.md)
- [Error Handling Guide](../features/error-handling.md)
