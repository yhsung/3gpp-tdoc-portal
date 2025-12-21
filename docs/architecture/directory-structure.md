# Directory Structure

[← Back to Architecture](../README.md#-architecture)

## Repository Organization

```
3gpp-tdoc-portal/
├── download_tdocs.py          # Main processing script
├── requirements.txt           # Python dependencies
├── README.md                  # Quick start guide
├── FOLDER_SUMMARY.md         # Legacy comprehensive overview
├── .gitignore                 # Git ignore rules
│
├── docs/                      # Documentation (you are here)
│   ├── README.md             # Documentation hub
│   ├── architecture/         # System architecture
│   ├── development/          # Developer guides
│   ├── features/             # Feature documentation
│   ├── usage/                # User guides
│   └── planning/             # Future plans
│
├── specs/                     # Technical specifications
│   └── web-app-implementation-plan.md
│
└── artifacts/                 # Generated files (git-ignored)
    ├── tdocs/                # Downloaded ZIP files
    ├── extracted/            # Extracted documents
    └── output/               # Converted files
        ├── html/            # HTML outputs
        └── markdown/        # Markdown outputs
```

## Core Files

### `download_tdocs.py` (314 lines)
Main executable script containing:
- Configuration constants
- Worker functions for download/extract/convert
- Main pipeline orchestration
- Progress tracking logic

### `requirements.txt`
Python dependencies:
- `requests` - HTTP client
- `beautifulsoup4` - HTML parsing
- `docling` - Document conversion
- `tqdm` - Progress bars

### `README.md`
Quick start documentation with:
- Installation instructions
- Basic usage
- Feature overview
- Links to detailed docs

## Documentation Structure (`docs/`)

### `docs/README.md`
Central documentation hub with navigation to all guides

### `docs/architecture/`
- `overview.md` - System architecture
- `directory-structure.md` - This file
- `artifacts.md` - Artifacts directory guide

### `docs/development/`
- `getting-started.md` - Setup guide
- `script-reference.md` - API documentation
- `configuration.md` - Config options
- `contributing.md` - Contribution guide

### `docs/features/`
- `multi-processing.md` - Parallel processing
- `skip-logic.md` - Resume capability
- `error-handling.md` - Error strategies
- `progress-tracking.md` - Progress monitoring

### `docs/usage/`
- `quick-start.md` - Quick start guide
- `running-pipeline.md` - Usage details
- `output-files.md` - Output explanation

### `docs/planning/`
- `future-enhancements.md` - Roadmap
- `web-app-plan.md` - Web app overview

## Artifacts Directory (`artifacts/`)

All generated files live here (git-ignored):

### `artifacts/tdocs/`
Downloaded ZIP files from 3GPP:
- Pattern: `R1-XXXXXXX.zip`
- ~630+ files available
- Total size: ~2-5 GB

### `artifacts/extracted/`
Extracted document contents:
- Pattern: `artifacts/extracted/R1-XXXXXXX/`
- Preserves original structure
- Multiple file formats per TDoc

### `artifacts/output/html/`
HTML converted documents:
- Pattern: `{TDoc-ID}_{filename}.html`
- Example: `R1-2508300_proposal.html`
- Preserves document layout

### `artifacts/output/markdown/`
Markdown converted documents:
- Pattern: `{TDoc-ID}_{filename}.md`
- Example: `R1-2508300_proposal.md`
- Plain text format

## File Naming Conventions

### TDoc Files
- Format: `R1-XXXXXXX.zip` (7 digits)
- Example: `R1-2508300.zip`

### Extracted Directories
- Format: `artifacts/extracted/R1-XXXXXXX/`
- Contains original file structure from ZIP

### Converted Files
- Format: `{TDoc-ID}_{original-filename}.{ext}`
- Example: `R1-2508300_draft_agenda.html`
- Both HTML and Markdown generated

## Organization Rationale

**Source Code at Root:**
- Quick access to main script
- Clear entry point for users
- Simple project structure

**Documentation in `docs/`:**
- Separates docs from code
- Modular organization
- Easy to navigate

**Artifacts in Separate Directory:**
- All generated files isolated
- Simple git ignore
- Clear data separation

**Specs in `specs/`:**
- Technical specifications
- Future planning documents
- Architecture decisions

---

**Navigation:**
- [← System Overview](overview.md)
- [→ Artifacts Guide](artifacts.md)
- [Documentation Home](../README.md)
