# Getting Started

[← Back to Development](../README.md#-development)

## Overview

This guide will help you set up your development environment and get started with the 3GPP TDoc Portal project.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** - Required for running the script
- **pip** - Python package installer
- **Git** - Version control (for cloning the repository)
- **LibreOffice** (optional) - For better document conversion quality

### Checking Prerequisites

```bash
# Check Python version
python --version  # Should be 3.8 or higher

# Check pip
pip --version

# Check Git
git --version
```

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yhsung/3gpp-tdoc-portal.git
cd 3gpp-tdoc-portal
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Dependencies Explained

### Core Dependencies

**requests>=2.31.0**
- HTTP library for downloading files from 3GPP server
- Handles retries, timeouts, and connection management

**beautifulsoup4>=4.12.0**
- HTML parsing library for web scraping
- Used to extract TDoc file links from 3GPP directory listing

**docling>=1.0.0**
- Document conversion library from IBM Research
- Converts PDF, DOCX, PPTX, XLSX to HTML and Markdown
- Preserves layout and formatting

**tqdm>=4.66.0**
- Progress bar library
- Provides real-time feedback during download/extract/convert phases

### Optional: LibreOffice Installation

LibreOffice improves conversion quality for Office documents (DOCX, PPTX, XLSX).

**macOS:**
```bash
brew install --cask libreoffice
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install libreoffice
```

**Windows:**
Download from [libreoffice.org](https://www.libreoffice.org/)

## Verification

### Test Your Installation

```bash
# Run the script with --help (when available)
python download_tdocs.py

# The script should start and display progress bars
```

### Expected Directory Structure

After installation, your directory should look like:

```
3gpp-tdoc-portal/
├── download_tdocs.py
├── requirements.txt
├── README.md
├── FOLDER_SUMMARY.md
├── docs/
├── specs/
└── venv/  (if using virtual environment)
```

### First Run

On first run, the script will:
1. Create the `artifacts/` directory structure
2. Begin downloading TDoc files
3. Extract ZIP archives
4. Convert documents to HTML and Markdown

**Note:** The complete pipeline can take several hours depending on:
- Network speed
- Number of files to process (~630+ files)
- System resources

## Common Issues

### Issue 1: Python Version Too Old

**Error:** `SyntaxError` or compatibility issues

**Solution:**
```bash
# Check Python version
python --version

# If less than 3.8, install newer version
# macOS:
brew install python@3.11

# Ubuntu:
sudo apt-get install python3.11
```

### Issue 2: Permission Denied

**Error:** `PermissionError` when creating directories

**Solution:**
```bash
# Ensure you have write permissions
chmod +w .

# Or run in a directory where you have permissions
```

### Issue 3: Network Timeout

**Error:** `requests.exceptions.ConnectionError`

**Solution:**
- Check internet connection
- The script will automatically skip and continue
- Re-run the script to retry failed downloads

### Issue 4: Docling Conversion Warnings

**Warning:** `LibreOffice DrawingML` warnings

**Solution:**
- These are non-critical warnings
- Install LibreOffice for better conversion quality (see above)
- Conversion will still work without LibreOffice

## Development Setup

### Additional Tools for Development

```bash
# Install development dependencies (if creating)
pip install pytest black flake8 mypy

# Code formatting
black download_tdocs.py

# Linting
flake8 download_tdocs.py

# Type checking
mypy download_tdocs.py
```

## Next Steps

After successful installation:

1. **Run the Pipeline**: See [Running Pipeline](../usage/running-pipeline.md)
2. **Understand Configuration**: See [Configuration](configuration.md)
3. **Explore Features**: See [Features Documentation](../features/)
4. **Read Script Reference**: See [Script Reference](script-reference.md)

---

**Navigation:**
- [← Documentation Home](../README.md)
- [→ Next: Script Reference](script-reference.md)

**Related:**
- [Quick Start](../usage/quick-start.md)
- [Configuration](configuration.md)
- [Running Pipeline](../usage/running-pipeline.md)
