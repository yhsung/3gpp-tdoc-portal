# 3GPP TDoc Downloader, Extractor, and Converter

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

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

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

### Third-Party Licenses

This project uses the following third-party libraries:
- **requests** - Apache License 2.0
- **beautifulsoup4** - MIT License
- **docling** - MIT License (core library)
- **tqdm** - MPL-2.0 OR MIT License (used under MIT)

All dependencies use permissive licenses compatible with Apache 2.0. See [LICENSE_COMPLIANCE.md](LICENSE_COMPLIANCE.md) for detailed license analysis and [NOTICE](NOTICE) file for attribution.

## Contributing

Contributions are welcome! Please see [docs/development/contributing.md](docs/development/contributing.md) for development guidelines.

## Acknowledgments

- 3GPP for providing access to TDoc documents
- [Docling](https://github.com/docling-project/docling) team at IBM Research for the document conversion engine
