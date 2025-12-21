# Quick Start Guide

[← Back to Usage](../README.md#-usage)

## Overview

Get up and running with the 3GPP TDoc Portal in just a few steps. This guide provides the fastest path to downloading, extracting, and converting 3GPP TDoc files.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Internet connection
- ~10-20 GB free disk space

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yhsung/3gpp-tdoc-portal.git
cd 3gpp-tdoc-portal
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**What Gets Installed:**
- `requests` - For downloading files
- `beautifulsoup4` - For web scraping
- `docling` - For document conversion
- `tqdm` - For progress bars

## Running the Pipeline

### Basic Usage

Simply run the script:

```bash
python download_tdocs.py
```

That's it! The script will:
1. ✅ Fetch list of TDoc files from 3GPP server (~630 files)
2. ✅ Download all ZIP files in parallel (4 workers)
3. ✅ Extract all downloaded files
4. ✅ Convert all documents to HTML and Markdown

### What You'll See

```
Fetching TDoc file list from 3GPP server...
Found 630 TDoc files

=== Phase 1: Download Files ===
Download Progress: 100%|██████████| 630/630 [05:23<00:00, 1.95file/s]

=== Phase 2: Extract Files ===
Extract Progress: 100%|██████████| 630/630 [03:45<00:00, 2.79file/s]

=== Phase 3: Convert Documents ===
Convert Progress: 100%|██████████| 3257/3257 [35:12<00:00, 1.54file/s]

=== Pipeline Complete ===
```

### Expected Duration

**First Run** (all files):
- Download: ~5-10 minutes (depends on network speed)
- Extract: ~3-5 minutes
- Convert: ~30-45 minutes (depends on CPU)
- **Total: ~40-60 minutes**

**Subsequent Runs** (with skip logic):
- Only processes new or failed files
- Can complete in seconds if nothing new

## Output Files

All files are saved in the `artifacts/` directory:

```
artifacts/
├── tdocs/          # Downloaded ZIP files
├── extracted/      # Extracted documents
└── output/
    ├── html/       # HTML converted files
    └── markdown/   # Markdown converted files
```

### Viewing Converted Files

**HTML Files:**
```bash
# Open in browser (macOS)
open artifacts/output/html/R1-2508300_proposal.html

# Or navigate in file explorer and double-click
```

**Markdown Files:**
```bash
# View in terminal
cat artifacts/output/markdown/R1-2508300_proposal.md

# Or open in text editor
```

### File Naming Pattern

Converted files follow this pattern:
```
{TDoc-ID}_{original-filename}.{html|md}
```

**Examples:**
- `R1-2508300_proposal.html`
- `R1-2508300_proposal.md`
- `R1-2508301_meeting_notes.html`
- `R1-2508301_meeting_notes.md`

## Resume Capability

### Interrupted Pipeline

If the script is interrupted (Ctrl+C, network failure, crash):

1. **Don't worry** - Progress is saved
2. **Just run again**:
   ```bash
   python download_tdocs.py
   ```
3. **Skip logic** automatically resumes from where it left off

### What Gets Skipped

- ✅ Downloaded files are skipped
- ✅ Extracted files are skipped
- ✅ Converted files are skipped
- ✅ Only new or failed files are processed

**Example Output:**
```
Download Progress: 100%|██████████| 630/630 [00:10<00:00, 63.5file/s]
Downloaded: 5, Skipped: 625, Failed: 0
```

## Incremental Updates

### Processing New Files

When new TDoc files are added to 3GPP server:

1. **Just run the script**:
   ```bash
   python download_tdocs.py
   ```

2. **Only new files are processed**:
   ```
   Downloaded: 10, Skipped: 630, Failed: 0
   Extracted: 10, Skipped: 630
   Converted: 45, Skipped: 3257, Failed: 0
   ```

3. **Fast incremental update** - completes in minutes, not hours

## Common Commands

### Full Reset

To start from scratch (delete all artifacts):

```bash
rm -rf artifacts/
python download_tdocs.py
```

### Retry Failed Downloads

```bash
# Failed files are automatically retried on next run
python download_tdocs.py
```

### View Summary Statistics

```bash
# Check how many files in each directory
ls artifacts/tdocs/ | wc -l         # Downloaded ZIPs
ls artifacts/extracted/ | wc -l      # Extracted TDocs
ls artifacts/output/html/ | wc -l    # HTML files
ls artifacts/output/markdown/ | wc -l # Markdown files
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'requests'"

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: "Permission denied"

**Solution:**
```bash
# Ensure you have write permissions in current directory
chmod +w .

# Or run in directory where you have permissions
cd ~/Documents
git clone https://github.com/yhsung/3gpp-tdoc-portal.git
cd 3gpp-tdoc-portal
python download_tdocs.py
```

### Issue: "Disk full"

**Solution:**
```bash
# Check available disk space
df -h

# Free up space or use external drive
# Change ARTIFACTS_DIR in download_tdocs.py to external drive path
```

### Issue: All conversions failing

**Solution:**
```bash
# Install LibreOffice for better conversion quality
# macOS:
brew install --cask libreoffice

# Ubuntu/Debian:
sudo apt-get install libreoffice

# Then re-run
python download_tdocs.py
```

### Issue: Script runs too slow

**Solution:**
```bash
# Increase parallel workers
# Edit download_tdocs.py:
# MAX_WORKERS = 8  # Increase from default 4

python download_tdocs.py
```

## Next Steps

After completing the quick start:

1. **Explore Output Files** - View HTML documents in browser
2. **Read Full Guide** - See [Running Pipeline](running-pipeline.md) for details
3. **Customize Settings** - See [Configuration](../development/configuration.md)
4. **Learn Features** - Check out [Features Documentation](../features/)

## Getting Help

- **Documentation**: Browse the [docs/](../README.md) folder
- **Issues**: Report problems on [GitHub Issues](https://github.com/yhsung/3gpp-tdoc-portal/issues)
- **Questions**: Open an issue with the "question" label

---

**Navigation:**
- [← Documentation Home](../README.md)
- [→ Next: Running Pipeline](running-pipeline.md)

**Related:**
- [Output Files Guide](output-files.md)
- [Getting Started](../development/getting-started.md)
- [Features Overview](../features/)
