# Multi-Processing

[← Back to Features](../README.md#-features)

## Overview

The 3GPP TDoc Portal uses parallel processing to significantly speed up the download, extraction, and conversion pipeline. This document explains the multi-processing architecture and how to optimize it.

## Architecture

### ProcessPoolExecutor

The script uses Python's `concurrent.futures.ProcessPoolExecutor` for parallel processing:

```python
from concurrent.futures import ProcessPoolExecutor, as_completed

with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
    # Submit tasks
    futures = {executor.submit(worker_func, item): item for item in items}

    # Process results as they complete
    for future in as_completed(futures):
        result = future.result()
        process_result(result)
```

### Why Process Pool (Not Thread Pool)?

**Process Pool Benefits:**
- True parallel execution (bypasses Python GIL)
- Better for CPU-intensive tasks (document conversion)
- Process isolation (crash in one worker doesn't affect others)

**Thread Pool Limitations:**
- Python GIL prevents true parallelism for CPU-bound tasks
- Multiple threads compete for single CPU core
- Less effective for document conversion

## Three-Phase Parallel Processing

Each phase of the pipeline uses parallel processing:

### Phase 1: Download (Network-Bound)

```python
with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = {executor.submit(download_file_worker, filename): filename
              for filename in tdoc_files}

    for future in as_completed(futures):
        result = future.result()
        # Process download result
```

**Characteristics:**
- Network I/O bound
- Can benefit from higher MAX_WORKERS (e.g., 8-12)
- Limited by network bandwidth and server rate limits

### Phase 2: Extract (I/O-Bound)

```python
with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = {executor.submit(extract_file_worker, filename): filename
              for filename in zip_files}

    for future in as_completed(futures):
        result = future.result()
        # Process extraction result
```

**Characteristics:**
- Disk I/O bound
- Moderate benefit from parallelism
- Limited by disk speed (SSD vs HDD matters)

### Phase 3: Convert (CPU-Bound)

```python
with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = {executor.submit(convert_document_worker, doc_info): doc_info
              for doc_info in documents}

    for future in as_completed(futures):
        result = future.result()
        # Process conversion result
```

**Characteristics:**
- CPU bound (document parsing and layout analysis)
- Optimal MAX_WORKERS = CPU core count
- Memory intensive (each worker loads documents)

## Worker Function Design

All worker functions follow a consistent pattern:

### Worker Signature

```python
def worker_function(item) -> Dict[str, str]:
    """
    Worker function for parallel processing.

    Args:
        item: Item to process

    Returns:
        Dict with keys: filename, status, message
    """
    pass
```

### Return Format

```python
{
    'filename': str,   # Name of processed file
    'status': str,     # 'success', 'skip', 'fail'
    'message': str     # Status details
}
```

### Example Worker

```python
def download_file_worker(filename):
    """Worker function to download a single file."""
    filepath = os.path.join(DOWNLOAD_DIR, filename)

    # Skip logic
    if os.path.exists(filepath):
        return {
            'filename': filename,
            'status': 'skip',
            'message': 'Already exists'
        }

    try:
        # Download logic
        response = requests.get(url, stream=True)
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return {
            'filename': filename,
            'status': 'success',
            'message': f'{size_mb:.2f} MB'
        }

    except requests.RequestException as e:
        return {
            'filename': filename,
            'status': 'fail',
            'message': str(e)
        }
```

## Performance Tuning

### Configuring MAX_WORKERS

The `MAX_WORKERS` constant controls parallelism:

```python
MAX_WORKERS = 4  # Default
```

### Recommended Settings

**Based on CPU Cores:**
```python
import os

# Match CPU count
MAX_WORKERS = os.cpu_count()  # e.g., 8 for 8-core CPU

# Conservative (leave cores for system)
MAX_WORKERS = max(1, os.cpu_count() - 2)  # e.g., 6 for 8-core CPU
```

**Based on Task Type:**
```python
# Network-bound (downloads)
MAX_WORKERS = 8  # Can exceed CPU count

# CPU-bound (conversion)
MAX_WORKERS = os.cpu_count()  # Match CPU count

# I/O-bound (extraction)
MAX_WORKERS = 4  # Moderate parallelism
```

**Based on System Resources:**

| System | CPU Cores | RAM | Recommended MAX_WORKERS |
|--------|-----------|-----|------------------------|
| Laptop | 4 | 8 GB | 2-4 |
| Desktop | 8 | 16 GB | 6-8 |
| Workstation | 16 | 32 GB | 12-16 |
| Server | 32+ | 64+ GB | 16-24 |

### Performance Benchmarks

**Serial vs Parallel Processing** (630 files):

| Phase | Serial Time | Parallel (4 workers) | Speedup |
|-------|-------------|---------------------|---------|
| Download | ~30 min | ~8 min | 3.75x |
| Extract | ~15 min | ~4 min | 3.75x |
| Convert | ~120 min | ~35 min | 3.43x |
| **Total** | **~165 min** | **~47 min** | **3.51x** |

**Scaling with Workers** (conversion phase):

| Workers | Time | Speedup | Efficiency |
|---------|------|---------|------------|
| 1 | 120 min | 1.0x | 100% |
| 2 | 62 min | 1.94x | 97% |
| 4 | 35 min | 3.43x | 86% |
| 8 | 22 min | 5.45x | 68% |
| 16 | 18 min | 6.67x | 42% |

**Observations:**
- Diminishing returns after 8 workers
- Optimal for most systems: 4-8 workers
- Memory usage increases linearly with workers

### Memory Considerations

Each worker process consumes memory:

**Typical Memory Usage:**
- Base process: ~100 MB
- Document conversion worker: ~200-500 MB
- 4 workers: ~1-2 GB total
- 8 workers: ~2-4 GB total

**Memory Tuning:**
```python
# If running out of memory, reduce workers
MAX_WORKERS = 2  # Low memory systems

# High memory systems can use more workers
MAX_WORKERS = 16
```

## Progress Tracking

### Real-Time Progress Bars

Each phase displays a tqdm progress bar:

```python
with tqdm(total=len(items), desc="Phase Progress", unit="file") as pbar:
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(worker_func, item): item for item in items}

        for future in as_completed(futures):
            result = future.result()
            pbar.update(1)  # Update progress bar
            pbar.write(f"[{status}] {filename} - {message}")
```

### Progress Output

```
Download Progress: 42%|████▍     | 267/630 [02:15<03:02, 1.99file/s]
[OK] R1-2508300.zip - 2.45 MB
[OK] R1-2508301.zip - 1.87 MB
[SKIP] R1-2508302.zip - Already exists
[FAIL] R1-2508303.zip - Connection timeout
```

### Progress Metrics

- **Percentage**: Current completion percentage
- **Count**: Processed / Total files
- **Time**: Elapsed time and ETA
- **Rate**: Files processed per second

## Error Handling in Parallel Context

### Isolated Failures

Worker process failures don't stop the pipeline:

```python
try:
    result = future.result()
    if result['status'] == 'success':
        success_count += 1
    elif result['status'] == 'skip':
        skip_count += 1
    else:
        fail_count += 1
except Exception as e:
    # Worker process crashed
    fail_count += 1
    print(f"Worker failed: {e}")
```

### Graceful Degradation

- Failed downloads don't block extraction
- Failed extractions don't block conversion
- Failed conversions are logged and skipped
- Pipeline completes even with failures

## Best Practices

### DO:
- ✅ Use ProcessPoolExecutor for CPU-bound tasks
- ✅ Tune MAX_WORKERS based on system resources
- ✅ Return structured results from workers
- ✅ Handle errors in worker functions
- ✅ Use progress bars for user feedback

### DON'T:
- ❌ Don't share state between workers (use process-safe patterns)
- ❌ Don't set MAX_WORKERS too high (memory exhaustion)
- ❌ Don't use threads for CPU-bound tasks (GIL limitation)
- ❌ Don't ignore worker exceptions (log them)

## Advanced: Dynamic Worker Scaling

Future enhancement to adjust workers based on system load:

```python
import psutil

def get_optimal_workers():
    """Determine optimal worker count based on system resources."""
    cpu_count = os.cpu_count()
    cpu_percent = psutil.cpu_percent(interval=1)
    memory_percent = psutil.virtual_memory().percent

    # Scale down if system is under load
    if cpu_percent > 80 or memory_percent > 80:
        return max(2, cpu_count // 2)
    else:
        return cpu_count

MAX_WORKERS = get_optimal_workers()
```

---

**Navigation:**
- [← Features Overview](../README.md#features)
- [Documentation Home](../README.md)
- [→ Next: Skip Logic](skip-logic.md)

**Related:**
- [Configuration](../development/configuration.md)
- [Script Reference](../development/script-reference.md)
- [Progress Tracking](progress-tracking.md)
