# Error Handling

[← Back to Features](../README.md#-features)

## Overview

The 3GPP TDoc Portal implements comprehensive error handling to ensure the pipeline continues even when individual files fail. This document explains error handling strategies across all phases.

## Design Philosophy

### Fail-Safe Principles

1. **Isolate Failures** - One file failure doesn't stop the pipeline
2. **Log Everything** - All errors are captured and reported
3. **Clean Up Partial Work** - Remove corrupted partial files
4. **Provide Feedback** - User sees what succeeded and what failed
5. **Enable Retry** - Failed files can be retried on next run

### Error Handling Goals

- ✅ Complete pipeline despite individual failures
- ✅ Prevent data corruption from partial operations
- ✅ Provide clear error messages
- ✅ Enable debugging and troubleshooting
- ✅ Support resume after fixing issues

## Phase 1: Download Error Handling

### Network Errors

**Common Network Errors:**
- Connection timeout
- Connection refused
- DNS resolution failure
- Server unavailable (503)
- Network unreachable

**Implementation:**

```python
def download_file_worker(filename):
    """Worker function to download a single file."""
    filepath = os.path.join(DOWNLOAD_DIR, filename)
    url = BASE_URL + filename

    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()  # Raise exception for HTTP errors

        # Download file
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        file_size = os.path.getsize(filepath)
        size_mb = file_size / (1024 * 1024)

        return {
            'filename': filename,
            'status': 'success',
            'message': f'{size_mb:.2f} MB'
        }

    except requests.RequestException as e:
        # Remove partial file if download failed
        if os.path.exists(filepath):
            os.remove(filepath)

        return {
            'filename': filename,
            'status': 'fail',
            'message': str(e)
        }
```

**Error Response:**
```python
{
    'filename': 'R1-2508300.zip',
    'status': 'fail',
    'message': 'HTTPSConnectionPool(host=\'www.3gpp.org\', port=443): Read timed out.'
}
```

### HTTP Status Errors

**HTTP Error Codes:**
- 404 Not Found - File doesn't exist
- 403 Forbidden - Access denied
- 500 Internal Server Error
- 503 Service Unavailable

**Handling:**
```python
response = requests.get(url, stream=True)
response.raise_for_status()  # Raises HTTPError for 4xx/5xx codes
```

**Error Message:**
```
[FAIL] R1-2508300.zip - 404 Client Error: Not Found for url: ...
```

### Partial File Cleanup

**Why Clean Up Partial Files?**

Problem without cleanup:
```
1. Download starts
2. Network fails mid-download
3. Partial file remains (e.g., 50% complete)
4. Next run skips file (exists check passes)
5. Extraction fails (corrupted ZIP)
```

Solution with cleanup:
```python
except requests.RequestException as e:
    # Remove partial file
    if os.path.exists(filepath):
        os.remove(filepath)
```

**Result:**
- Partial files are removed
- Skip logic won't trigger on corrupted files
- Next run will retry download

## Phase 2: Extract Error Handling

### ZIP File Errors

**Common ZIP Errors:**
- Corrupted ZIP file
- Invalid ZIP format
- Password-protected ZIP
- Disk space exhausted
- Permission denied

**Implementation:**

```python
def extract_file_worker(filename):
    """Worker function to extract a single file."""
    zip_path = os.path.join(DOWNLOAD_DIR, filename)
    tdoc_id = filename.replace('.zip', '')
    extract_path = os.path.join(EXTRACT_DIR, tdoc_id)

    try:
        # Create extraction directory
        os.makedirs(extract_path, exist_ok=True)

        # Extract ZIP file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)

        # Count extracted files
        file_count = sum(len(files) for _, _, files in os.walk(extract_path))

        return {
            'filename': filename,
            'status': 'success',
            'message': f'Extracted {file_count} files'
        }

    except zipfile.BadZipFile:
        return {
            'filename': filename,
            'status': 'fail',
            'message': 'Corrupted ZIP file'
        }

    except Exception as e:
        return {
            'filename': filename,
            'status': 'fail',
            'message': str(e)
        }
```

**Error Types:**

**Corrupted ZIP:**
```python
except zipfile.BadZipFile:
    return {'filename': filename, 'status': 'fail', 'message': 'Corrupted ZIP file'}
```

**Disk Full:**
```python
except OSError as e:
    if e.errno == 28:  # No space left on device
        return {'filename': filename, 'status': 'fail', 'message': 'Disk full'}
```

**Permission Denied:**
```python
except PermissionError:
    return {'filename': filename, 'status': 'fail', 'message': 'Permission denied'}
```

### Extraction Cleanup

**Empty Directory Handling:**

Skip logic handles empty directories automatically:
```python
# Skip only if directory exists AND is non-empty
if os.path.exists(extract_path) and os.listdir(extract_path):
    return {'filename': filename, 'status': 'skip', 'message': 'Already extracted'}
```

**Benefits:**
- Failed extraction leaves empty directory
- Next run will retry extraction (skip logic doesn't trigger)
- No manual cleanup needed

## Phase 3: Convert Error Handling

### Conversion Errors

**Common Conversion Errors:**
- Unsupported file format
- Corrupted document
- Missing dependencies (LibreOffice)
- Memory exhaustion
- Document parsing errors

**Implementation:**

```python
def convert_document_worker(doc_info):
    """Worker function to convert a single document."""
    tdoc_id, doc_filename, doc_path = doc_info

    try:
        # Initialize converter
        converter = DocumentConverter()

        # Convert document
        result = converter.convert(doc_path)

        # Export to HTML
        html_output_path = os.path.join(OUTPUT_DIR, "html", f"{tdoc_id}_{base_name}.html")
        with open(html_output_path, 'w', encoding='utf-8') as f:
            f.write(result.document.export_to_html())

        # Export to Markdown
        md_output_path = os.path.join(OUTPUT_DIR, "markdown", f"{tdoc_id}_{base_name}.md")
        with open(md_output_path, 'w', encoding='utf-8') as f:
            f.write(result.document.export_to_markdown())

        return {
            'filename': doc_filename,
            'status': 'success',
            'message': 'Converted successfully'
        }

    except Exception as e:
        return {
            'filename': doc_filename,
            'status': 'fail',
            'message': f'Conversion failed: {str(e)}'
        }
```

**Error Types:**

**Unsupported Format:**
```
[FAIL] document.xyz - Conversion failed: Unsupported file type
```

**Corrupted Document:**
```
[FAIL] proposal.docx - Conversion failed: File is corrupted or invalid
```

**LibreOffice Warning:**
```
[WARN] presentation.pptx - LibreOffice DrawingML elements not supported
[OK] presentation.pptx - Converted successfully (with warnings)
```

### Partial Conversion Handling

**Problem Scenario:**
1. HTML conversion succeeds
2. Markdown conversion fails
3. Only HTML file exists

**Solution:**

Skip logic requires both files:
```python
# Skip only if BOTH HTML and Markdown exist
if os.path.exists(html_output_path) and os.path.exists(md_output_path):
    return {'filename': doc_filename, 'status': 'skip', 'message': 'Already converted'}
```

**Retry Behavior:**
- Next run will retry conversion (skip logic doesn't trigger)
- Both HTML and Markdown will be regenerated
- Ensures complete conversion

## Error Reporting

### Real-Time Feedback

Progress output shows errors as they occur:

```
Convert Progress: 45%|████▌     | 285/630 [08:12<09:30, 0.61file/s]
[OK] R1-2508300_proposal.docx - Converted successfully
[OK] R1-2508301_presentation.pptx - Converted successfully
[FAIL] R1-2508302_corrupted.pdf - Conversion failed: Invalid PDF
[SKIP] R1-2508303_agenda.docx - Already converted
```

### Summary Statistics

Each phase provides summary statistics:

```
=== Download Summary ===
Successfully downloaded: 625 files
Skipped (already exists): 4 files
Failed: 1 files

=== Extract Summary ===
Successfully extracted: 629 ZIP files
Skipped (already extracted): 1 ZIP files

=== Convert Summary ===
Successfully converted: 3147 documents
Skipped (already converted): 98 documents
Failed: 12 documents
```

### Error Details

Failed operations include error messages:

```python
# Download failure
[FAIL] R1-2508300.zip - Connection timeout after 30s

# Extract failure
[FAIL] R1-2508301.zip - Corrupted ZIP file

# Convert failure
[FAIL] proposal.docx - Conversion failed: Memory error
```

## Retry Strategies

### Automatic Retry (Next Run)

Simply run the script again:
```bash
python download_tdocs.py
```

**What Happens:**
- Skip logic skips successful files
- Failed files are retried
- New summary shows only retried results

**Example:**
```
First Run:
Downloaded: 625, Skipped: 0, Failed: 5

Second Run (retry):
Downloaded: 4, Skipped: 625, Failed: 1

Third Run (final retry):
Downloaded: 1, Skipped: 629, Failed: 0
```

### Manual Intervention

**Fix and Retry:**

1. **Identify Problem:**
   ```
   [FAIL] R1-2508300.zip - 404 Not Found
   ```

2. **Check Issue:**
   - File doesn't exist on server
   - URL changed
   - Access restrictions

3. **Manual Fix:**
   - Download manually
   - Place in `artifacts/tdocs/`
   - Or skip this file

4. **Retry:**
   ```bash
   python download_tdocs.py
   ```

### Partial Reset

**Reset specific phase:**

```bash
# Retry all downloads
rm -rf artifacts/tdocs/
python download_tdocs.py

# Retry specific file extraction
rm -rf artifacts/extracted/R1-2508300/
python download_tdocs.py

# Retry specific file conversion
rm artifacts/output/html/R1-2508300_*.html
rm artifacts/output/markdown/R1-2508300_*.md
python download_tdocs.py
```

## Logging

### Console Output

All errors are logged to console:
```
[FAIL] R1-2508300.zip - Connection timeout
[FAIL] R1-2508301.zip - 404 Not Found
[FAIL] proposal.docx - Conversion failed: Invalid format
```

### Future: File Logging

Planned enhancement for persistent logging:

```python
import logging

# Configure logging
logging.basicConfig(
    filename='artifacts/pipeline.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Log errors
logging.error(f"Download failed: {filename} - {error_message}")
logging.warning(f"Conversion warning: {doc_filename} - {warning}")
logging.info(f"Successfully processed: {filename}")
```

## Troubleshooting

### Common Issues

**Issue 1: All Downloads Failing**

**Symptoms:**
```
Downloaded: 0, Skipped: 0, Failed: 630
```

**Possible Causes:**
- Network disconnected
- 3GPP server down
- Firewall blocking requests

**Solution:**
- Check internet connection
- Verify BASE_URL is accessible
- Check firewall settings

**Issue 2: Specific File Always Fails**

**Symptoms:**
```
[FAIL] R1-2508300.zip - Corrupted ZIP file
```

**Possible Causes:**
- File actually corrupted on server
- Download interrupted
- Partial file not cleaned up

**Solution:**
```bash
# Force re-download
rm artifacts/tdocs/R1-2508300.zip
python download_tdocs.py
```

**Issue 3: All Conversions Failing**

**Symptoms:**
```
Converted: 0, Skipped: 0, Failed: 3257
```

**Possible Causes:**
- Docling not installed
- LibreOffice missing
- Memory exhausted

**Solution:**
```bash
# Reinstall docling
pip install --upgrade docling

# Install LibreOffice (macOS)
brew install --cask libreoffice

# Reduce MAX_WORKERS to save memory
# Edit download_tdocs.py: MAX_WORKERS = 2
```

---

**Navigation:**
- [← Skip Logic](skip-logic.md)
- [Documentation Home](../README.md)
- [→ Next: Progress Tracking](progress-tracking.md)

**Related:**
- [Multi-Processing](multi-processing.md)
- [Running Pipeline](../usage/running-pipeline.md)
- [Script Reference](../development/script-reference.md)
