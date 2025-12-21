# Documentation Restructuring Plan

## Overview
Break down the monolithic FOLDER_SUMMARY.md into a hierarchical, modular documentation structure in the `docs/` folder.

## Current State
- Single file: `FOLDER_SUMMARY.md` (224 lines)
- Contains all documentation in one place
- Difficult to navigate and maintain
- Mix of different concerns (architecture, usage, development, API)

## Proposed Structure

```
docs/
├── README.md                          # Documentation index and navigation
├── architecture/
│   ├── overview.md                    # System architecture overview
│   ├── directory-structure.md         # Repository organization
│   └── artifacts.md                   # Artifacts directory explained
├── development/
│   ├── getting-started.md             # Installation and setup
│   ├── script-reference.md            # download_tdocs.py documentation
│   ├── configuration.md               # Configuration options
│   └── contributing.md                # Development workflow and guidelines
├── features/
│   ├── multi-processing.md            # Parallel processing details
│   ├── skip-logic.md                  # Resume capability explained
│   ├── error-handling.md              # Error handling strategies
│   └── progress-tracking.md           # Progress bars and monitoring
├── usage/
│   ├── quick-start.md                 # Quick start guide
│   ├── running-pipeline.md            # How to run the pipeline
│   └── output-files.md                # Understanding output files
└── planning/
    ├── future-enhancements.md         # Roadmap and planned features
    └── web-app-plan.md                # Link to web app specs
```

## Document Breakdown

### 1. `docs/README.md` (Documentation Hub)
**Purpose:** Central navigation for all documentation
**Content:**
- Overview of documentation structure
- Quick links to common topics
- Getting started guide
- Index of all documents

**Extracted from:**
- Project Overview section
- Links to all sub-documents

---

### 2. `docs/architecture/overview.md`
**Purpose:** High-level system architecture
**Content:**
- System components overview
- Three-phase pipeline architecture
- Technology stack
- Design decisions

**Extracted from:**
- Project Overview
- Development Workflow > Current State
- Key Features overview

---

### 3. `docs/architecture/directory-structure.md`
**Purpose:** Repository organization and file structure
**Content:**
- Complete repository tree
- Explanation of each directory
- File naming conventions
- Organization rationale

**Extracted from:**
- Repository Structure section
- Core Files section (brief overview)

---

### 4. `docs/architecture/artifacts.md`
**Purpose:** Detailed explanation of artifacts directory
**Content:**
- Purpose of artifacts/
- artifacts/tdocs/ structure
- artifacts/extracted/ organization
- artifacts/output/ (html and markdown)
- File patterns and examples
- Git ignore strategy

**Extracted from:**
- Artifacts Directory (Git-Ignored) section
- Git Configuration section

---

### 5. `docs/development/getting-started.md`
**Purpose:** Developer setup and installation
**Content:**
- Prerequisites
- Installation steps
- Dependency explanation
- Environment setup
- Verification steps

**Extracted from:**
- requirements.txt documentation
- Usage > Running the Script
- Installation context from README.md

---

### 6. `docs/development/script-reference.md`
**Purpose:** Complete reference for download_tdocs.py
**Content:**
- Script purpose and overview
- All functions with descriptions
- Configuration constants
- Worker functions explained
- Main pipeline flow
- Code organization

**Extracted from:**
- Core Files > download_tdocs.py section
- Functions list
- Configuration details

---

### 7. `docs/development/configuration.md`
**Purpose:** Configuration options and customization
**Content:**
- All configuration constants
- How to modify settings
- MAX_WORKERS tuning
- Directory path customization
- URL configuration

**Extracted from:**
- Configuration section from download_tdocs.py
- BASE_URL, DOWNLOAD_DIR, etc.

---

### 8. `docs/development/contributing.md`
**Purpose:** Development workflow and contribution guidelines
**Content:**
- Development workflow
- Code style guidelines
- Testing procedures
- Git workflow
- Pull request process
- Future development roadmap

**Extracted from:**
- Development Workflow section
- Git Configuration
- Future Development plans

---

### 9. `docs/features/multi-processing.md`
**Purpose:** Detailed explanation of parallel processing
**Content:**
- Multi-processing architecture
- ProcessPoolExecutor usage
- Worker process design
- Performance benefits
- Tuning guidelines

**Extracted from:**
- Key Features > Multi-Processing
- Worker functions explanation

---

### 10. `docs/features/skip-logic.md`
**Purpose:** Resume capability and smart skipping
**Content:**
- Skip logic for downloads
- Skip logic for extraction
- Skip logic for conversion
- How it enables resumption
- File existence checks

