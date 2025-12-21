# Skip Logic

[← Back to Features](../README.md#-features)

## Overview

The 3GPP TDoc Portal implements smart skip logic at each phase of the pipeline, enabling resume capability and preventing redundant processing. This document explains how skip logic works and why it's essential.

## Purpose

### Why Skip Logic Matters

**Problem Without Skip Logic:**
- Network interruptions require full restart
- Power failures lose all progress
- Script errors force complete re-download
- Duplicate processing wastes time and resources

**Solution With Skip Logic:**
- Resume from interruption point
- Skip already processed files
- Incremental processing of new files
- Idempotent pipeline execution

### Benefits

1. **Resume Capability** - Continue after interruption
2. **Incremental Updates** - Process only new files
3. **Development Efficiency** - Test without re-downloading
4. **Resource Conservation** - Avoid redundant work
5. **Fault Tolerance** - Graceful handling of partial failures

## Three-Phase Skip Logic

Skip logic is implemented at each phase:

```
Phase 1: Download → Skip if ZIP exists
Phase 2: Extract → Skip if directory exists and non-empty
Phase 3: Convert → Skip if both HTML and Markdown exist
```

## Phase 1: Download Skip Logic

### Implementation

```python
def download_file_worker(filename):
    """Worker function to download a single file."""
    filepath = os.path.join(DOWNLOAD_DIR, filename)

    # Skip if file already exists
    if os.path.exists(filepath):
        return {
            'filename': filename,
            'status': 'skip',
            'message': 'Already exists'
        }

    # Proceed with download...
```

### Skip Condition

**Skip if:**
- File exists at `artifacts/tdocs/{filename}`

**Don't skip if:**
- File doesn't exist
- File is being downloaded for the first time

### File Check

```python
filepath = os.path.join(DOWNLOAD_DIR, filename)
# Example: artifacts/tdocs/R1-2508300.zip

if os.path.exists(filepath):
    # File exists → Skip
else:
    # File doesn't exist → Download
```

### Partial Download Handling

If download fails mid-stream, partial file is removed:

```python
try:
    # Download logic
    with open(filepath, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
except requests.RequestException as e:
    # Remove partial file
    if os.path.exists(filepath):
        os.remove(filepath)
    return {'filename': filename, 'status': 'fail', 'message': str(e)}
```

**Why Remove Partial Files?**
- Corrupted files cause extraction errors
- Incomplete downloads should be re-attempted
- Prevents false skip on next run

## Phase 2: Extract Skip Logic

### Implementation

```python
def extract_file_worker(filename):
    """Worker function to extract a single file."""
    tdoc_id = filename.replace('.zip', '')
    extract_path = os.path.join(EXTRACT_DIR, tdoc_id)

    # Skip if already extracted
    if os.path.exists(extract_path) and os.listdir(extract_path):
        return {
            'filename': filename,
            'status': 'skip',
            'message': 'Already extracted'
        }

    # Proceed with extraction...
```

### Skip Condition

**Skip if:**
- Directory exists at `artifacts/extracted/{tdoc_id}/`
- **AND** directory is non-empty

**Don't skip if:**
- Directory doesn't exist
- Directory exists but is empty (failed extraction)

### Directory Check

```python
extract_path = os.path.join(EXTRACT_DIR, tdoc_id)
# Example: artifacts/extracted/R1-2508300/

if os.path.exists(extract_path) and os.listdir(extract_path):
    # Directory exists AND contains files → Skip
else:
    # Directory doesn't exist OR is empty → Extract
```

### Why Check for Non-Empty?

Empty directories indicate failed extraction:

```python
# Previous extraction attempt failed, left empty directory
if os.path.exists(extract_path) and not os.listdir(extract_path):
    # Empty directory → Re-extract
```

**Scenarios:**
- Corrupted ZIP file → Extraction fails, creates empty dir
- Interrupted extraction → Partial extraction, may be empty
- Permission issues → Directory created but no files written

## Phase 3: Convert Skip Logic

### Implementation

```python
def convert_document_worker(doc_info):
    """Worker function to convert a single document."""
    tdoc_id, doc_filename, doc_path = doc_info

    base_name = os.path.splitext(doc_filename)[0]
    html_filename = f"{tdoc_id}_{base_name}.html"
    md_filename = f"{tdoc_id}_{base_name}.md"

    html_output_path = os.path.join(OUTPUT_DIR, "html", html_filename)
    md_output_path = os.path.join(OUTPUT_DIR, "markdown", md_filename)

    # Skip if both HTML and Markdown already exist
    if os.path.exists(html_output_path) and os.path.exists(md_output_path):
        return {
            'filename': doc_filename,
            'status': 'skip',
            'message': 'Already converted'
        }

    # Proceed with conversion...
```

### Skip Condition

**Skip if:**
- HTML file exists at `artifacts/output/html/{tdoc_id}_{filename}.html`
- **AND** Markdown file exists at `artifacts/output/markdown/{tdoc_id}_{filename}.md`

**Don't skip if:**
- Neither file exists
- Only HTML exists (Markdown missing)
- Only Markdown exists (HTML missing)
- Both missing

### Both Formats Required

Why require both HTML **and** Markdown?

```python
if os.path.exists(html_output_path) and os.path.exists(md_output_path):
    # Both formats exist → Skip
else:
    # One or both missing → Reconvert to ensure both
```

**Reasoning:**
- Conversion generates both formats in single pass
- If only one exists, previous conversion was incomplete
- Reconverting ensures both formats available
- Small overhead to regenerate both vs complex partial logic

### Output File Paths

```python
# Input: artifacts/extracted/R1-2508300/proposal.docx
tdoc_id = "R1-2508300"
doc_filename = "proposal.docx"
base_name = "proposal"

# Output files:
html_output = "artifacts/output/html/R1-2508300_proposal.html"
md_output = "artifacts/output/markdown/R1-2508300_proposal.md"
```

## Resume Scenarios

### Scenario 1: Network Interruption During Download

**Situation:**
- Downloaded 200/630 files
- Network connection lost
- Script terminated

**Resume Process:**
1. Run script again
2. Phase 1 (Download):
   - Skip 200 already downloaded files
   - Download remaining 430 files
3. Phase 2 (Extract):
   - Process all 630 files (200 skip, 430 new)
4. Phase 3 (Convert):
   - Process all documents

**Output:**
```
Download Progress: 100%|██████████| 630/630 [03:15<00:00, 3.23file/s]
Downloaded: 430, Skipped: 200, Failed: 0
```

### Scenario 2: Disk Full During Extraction

**Situation:**
- All files downloaded (630)
- Extracted 150 files
- Disk full, script crashed

**Resume Process:**
1. Free up disk space
2. Run script again
3. Phase 1 (Download):
   - Skip all 630 files (already downloaded)
4. Phase 2 (Extract):
   - Skip 150 already extracted
   - Extract remaining 480 files
5. Phase 3 (Convert):
   - Process all documents

### Scenario 3: Conversion Error for Specific File

**Situation:**
- Downloaded and extracted all files
- Converting documents
- Conversion fails for corrupted document
- Script continues

**Resume Process:**
1. Fix corrupted file (if possible)
2. Run script again
3. Phase 1-2:
   - Skip all (already processed)
4. Phase 3 (Convert):
   - Skip successfully converted documents
   - Retry failed document
   - Continue with remaining

## Incremental Updates

### Processing New Files Only

**Scenario:** New TDoc files added to 3GPP server

**Before:**
- 630 files processed
- All in `artifacts/`

**After 3GPP Update:**
- 10 new files on server
- Total: 640 files

**Run Script:**
```
Download Progress: 100%|██████████| 640/640 [00:30<00:00, 21.3file/s]
Downloaded: 10, Skipped: 630, Failed: 0

Extract Progress: 100%|██████████| 640/640 [00:15<00:00, 42.7file/s]
Extracted: 10, Skipped: 630

Convert Progress: 100%|██████████| 65/65 [02:30<00:00, 0.43file/s]
Converted: 35, Skipped: 30, Failed: 0
```

**Result:**
- Only 10 new files downloaded
- Only 10 new files extracted
- Only new documents converted
- Total time: ~3 minutes (vs hours for full run)

## Manual Skip Control

### Force Re-download

To force re-download of specific file:

```bash
# Remove downloaded file
rm artifacts/tdocs/R1-2508300.zip

# Run script - will re-download this file
python download_tdocs.py
```

### Force Re-extraction

```bash
# Remove extracted directory
rm -rf artifacts/extracted/R1-2508300/

# Run script - will re-extract this file
python download_tdocs.py
```

### Force Re-conversion

```bash
# Remove converted files
rm artifacts/output/html/R1-2508300_*.html
rm artifacts/output/markdown/R1-2508300_*.md

# Run script - will re-convert documents from this TDoc
python download_tdocs.py
```

### Full Reset

```bash
# Remove all artifacts
rm -rf artifacts/

# Run script - full pipeline from scratch
python download_tdocs.py
```

## Best Practices

### DO:
- ✅ Trust skip logic for incremental processing
- ✅ Run script multiple times without worry
- ✅ Use partial cleanup to reprocess specific phases
- ✅ Let script handle resume automatically

### DON'T:
- ❌ Don't manually modify artifact files
- ❌ Don't delete partial directories without cleanup
- ❌ Don't assume partial files are valid
- ❌ Don't bypass skip logic without good reason

## Troubleshooting Skip Logic

### Issue 1: File Skipped But Corrupted

**Problem:** Downloaded file is corrupted but skip logic prevents re-download

**Solution:**
```bash
# Remove corrupted file
rm artifacts/tdocs/R1-2508300.zip

# Run script to re-download
python download_tdocs.py
```

### Issue 2: Empty Extraction Directory

**Problem:** Extraction failed, left empty directory

**Solution:**
Skip logic handles this automatically:
```python
# Empty directory triggers re-extraction
if os.path.exists(extract_path) and os.listdir(extract_path):
    # Skip only if non-empty
```

### Issue 3: Only HTML Exists, No Markdown

**Problem:** Previous conversion incomplete, only HTML generated

**Solution:**
Skip logic handles this automatically:
```python
# Reconverts if either file missing
if os.path.exists(html_output_path) and os.path.exists(md_output_path):
    # Skip only if BOTH exist
```

---

**Navigation:**
- [← Multi-Processing](multi-processing.md)
- [Documentation Home](../README.md)
- [→ Next: Error Handling](error-handling.md)

**Related:**
- [Running Pipeline](../usage/running-pipeline.md)
- [Script Reference](../development/script-reference.md)
- [Artifacts Guide](../architecture/artifacts.md)
