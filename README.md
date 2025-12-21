# 3GPP TDoc Downloader, Extractor, and Converter

Python script to download all 3GPP TDoc files from RAN1 meeting documents, extract them, and convert documents to HTML and Markdown using docling.

> 📋 For comprehensive project documentation, see [FOLDER_SUMMARY.md](FOLDER_SUMMARY.md)

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
- **Multi-processing**: Parallel processing with 4 workers for faster execution

## Output

All files are saved in the `artifacts/` directory:
- `artifacts/tdocs/` - Downloaded ZIP files
- `artifacts/extracted/` - Extracted documents
- `artifacts/output/html/` - HTML conversions
- `artifacts/output/markdown/` - Markdown conversions

Converted files follow the pattern: `{TDoc-ID}_{original-filename}.{html|md}`

## Additional Information

- **Source**: [3GPP RAN1 Documents](https://www.3gpp.org/ftp/meetings_3gpp_sync/RAN1/Docs/)
- **Document Count**: ~630+ TDoc files available
- **Conversion Engine**: [Docling](https://github.com/DS4SD/docling) for high-quality layout preservation
- **Documentation**: See [FOLDER_SUMMARY.md](FOLDER_SUMMARY.md) for detailed project information
- **Web Application**: See [specs/web-app-implementation-plan.md](specs/web-app-implementation-plan.md) for future development plans
