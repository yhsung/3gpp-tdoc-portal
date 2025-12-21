# 3GPP TDoc Downloader, Extractor, and Converter

Python script to download all 3GPP TDoc files from RAN1 meeting documents, extract them, and convert documents to HTML and Markdown using docling.

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the script:
```bash
python download_tdocs.py
```

The script will:
1. Download all TDoc ZIP files from the 3GPP server
2. Extract each ZIP archive
3. Convert documents (PDF, Word, PowerPoint, Excel) to HTML and Markdown
4. Save all files in the `artifacts/` directory

## Features

- **Complete Pipeline**: Download → Extract → Convert in one script
- **Resume capability**: Skips already downloaded, extracted, and converted files
- **Progress bars**: Visual progress indicators for downloads, extraction, and conversion
- **Progress tracking**: Shows detailed status for each step
- **Error handling**: Failures are logged and don't stop the process
- **Respectful downloading**: Includes delays between requests
- **Multiple formats**: Supports PDF, DOCX, DOC, PPTX, PPT, XLSX, XLS

## Directory Structure

```
.
├── download_tdocs.py   # Main script
├── requirements.txt    # Python dependencies
└── artifacts/          # All generated files (git-ignored)
    ├── tdocs/          # Downloaded ZIP files
    ├── extracted/      # Extracted document contents
    └── output/
        ├── html/       # Converted HTML files
        └── markdown/   # Converted Markdown files
```

## Output Files

Converted files are named with the pattern: `{TDoc-ID}_{original-filename}.{html|md}`

Example:
- `R1-2508300_proposal.html`
- `R1-2508300_proposal.md`

## Notes

- Source URL: https://www.3gpp.org/ftp/meetings_3gpp_sync/RAN1/Docs/
- Processing time varies based on document count and size
- Docling provides high-quality conversion with layout preservation
- Approximately 630+ TDoc files to process
