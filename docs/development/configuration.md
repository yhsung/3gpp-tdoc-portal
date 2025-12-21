# Configuration

[← Back to Development](../README.md#-development)

## Overview

The 3GPP TDoc Portal script can be customized through configuration constants in `download_tdocs.py`. This guide explains all available configuration options.

## Configuration Constants

All configuration is done through constants at the top of `download_tdocs.py`:

```python
# Configuration
BASE_URL = "https://www.3gpp.org/ftp/meetings_3gpp_sync/RAN1/Docs/"
MAX_WORKERS = 4
ARTIFACTS_DIR = "artifacts"
DOWNLOAD_DIR = "artifacts/tdocs"
EXTRACT_DIR = "artifacts/extracted"
OUTPUT_DIR = "artifacts/output"
```

## Base URL Configuration

### `BASE_URL`

**Default:** `"https://www.3gpp.org/ftp/meetings_3gpp_sync/RAN1/Docs/"`

**Purpose:** URL of the 3GPP directory to scrape for TDoc files

**Usage:**
```python
BASE_URL = "https://www.3gpp.org/ftp/meetings_3gpp_sync/RAN1/Docs/"
```

**Customization Examples:**

**Different RAN Group:**
```python
# RAN2 documents
BASE_URL = "https://www.3gpp.org/ftp/meetings_3gpp_sync/RAN2/Docs/"

# RAN3 documents
BASE_URL = "https://www.3gpp.org/ftp/meetings_3gpp_sync/RAN3/Docs/"
```

**Specific Meeting:**
```python
# RAN1 Meeting #112
BASE_URL = "https://www.3gpp.org/ftp/tsg_ran/WG1_RL1/TSGR1_112/Docs/"
```

**Notes:**
- URL must be a valid 3GPP FTP directory
- Must contain files matching pattern `R1-XXXXXXX.zip`
- Script uses web scraping to extract file links

## Performance Configuration

### `MAX_WORKERS`

**Default:** `4`

**Purpose:** Number of parallel worker processes for download, extraction, and conversion

**Usage:**
```python
MAX_WORKERS = 4
```

**Recommended Settings:**

**CPU-Bound (Conversion Phase):**
```python
import os
MAX_WORKERS = os.cpu_count()  # Match CPU core count
```

**Network-Bound (Download Phase):**
```python
MAX_WORKERS = 8  # Can exceed CPU count
```

**Conservative (Respect Server Limits):**
```python
MAX_WORKERS = 2  # Reduce load on 3GPP server
```

**Performance Testing:**
```python
MAX_WORKERS = 1  # Disable parallel processing
```

**Impact:**
- **Higher values**: Faster processing, more resource usage
- **Lower values**: Slower processing, less resource usage
- **Sweet spot**: 4-8 workers for most systems

**Tuning Guidelines:**
| System | Recommended MAX_WORKERS |
|--------|------------------------|
| 4-core laptop | 4 |
| 8-core desktop | 6-8 |
| High-end workstation | 8-12 |
| Server | 12-16 |

## Directory Configuration

### `ARTIFACTS_DIR`

**Default:** `"artifacts"`

**Purpose:** Base directory for all generated files

**Usage:**
```python
ARTIFACTS_DIR = "artifacts"
```

**Customization Examples:**

**Absolute Path:**
```python
ARTIFACTS_DIR = "/data/3gpp-tdocs"
```

**User Home Directory:**
```python
import os
ARTIFACTS_DIR = os.path.expanduser("~/3gpp-data")
```

**Network Drive:**
```python
ARTIFACTS_DIR = "/mnt/network/3gpp-tdocs"
```

---

### `DOWNLOAD_DIR`

**Default:** `"artifacts/tdocs"`

**Purpose:** Storage location for downloaded TDoc ZIP files

**Usage:**
```python
DOWNLOAD_DIR = "artifacts/tdocs"
```

**Customization:**
```python
# Absolute path
DOWNLOAD_DIR = "/data/3gpp-tdocs/downloads"

# Relative to ARTIFACTS_DIR
DOWNLOAD_DIR = os.path.join(ARTIFACTS_DIR, "tdocs")
```

**Storage Requirements:**
- Approximately 2-5 GB for ~630 files
- Must have write permissions

---

### `EXTRACT_DIR`

**Default:** `"artifacts/extracted"`

**Purpose:** Storage location for extracted document contents

**Usage:**
```python
EXTRACT_DIR = "artifacts/extracted"
```

**Customization:**
```python
# Absolute path
EXTRACT_DIR = "/data/3gpp-tdocs/extracted"

# Relative to ARTIFACTS_DIR
EXTRACT_DIR = os.path.join(ARTIFACTS_DIR, "extracted")
```

**Storage Requirements:**
- Approximately 5-10 GB (expanded from ZIPs)
- One subdirectory per TDoc

---

### `OUTPUT_DIR`

**Default:** `"artifacts/output"`

**Purpose:** Storage location for converted HTML and Markdown files

**Usage:**
```python
OUTPUT_DIR = "artifacts/output"
```

**Structure:**
- `OUTPUT_DIR/html/` - HTML conversions
- `OUTPUT_DIR/markdown/` - Markdown conversions

**Customization:**
```python
# Absolute path
OUTPUT_DIR = "/data/3gpp-tdocs/output"

# Relative to ARTIFACTS_DIR
OUTPUT_DIR = os.path.join(ARTIFACTS_DIR, "output")
```

**Storage Requirements:**
- Approximately 3-6 GB for HTML + Markdown
- Both formats generated for each document

## Advanced Configuration

### Custom File Patterns

To change the TDoc file pattern, modify the regex in `fetch_document_list()`:

```python
def fetch_document_list(url):
    # Default: R1-XXXXXXX.zip
    tdoc_pattern = r"(R1-\d{7}\.zip)$"

    # Custom: R2-XXXXXXX.zip (RAN2)
    tdoc_pattern = r"(R2-\d{7}\.zip)$"

    # Custom: Any RAN group
    tdoc_pattern = r"(R\d-\d{7}\.zip)$"
```

### Supported File Types

To modify supported document types for conversion, edit `main()`:

```python
# Default supported extensions
SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.pptx', '.ppt', '.xlsx', '.xls'}

# In main() function:
if doc_filename.lower().endswith(tuple(SUPPORTED_EXTENSIONS)):
    documents_to_convert.append((tdoc_id, doc_filename, doc_path))
```

### Request Timeout

To modify download timeout, add to `download_file_worker()`:

```python
def download_file_worker(filename):
    # Default timeout (requests library default)
    response = requests.get(url, stream=True)

    # Custom timeout (30 seconds)
    response = requests.get(url, stream=True, timeout=30)
```

## Configuration File (Future)

For easier configuration management, consider externalizing to a config file:

**config.ini:**
```ini
[paths]
artifacts_dir = artifacts
download_dir = artifacts/tdocs
extract_dir = artifacts/extracted
output_dir = artifacts/output

[processing]
max_workers = 4

[source]
base_url = https://www.3gpp.org/ftp/meetings_3gpp_sync/RAN1/Docs/
```

**Load with ConfigParser:**
```python
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

BASE_URL = config['source']['base_url']
MAX_WORKERS = config.getint('processing', 'max_workers')
```

## Environment Variables

For containerized deployments, use environment variables:

```python
import os

BASE_URL = os.getenv('TDOC_BASE_URL', 'https://www.3gpp.org/ftp/meetings_3gpp_sync/RAN1/Docs/')
MAX_WORKERS = int(os.getenv('TDOC_MAX_WORKERS', '4'))
ARTIFACTS_DIR = os.getenv('TDOC_ARTIFACTS_DIR', 'artifacts')
```

**Usage:**
```bash
export TDOC_MAX_WORKERS=8
export TDOC_ARTIFACTS_DIR=/data/tdocs
python download_tdocs.py
```

## Best Practices

1. **Use Absolute Paths for Production**: Avoid relative paths in production environments
2. **Set MAX_WORKERS Based on System**: Profile and tune based on your hardware
3. **Respect Server Limits**: Don't set MAX_WORKERS too high for downloads
4. **Plan Storage**: Ensure sufficient disk space (~10-20 GB total)
5. **Use Configuration Files**: Externalize config for easier management
6. **Version Control**: Don't commit local configuration changes

---

**Navigation:**
- [← Script Reference](script-reference.md)
- [Documentation Home](../README.md)
- [→ Next: Contributing](contributing.md)

**Related:**
- [Getting Started](getting-started.md)
- [Multi-Processing Feature](../features/multi-processing.md)
- [Directory Structure](../architecture/directory-structure.md)
