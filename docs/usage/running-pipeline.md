# Running the Pipeline

[← Back to Usage](../README.md#-usage)

## Overview

This guide provides comprehensive instructions for running the 3GPP TDoc Portal pipeline, including all three phases, command-line usage, and output interpretation.

## Pipeline Overview

The 3GPP TDoc Portal operates as a three-phase pipeline:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Phase 1   │───▶│   Phase 2   │───▶│   Phase 3   │
│  Download   │    │   Extract   │    │   Convert   │
└─────────────┘    └─────────────┘    └─────────────┘
     ↓                   ↓                   ↓
 ZIP files         Extracted docs      HTML + Markdown
 artifacts/tdocs/  artifacts/extracted/ artifacts/output/
```

## Running the Script

### Basic Execution

```bash
python download_tdocs.py
```

### What Happens

1. **Initialization**
   - Creates directory structure (if not exists)
   - Fetches list of TDoc files from 3GPP server

2. **Phase 1: Download**
   - Downloads all TDoc ZIP files
   - Uses 4 parallel workers
   - Skips already downloaded files

3. **Phase 2: Extract**
   - Extracts all downloaded ZIP files
   - Uses 4 parallel workers
   - Skips already extracted files

4. **Phase 3: Convert**
   - Converts all documents to HTML and Markdown
   - Uses 4 parallel workers
   - Skips already converted files

## Phase 1: Download Details

### Purpose

Download all TDoc ZIP files from 3GPP server to `artifacts/tdocs/`.

### Process

```
Fetching TDoc file list from 3GPP server...
Found 630 TDoc files

=== Phase 1: Download Files ===
Download Progress: 100%|██████████| 630/630 [05:23<00:00, 1.95file/s]
[OK] R1-2508300.zip - 2.45 MB
[OK] R1-2508301.zip - 1.87 MB
[SKIP] R1-2508302.zip - Already exists
[FAIL] R1-2508303.zip - Connection timeout
```

### Output

**Success:**
```
[OK] R1-2508300.zip - 2.45 MB
```
File downloaded successfully, size displayed.

**Skip:**
```
[SKIP] R1-2508302.zip - Already exists
```
File already exists in `artifacts/tdocs/`, skip download.

**Fail:**
```
[FAIL] R1-2508303.zip - Connection timeout
```
Download failed, error message displayed.

### Summary

```
=== Download Summary ===
Successfully downloaded: 625 files
Skipped (already exists): 4 files
Failed: 1 files
```

### Skip Logic

Files are skipped if they exist in `artifacts/tdocs/`:
```python
if os.path.exists(filepath):
    return {'status': 'skip', 'message': 'Already exists'}
```

### Duration

- **First run**: ~5-10 minutes (depends on network speed)
- **Subsequent runs**: Seconds (only new files)

## Phase 2: Extract Details

### Purpose

Extract all downloaded ZIP files to `artifacts/extracted/{TDoc-ID}/`.

### Process

```
=== Phase 2: Extract Files ===
Extract Progress: 100%|██████████| 630/630 [03:45<00:00, 2.79file/s]
[OK] R1-2508300.zip - Extracted 3 files
[OK] R1-2508301.zip - Extracted 5 files
[SKIP] R1-2508302.zip - Already extracted
```

### Output

**Success:**
```
[OK] R1-2508300.zip - Extracted 3 files
```
ZIP extracted successfully, file count displayed.

**Skip:**
```
[SKIP] R1-2508302.zip - Already extracted
```
Directory already exists and contains files, skip extraction.

### Summary

```
=== Extract Summary ===
Successfully extracted: 629 ZIP files
Skipped (already extracted): 1 ZIP files
```

### Skip Logic

Files are skipped if directory exists and is non-empty:
```python
if os.path.exists(extract_path) and os.listdir(extract_path):
    return {'status': 'skip', 'message': 'Already extracted'}
```

### Directory Structure

Each TDoc is extracted to its own directory:
```
artifacts/extracted/
├── R1-2508300/
│   ├── proposal.docx
│   ├── meeting_notes.pdf
│   └── presentation.pptx
├── R1-2508301/
│   └── agenda.docx
└── ...
```

### Duration

- **First run**: ~3-5 minutes
- **Subsequent runs**: Seconds (only new files)

## Phase 3: Convert Details

### Purpose

Convert all documents to HTML and Markdown formats in `artifacts/output/`.

### Process

```
=== Phase 3: Convert Documents ===
Scanning for documents to convert...
Found 3257 documents to process

Convert Progress: 100%|██████████| 3257/3257 [35:12<00:00, 1.54file/s]
[OK] R1-2508300_proposal.docx - Converted successfully
[OK] R1-2508300_meeting_notes.pdf - Converted successfully
[SKIP] R1-2508301_agenda.docx - Already converted
[FAIL] R1-2508302_corrupted.pdf - Conversion failed: Invalid PDF
```

### Output

**Success:**
```
[OK] R1-2508300_proposal.docx - Converted successfully
```
Document converted to both HTML and Markdown.

**Skip:**
```
[SKIP] R1-2508301_agenda.docx - Already converted
```
Both HTML and Markdown files already exist, skip conversion.

**Fail:**
```
[FAIL] R1-2508302_corrupted.pdf - Conversion failed: Invalid PDF
```
Conversion failed, error message displayed.

### Summary

```
=== Convert Summary ===
Successfully converted: 3147 documents
Skipped (already converted): 98 documents
Failed: 12 documents
```

### Supported Formats

The conversion phase processes these file types:
- **PDF**: `.pdf`
- **Word**: `.docx`, `.doc`
- **PowerPoint**: `.pptx`, `.ppt`
- **Excel**: `.xlsx`, `.xls`

### Skip Logic

Documents are skipped if both HTML and Markdown exist:
```python
if os.path.exists(html_output_path) and os.path.exists(md_output_path):
    return {'status': 'skip', 'message': 'Already converted'}
```

### Output Structure

```
artifacts/output/
├── html/
│   ├── R1-2508300_proposal.html
│   ├── R1-2508300_meeting_notes.html
│   └── ...
└── markdown/
    ├── R1-2508300_proposal.md
    ├── R1-2508300_meeting_notes.md
    └── ...
```

### Duration

- **First run**: ~30-45 minutes (CPU-intensive)
- **Subsequent runs**: Minutes (only new files)

## Complete Pipeline Output

### Full Example

```bash
$ python download_tdocs.py
```

**Complete Output:**

```
Fetching TDoc file list from 3GPP server...
Found 630 TDoc files

=== Phase 1: Download Files ===
Download Progress: 100%|██████████| 630/630 [05:23<00:00, 1.95file/s]
[OK] R1-2508300.zip - 2.45 MB
[OK] R1-2508301.zip - 1.87 MB
...

=== Download Summary ===
Successfully downloaded: 625 files
Skipped (already exists): 4 files
Failed: 1 files

=== Phase 2: Extract Files ===
Extract Progress: 100%|██████████| 630/630 [03:45<00:00, 2.79file/s]
[OK] R1-2508300.zip - Extracted 3 files
[OK] R1-2508301.zip - Extracted 5 files
...

=== Extract Summary ===
Successfully extracted: 629 ZIP files
Skipped (already extracted): 1 ZIP files

=== Phase 3: Convert Documents ===
Scanning for documents to convert...
Found 3257 documents to process

Convert Progress: 100%|██████████| 3257/3257 [35:12<00:00, 1.54file/s]
[OK] R1-2508300_proposal.docx - Converted successfully
[OK] R1-2508300_meeting_notes.pdf - Converted successfully
...

=== Convert Summary ===
Successfully converted: 3147 documents
Skipped (already converted): 98 documents
Failed: 12 documents

=== Pipeline Complete ===
Output files located at:
  - HTML: artifacts/output/html/
  - Markdown: artifacts/output/markdown/
```

## Performance Metrics

### Typical First Run

| Phase | Duration | Files Processed | Rate |
|-------|----------|-----------------|------|
| Download | 5-10 min | 630 | 1.5-2 files/sec |
| Extract | 3-5 min | 630 | 2-3 files/sec |
| Convert | 30-45 min | 3257 | 1-1.5 files/sec |
| **Total** | **40-60 min** | **4517** | **1.25 files/sec** |

### Typical Incremental Run

With 10 new files added:

| Phase | Duration | Files Processed | Skipped |
|-------|----------|-----------------|---------|
| Download | ~10 sec | 10 | 630 |
| Extract | ~5 sec | 10 | 630 |
| Convert | ~2 min | 45 | 3257 |
| **Total** | **~2.5 min** | **65** | **4517** |

## Advanced Usage

### Environment Variables (Future)

Planned support for environment variables:

```bash
# Set custom artifacts directory
export TDOC_ARTIFACTS_DIR=/data/tdocs

# Set custom worker count
export TDOC_MAX_WORKERS=8

# Run script
python download_tdocs.py
```

### Programmatic Usage (Future)

Planned API for programmatic usage:

```python
from download_tdocs import TDocPipeline

pipeline = TDocPipeline(
    artifacts_dir="/data/tdocs",
    max_workers=8
)

# Run full pipeline
pipeline.run_all()

# Or run individual phases
pipeline.download()
pipeline.extract()
pipeline.convert()
```

## Monitoring Progress

### Real-Time Monitoring

Progress bars update in real-time:

```
Download Progress: 42%|████▍     | 267/630 [02:15<03:02, 1.99file/s]
```

**Information:**
- **42%**: Completion percentage
- **267/630**: Processed / Total files
- **02:15**: Elapsed time
- **03:02**: Estimated time remaining
- **1.99file/s**: Processing rate

### Checking Status During Run

Open another terminal:

```bash
# Check downloads
ls artifacts/tdocs/ | wc -l

# Check extractions
ls artifacts/extracted/ | wc -l

# Check conversions
ls artifacts/output/html/ | wc -l
```

## Handling Interruptions

### Ctrl+C (Keyboard Interrupt)

```bash
# Press Ctrl+C to stop
^C
KeyboardInterrupt

# Progress is saved
# Simply run again to resume
python download_tdocs.py
```

### Network Interruption

- Failed downloads are logged
- Partial files are removed
- Re-run script to retry

### System Crash

- Downloaded files are preserved
- Extracted directories are preserved
- Converted files are preserved
- Re-run script to continue

## Verifying Results

### Check File Counts

```bash
# Count downloaded ZIPs
ls artifacts/tdocs/ | wc -l
# Expected: ~630

# Count extracted directories
ls artifacts/extracted/ | wc -l
# Expected: ~630

# Count HTML files
ls artifacts/output/html/ | wc -l
# Expected: ~3257

# Count Markdown files
ls artifacts/output/markdown/ | wc -l
# Expected: ~3257
```

### Check Specific File

```bash
# Verify HTML file exists and has content
ls -lh artifacts/output/html/R1-2508300_proposal.html
# Should show file size

# View Markdown file
cat artifacts/output/markdown/R1-2508300_proposal.md
```

### Check for Failures

Review terminal output for `[FAIL]` messages:

```bash
# Re-run to see failures again
python download_tdocs.py 2>&1 | grep FAIL
```

---

**Navigation:**
- [← Quick Start](quick-start.md)
- [Documentation Home](../README.md)
- [→ Next: Output Files](output-files.md)

**Related:**
- [Multi-Processing](../features/multi-processing.md)
- [Skip Logic](../features/skip-logic.md)
- [Progress Tracking](../features/progress-tracking.md)
- [Error Handling](../features/error-handling.md)
