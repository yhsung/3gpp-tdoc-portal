# Artifacts Directory Guide

[← Back to Architecture](../README.md#-architecture)

## Overview

The `artifacts/` directory contains all generated files from the TDoc processing pipeline. This directory is **git-ignored** to avoid committing large binary files to version control.

## Directory Structure

```
artifacts/
├── tdocs/          # Downloaded ZIP files (~2-5 GB)
├── extracted/      # Extracted documents (~5-10 GB)
└── output/         # Converted files (~3-6 GB)
    ├── html/
    └── markdown/
```

## artifacts/tdocs/

**Purpose:** Downloaded TDoc ZIP files from 3GPP server

**Contents:**
- ZIP archives from RAN1 meetings
- File pattern: `R1-XXXXXXX.zip`
- Approximately 630+ files
- Total size: 2-5 GB

**Example:**
```
artifacts/tdocs/
├── R1-2508300.zip
├── R1-2508301.zip
├── R1-2508302.zip
└── ...
```

**Skip Logic:**
Files are skipped if they already exist in this directory, enabling resume capability.

## artifacts/extracted/

**Purpose:** Extracted contents of TDoc ZIP files

**Contents:**
- One directory per TDoc
- Pattern: `artifacts/extracted/R1-XXXXXXX/`
- Preserves original ZIP structure
- Multiple document formats

**Example:**
```
artifacts/extracted/
├── R1-2508300/
│   ├── draft_agenda.docx
│   ├── meeting_notes.pdf
│   └── presentation.pptx
├── R1-2508301/
│   └── proposal.docx
└── ...
```

**Skip Logic:**
Directories are skipped if they exist and contain files, preventing re-extraction.

## artifacts/output/

**Purpose:** Converted HTML and Markdown documents

### artifacts/output/html/

**Contents:**
- HTML converted documents
- Layout preservation
- Pattern: `{TDoc-ID}_{filename}.html`

**Example:**
```
artifacts/output/html/
├── R1-2508300_draft_agenda.html
├── R1-2508300_meeting_notes.html
├── R1-2508300_presentation.html
└── ...
```

### artifacts/output/markdown/

**Contents:**
- Markdown converted documents
- Plain text format
- Pattern: `{TDoc-ID}_{filename}.md`

**Example:**
```
artifacts/output/markdown/
├── R1-2508300_draft_agenda.md
├── R1-2508300_meeting_notes.md
├── R1-2508300_presentation.md
└── ...
```

**Skip Logic:**
Documents are skipped if both HTML and Markdown files exist.

## File Naming Convention

### Format
```
{TDoc-ID}_{original-filename}.{extension}
```

### Components
- **TDoc-ID**: `R1-XXXXXXX` (7-digit number)
- **original-filename**: Base name from source file (without extension)
- **extension**: `html` or `md`

### Examples
| Original File | TDoc ID | Output Files |
|--------------|---------|--------------|
| `proposal.docx` | R1-2508300 | `R1-2508300_proposal.html`<br/>`R1-2508300_proposal.md` |
| `draft agenda.pptx` | R1-2508301 | `R1-2508301_draft_agenda.html`<br/>`R1-2508301_draft_agenda.md` |

## Storage Requirements

### Typical Sizes
- **Single TDoc ZIP**: 1-50 MB
- **Extracted TDoc**: 2-100 MB
- **Converted files**: 1-20 MB per document

### Total Estimates
- **tdocs/**: 2-5 GB (630+ files)
- **extracted/**: 5-10 GB (expanded)
- **output/**: 3-6 GB (HTML + Markdown)
- **Total**: ~10-20 GB for full dataset

## Git Configuration

### .gitignore Entry
```gitignore
# Artifacts - Data directories with large binary files
artifacts/
```

### Rationale
- **Size**: Too large for git (10-20 GB)
- **Binary**: ZIP and document files
- **Regenerable**: Can be recreated by running script
- **Local**: User-specific data

## Cleanup

### Manual Cleanup
```bash
# Remove all artifacts
rm -rf artifacts/

# Remove specific phase
rm -rf artifacts/tdocs/      # Downloaded ZIPs
rm -rf artifacts/extracted/  # Extracted files
rm -rf artifacts/output/     # Converted files
```

### Selective Cleanup
```bash
# Keep downloads, remove processed
rm -rf artifacts/extracted/ artifacts/output/

# Keep everything except output
rm -rf artifacts/output/
```

## Backup Recommendations

**What to Backup:**
- `artifacts/tdocs/` - Downloaded files (to avoid re-download)

**What NOT to Backup:**
- `artifacts/extracted/` - Can be re-extracted from ZIPs
- `artifacts/output/` - Can be regenerated from extracted files

**Backup Strategy:**
- Backup ZIPs to external drive or cloud storage
- Delete extracted/ and output/ when space is needed
- Re-run pipeline to regenerate

---

**Navigation:**
- [← Directory Structure](directory-structure.md)
- [Documentation Home](../README.md)
- [→ Output Files Guide](../usage/output-files.md)

**Related:**
- [Skip Logic](../features/skip-logic.md)
- [Running Pipeline](../usage/running-pipeline.md)