**Extracted from:**
- Key Features > Smart Skip Logic
- Worker function skip conditions

---

### 11. `docs/features/error-handling.md`
**Purpose:** Error handling strategies
**Content:**
- Network error handling
- Invalid ZIP file handling
- Conversion error handling
- Partial file cleanup
- Logging strategy

**Extracted from:**
- Key Features > Error Handling
- Worker function error cases

---

### 12. `docs/features/progress-tracking.md`
**Purpose:** Progress monitoring implementation
**Content:**
- Progress bar implementation
- Status message system
- Summary statistics
- Real-time feedback
- tqdm usage

**Extracted from:**
- Key Features > Progress Tracking
- Output section

---

### 13. `docs/usage/quick-start.md`
**Purpose:** Get up and running quickly
**Content:**
- Minimal steps to start
- Basic usage example
- Expected output
- Troubleshooting common issues

**Extracted from:**
- Usage > Running the Script (simplified)
- Basic workflow

---

### 14. `docs/usage/running-pipeline.md`
**Purpose:** Comprehensive pipeline usage guide
**Content:**
- Complete pipeline walkthrough
- Phase 1: Download details
- Phase 2: Extract details
- Phase 3: Convert details
- Command-line options
- Output interpretation

**Extracted from:**
- Usage section
- Output section
- Pipeline description

---

### 15. `docs/usage/output-files.md`
**Purpose:** Understanding generated output
**Content:**
- Output directory structure
- File naming patterns
- HTML output format
- Markdown output format
- Examples
- How to use output files

**Extracted from:**
- Artifacts Directory section
- Output examples
- File patterns

---

### 16. `docs/planning/future-enhancements.md`
**Purpose:** Roadmap and planned features
**Content:**
- Short-term enhancements
- Long-term vision
- Web application overview
- Database integration plans
- API development plans

**Extracted from:**
- Future Enhancements section
- Future Development section
- Specifications overview

---

### 17. `docs/planning/web-app-plan.md`
**Purpose:** Link and summary of web app plans
**Content:**
- Brief overview of web app
- Link to full spec (specs/web-app-implementation-plan.md)
- Key features summary
- Timeline summary

**Extracted from:**
- Specifications section
- Future Development > web application

---

## Migration Strategy

### Phase 1: Create docs/ Structure
1. Create docs/ directory
2. Create subdirectories (architecture, development, features, usage, planning)
3. Create skeleton files with headers

### Phase 2: Extract and Organize Content
1. Copy relevant sections from FOLDER_SUMMARY.md to new files
2. Add cross-references between documents
3. Add navigation links
4. Ensure no content is lost

### Phase 3: Create Navigation
1. Create docs/README.md as central hub
2. Add table of contents to each document
3. Add "See also" sections for related docs
4. Add breadcrumb navigation

### Phase 4: Update Root Documents
1. Update FOLDER_SUMMARY.md to be a brief overview with links to docs/
2. Update README.md to link to docs/README.md
3. Ensure consistent cross-referencing

### Phase 5: Cleanup
1. Remove redundancy
2. Verify all links work
3. Ensure logical flow
4. Add examples where helpful

## Benefits

### Improved Navigation
- Easier to find specific information
- Logical grouping by topic
- Clear hierarchy

### Better Maintenance
- Smaller, focused files
- Easier to update specific topics
- Less merge conflicts

### Enhanced Usability
- Quick start for new users
- Deep dive for developers
- Clear separation of concerns

### Scalability
- Easy to add new documentation
- Can grow with project
- Modular structure

## Cross-Reference Strategy

Each document should include:
- **Breadcrumb**: `Home > Category > Document`
- **Related Pages**: Links to related docs
- **See Also**: Links to complementary topics
- **Up**: Link to parent category

Example navigation footer:
```markdown
---
**Navigation:**
- [← Back to Architecture](../architecture/)
- [Documentation Home](../README.md)
- [→ Next: Artifacts Guide](artifacts.md)

**Related:**
- [Script Reference](../development/script-reference.md)
- [Getting Started](../development/getting-started.md)
```

## Estimated File Sizes

- Small (< 50 lines): quick-start.md, web-app-plan.md, configuration.md
- Medium (50-100 lines): Most feature and usage docs
- Large (100-150 lines): script-reference.md, directory-structure.md, README.md
- X-Large (150+ lines): None (breaking down large content)

Total estimated: ~1,500-2,000 lines across 17 files (vs 224 lines in 1 file)
More content, but better organized and more discoverable.
