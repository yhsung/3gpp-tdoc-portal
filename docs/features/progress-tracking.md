# Progress Tracking

[← Back to Features](../README.md#-features)

## Overview

The 3GPP TDoc Portal provides comprehensive real-time progress tracking throughout the download, extract, and convert pipeline. This document explains the progress monitoring system.

## Progress Bar System

### Library: tqdm

The script uses [tqdm](https://github.com/tqdm/tqdm) for progress visualization:

```python
from tqdm import tqdm

with tqdm(total=len(items), desc="Phase Progress", unit="file") as pbar:
    for item in items:
        process_item(item)
        pbar.update(1)  # Increment progress
```

### Why tqdm?

**Benefits:**
- Real-time visual feedback
- Automatic rate calculation
- Time estimates (elapsed and remaining)
- Smart terminal width detection
- Minimal performance overhead
- Thread-safe and process-safe

## Progress Display Format

### Standard Progress Bar

```
Download Progress: 42%|████▍     | 267/630 [02:15<03:02, 1.99file/s]
```

**Components:**

| Component | Example | Description |
|-----------|---------|-------------|
| Description | `Download Progress:` | Phase identifier |
| Percentage | `42%` | Completion percentage |
| Visual Bar | `████▍     ` | Visual progress indicator |
| Count | `267/630` | Processed / Total items |
| Elapsed Time | `[02:15<` | Time elapsed (mm:ss) |
| ETA | `<03:02` | Estimated time remaining |
| Rate | `1.99file/s]` | Processing rate |

### Status Messages

Below progress bar, individual file statuses:

```
[OK] R1-2508300.zip - 2.45 MB
[OK] R1-2508301.zip - 1.87 MB
[SKIP] R1-2508302.zip - Already exists
[FAIL] R1-2508303.zip - Connection timeout
```

**Status Indicators:**
- `[OK]` - Successfully processed
- `[SKIP]` - Skipped (already exists)
- `[FAIL]` - Processing failed

## Phase-Specific Progress

### Phase 1: Download Progress

```python
with tqdm(total=len(tdoc_files), desc="Download Progress", unit="file") as pbar:
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(download_file_worker, filename): filename
                  for filename in tdoc_files}

        for future in as_completed(futures):
            result = future.result()
            pbar.update(1)

            if result['status'] == 'success':
                pbar.write(f"[OK] {result['filename']} - {result['message']}")
            elif result['status'] == 'skip':
                pbar.write(f"[SKIP] {result['filename']} - {result['message']}")
            else:
                pbar.write(f"[FAIL] {result['filename']} - {result['message']}")
```

**Example Output:**
```
Download Progress: 100%|██████████| 630/630 [05:23<00:00, 1.95file/s]
[OK] R1-2508300.zip - 2.45 MB
[OK] R1-2508301.zip - 1.87 MB
[SKIP] R1-2508302.zip - Already exists
```

**Metrics:**
- **Total files**: 630
- **Processing rate**: 1.95 files/sec
- **Elapsed time**: 5:23
- **Status**: Success with file size, Skip, or Fail with error

### Phase 2: Extract Progress

```python
with tqdm(total=len(zip_files), desc="Extract Progress", unit="file") as pbar:
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(extract_file_worker, filename): filename
                  for filename in zip_files}

        for future in as_completed(futures):
            result = future.result()
            pbar.update(1)

            if result['status'] == 'success':
                pbar.write(f"[OK] {result['filename']} - {result['message']}")
            elif result['status'] == 'skip':
                pbar.write(f"[SKIP] {result['filename']} - {result['message']}")
```

**Example Output:**
```
Extract Progress: 100%|██████████| 630/630 [03:45<00:00, 2.79file/s]
[OK] R1-2508300.zip - Extracted 3 files
[OK] R1-2508301.zip - Extracted 5 files
[SKIP] R1-2508302.zip - Already extracted
```

**Metrics:**
- **Total files**: 630
- **Processing rate**: 2.79 files/sec
- **Elapsed time**: 3:45
- **Status**: Success with file count or Skip

### Phase 3: Convert Progress

```python
with tqdm(total=len(documents_to_convert), desc="Convert Progress", unit="file") as pbar:
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(convert_document_worker, doc_info): doc_info
                  for doc_info in documents_to_convert}

        for future in as_completed(futures):
            result = future.result()
            pbar.update(1)

            if result['status'] == 'success':
                pbar.write(f"[OK] {result['filename']} - {result['message']}")
            elif result['status'] == 'skip':
                pbar.write(f"[SKIP] {result['filename']} - {result['message']}")
            else:
                pbar.write(f"[FAIL] {result['filename']} - {result['message']}")
```

**Example Output:**
```
Convert Progress: 100%|██████████| 3257/3257 [35:12<00:00, 1.54file/s]
[OK] R1-2508300_proposal.docx - Converted successfully
[OK] R1-2508300_presentation.pptx - Converted successfully
[SKIP] R1-2508301_agenda.docx - Already converted
[FAIL] R1-2508302_corrupted.pdf - Conversion failed
```

**Metrics:**
- **Total documents**: 3257
- **Processing rate**: 1.54 files/sec
- **Elapsed time**: 35:12
- **Status**: Success, Skip, or Fail with error

## Summary Statistics

### After Each Phase

Summary displayed after phase completion:

**Download Summary:**
```
=== Download Summary ===
Successfully downloaded: 625 files
Skipped (already exists): 4 files
Failed: 1 files
```

**Extract Summary:**
```
=== Extract Summary ===
Successfully extracted: 629 ZIP files
Skipped (already extracted): 1 ZIP files
```

**Convert Summary:**
```
=== Convert Summary ===
Successfully converted: 3147 documents
Skipped (already converted): 98 documents
Failed: 12 documents
```

### Implementation

```python
# Track statistics
download_success = 0
download_skip = 0
download_fail = 0

# Process results
for future in as_completed(futures):
    result = future.result()

    if result['status'] == 'success':
        download_success += 1
    elif result['status'] == 'skip':
        download_skip += 1
    else:
        download_fail += 1

    pbar.update(1)

# Display summary
print(f"\n=== Download Summary ===")
print(f"Successfully downloaded: {download_success} files")
print(f"Skipped (already exists): {download_skip} files")
print(f"Failed: {download_fail} files")
```

## Complete Pipeline Output

### Full Run Example

```bash
$ python download_tdocs.py
```

**Output:**
```
Fetching TDoc file list from 3GPP server...
Found 630 TDoc files

=== Phase 1: Download Files ===
Download Progress: 100%|██████████| 630/630 [05:23<00:00, 1.95file/s]
[OK] R1-2508300.zip - 2.45 MB
[OK] R1-2508301.zip - 1.87 MB
[SKIP] R1-2508302.zip - Already exists
...

=== Download Summary ===
Successfully downloaded: 625 files
Skipped (already exists): 4 files
Failed: 1 files

=== Phase 2: Extract Files ===
Extract Progress: 100%|██████████| 630/630 [03:45<00:00, 2.79file/s]
[OK] R1-2508300.zip - Extracted 3 files
[OK] R1-2508301.zip - Extracted 5 files
[SKIP] R1-2508302.zip - Already extracted
...

=== Extract Summary ===
Successfully extracted: 629 ZIP files
Skipped (already extracted): 1 ZIP files

=== Phase 3: Convert Documents ===
Convert Progress: 100%|██████████| 3257/3257 [35:12<00:00, 1.54file/s]
[OK] R1-2508300_proposal.docx - Converted successfully
[OK] R1-2508300_presentation.pptx - Converted successfully
[SKIP] R1-2508301_agenda.docx - Already converted
[FAIL] R1-2508302_corrupted.pdf - Conversion failed: Invalid PDF
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

## Progress Bar Customization

### Custom Description

```python
with tqdm(total=len(items), desc="Custom Phase Name", unit="file") as pbar:
    # Process items
```

### Custom Unit

```python
# Download with MB unit
with tqdm(total=total_size_mb, desc="Download", unit="MB") as pbar:
    pbar.update(chunk_size_mb)

# Document count
with tqdm(total=doc_count, desc="Convert", unit="doc") as pbar:
    pbar.update(1)
```

### Disable Progress Bar

For scripting or logging:

```python
with tqdm(total=len(items), disable=True) as pbar:
    # No visual output
```

### Custom Format

```python
with tqdm(
    total=len(items),
    desc="Phase",
    unit="file",
    bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]'
) as pbar:
    # Custom format
```

## Performance Impact

### tqdm Overhead

**Minimal overhead:**
- Progress update: < 1ms
- Terminal write: < 5ms
- Total impact: < 0.1% of processing time

**Benchmark:**
```python
# Without tqdm: 35:10 total time
# With tqdm: 35:12 total time
# Overhead: 2 seconds (0.09%)
```

### Best Practices

**DO:**
- ✅ Use tqdm for long-running operations
- ✅ Update progress incrementally
- ✅ Use `pbar.write()` for status messages
- ✅ Display summary statistics

**DON'T:**
- ❌ Don't update progress in tight loops (< 10ms iterations)
- ❌ Don't use print() inside progress context (use `pbar.write()`)
- ❌ Don't update progress too frequently (causes flicker)

## Future Enhancements

### Planned Improvements

1. **File Logging:**
   ```python
   tqdm_logger = tqdm(total=len(items), file=open('progress.log', 'w'))
   ```

2. **Web Progress (WebSocket):**
   ```python
   # Send progress updates via WebSocket
   await websocket.send_json({
       'phase': 'download',
       'progress': progress_percent,
       'processed': count,
       'total': total
   })
   ```

3. **Nested Progress Bars:**
   ```python
   with tqdm(total=len(phases), desc="Overall") as main_pbar:
       for phase in phases:
           with tqdm(total=len(items), desc=phase) as phase_pbar:
               # Process phase items
   ```

4. **Rich Console Output:**
   ```python
   from rich.progress import Progress, BarColumn, TimeRemainingColumn

   with Progress() as progress:
       task = progress.add_task("Download", total=len(items))
       # Enhanced visual output
   ```

---

**Navigation:**
- [← Error Handling](error-handling.md)
- [Documentation Home](../README.md)
- [Features Overview](../README.md#features)

**Related:**
- [Multi-Processing](multi-processing.md)
- [Running Pipeline](../usage/running-pipeline.md)
- [Script Reference](../development/script-reference.md)
