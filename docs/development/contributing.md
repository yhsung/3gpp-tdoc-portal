# Contributing Guide

[← Back to Development](../README.md#-development)

## Overview

Thank you for your interest in contributing to the 3GPP TDoc Portal project! This guide will help you understand the development workflow and contribution process.

## Development Workflow

### 1. Set Up Development Environment

Follow the [Getting Started](getting-started.md) guide to set up your environment:

```bash
# Clone repository
git clone https://github.com/yhsung/3gpp-tdoc-portal.git
cd 3gpp-tdoc-portal

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Install development tools (recommended)
pip install black flake8 mypy pytest
```

### 2. Create a Feature Branch

```bash
# Create and switch to a new branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/bug-description
```

### 3. Make Your Changes

- Write clean, readable code
- Follow Python PEP 8 style guidelines
- Add comments for complex logic
- Update documentation if needed

### 4. Test Your Changes

```bash
# Run the script to test functionality
python download_tdocs.py

# Run linter (if installed)
flake8 download_tdocs.py

# Format code (if installed)
black download_tdocs.py

# Type check (if installed)
mypy download_tdocs.py
```

### 5. Commit Your Changes

```bash
# Stage your changes
git add .

# Commit with descriptive message
git commit -m "Add feature: description of your changes"
```

### 6. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create pull request on GitHub
```

## Code Style Guidelines

### Python Style

Follow [PEP 8](https://pep8.org/) Python style guide:

**Good:**
```python
def download_file_worker(filename):
    """Worker function to download a single file."""
    filepath = os.path.join(DOWNLOAD_DIR, filename)

    if os.path.exists(filepath):
        return {'filename': filename, 'status': 'skip', 'message': 'Already exists'}
```

**Bad:**
```python
def downloadFile(fileName):
    filePath=os.path.join(DOWNLOAD_DIR,fileName)
    if os.path.exists(filePath):return {'filename':fileName,'status':'skip','message':'Already exists'}
```

### Formatting

- **Indentation**: 4 spaces (no tabs)
- **Line length**: Maximum 100 characters
- **Imports**: Group by standard library, third-party, local
- **Docstrings**: Use triple quotes for function documentation

**Example:**
```python
import os
import re
from typing import List, Dict

import requests
from bs4 import BeautifulSoup
from docling.document_converter import DocumentConverter

def fetch_document_list(url: str) -> List[str]:
    """
    Fetch list of TDoc files from 3GPP server.

    Args:
        url: URL of the 3GPP directory page

    Returns:
        List of TDoc filenames matching pattern R1-XXXXXXX.zip

    Raises:
        requests.RequestException: If network request fails
    """
    pass
```

### Naming Conventions

- **Functions**: `lowercase_with_underscores`
- **Variables**: `lowercase_with_underscores`
- **Constants**: `UPPERCASE_WITH_UNDERSCORES`
- **Classes**: `PascalCase`

### Comments

Add comments for complex logic:

```python
# Skip if file already exists (resume capability)
if os.path.exists(filepath):
    return {'filename': filename, 'status': 'skip', 'message': 'Already exists'}

# Extract TDoc ID from filename (e.g., "R1-2508300" from "R1-2508300.zip")
tdoc_id = filename.replace('.zip', '')
```

## Testing

### Manual Testing

Test all three phases of the pipeline:

```bash
# Test with small subset first
# Modify BASE_URL to point to a test directory with fewer files

python download_tdocs.py
```

### Test Cases to Cover

1. **Download Phase:**
   - First download (new file)
   - Skip existing file
   - Handle network errors
   - Handle invalid URLs

2. **Extract Phase:**
   - First extraction (new ZIP)
   - Skip already extracted
   - Handle corrupted ZIP files

3. **Convert Phase:**
   - Convert each supported file type (PDF, DOCX, PPTX, XLSX)
   - Skip already converted
   - Handle unsupported formats
   - Handle conversion errors

### Unit Tests (Future)

When adding unit tests, use pytest:

```python
# test_download_tdocs.py

import pytest
from download_tdocs import fetch_document_list

def test_fetch_document_list():
    """Test fetching document list from 3GPP server."""
    url = "https://www.3gpp.org/ftp/meetings_3gpp_sync/RAN1/Docs/"
    files = fetch_document_list(url)

    assert isinstance(files, list)
    assert len(files) > 0
    assert all(f.endswith('.zip') for f in files)
```

## Documentation

### Update Documentation

When making changes, update relevant documentation:

- **README.md**: User-facing features and quick start
- **FOLDER_SUMMARY.md**: Comprehensive project overview
- **docs/**: Detailed documentation (this folder)
- **Code comments**: Inline documentation

### Documentation Structure

```
docs/
├── README.md                    # Documentation hub
├── architecture/                # System design
├── development/                 # Developer guides
├── features/                    # Feature documentation
├── usage/                       # User guides
└── planning/                    # Future plans
```

### Writing Documentation

- Use clear, concise language
- Include code examples
- Add cross-references to related docs
- Keep navigation links updated

## Git Workflow

### Commit Messages

Write clear, descriptive commit messages:

**Good:**
```
Add multi-processing support for document conversion

- Implement ProcessPoolExecutor with configurable workers
- Add progress tracking with tqdm
- Update documentation with performance tuning guide
```

**Bad:**
```
fixed stuff
```

### Commit Message Format

```
<type>: <short summary>

<detailed description>

<footer with references if needed>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

### Branch Naming

- `feature/feature-name` - New features
- `fix/bug-description` - Bug fixes
- `docs/documentation-topic` - Documentation updates
- `refactor/what-was-refactored` - Code refactoring

## Pull Request Process

### Before Submitting

1. ✅ Code follows style guidelines
2. ✅ All tests pass
3. ✅ Documentation is updated
4. ✅ Commit messages are clear
5. ✅ No merge conflicts with main branch

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing
- [ ] Manual testing completed
- [ ] All phases tested (download, extract, convert)

## Related Issues
Fixes #issue-number (if applicable)
```

### Review Process

1. Submit pull request
2. Wait for maintainer review
3. Address feedback if requested
4. Merge when approved

## Code Review Guidelines

When reviewing code:

- **Functionality**: Does it work as intended?
- **Style**: Does it follow code style guidelines?
- **Performance**: Are there performance implications?
- **Documentation**: Is it properly documented?
- **Tests**: Are tests adequate?

## Future Development Roadmap

See [Future Enhancements](../planning/future-enhancements.md) for planned features:

### Short-Term
- Add command-line arguments for configuration
- Implement logging to file
- Add unit tests
- Create configuration file support

### Long-Term
- Web application interface (see [Web App Plan](../planning/web-app-plan.md))
- Database integration
- RESTful API
- Search and filtering capabilities

## Getting Help

- **Documentation**: Check the [docs/](../README.md) folder
- **Issues**: Search existing [GitHub issues](https://github.com/yhsung/3gpp-tdoc-portal/issues)
- **Questions**: Open a new issue with the "question" label

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

**Navigation:**
- [← Configuration](configuration.md)
- [Documentation Home](../README.md)
- [→ Features Overview](../features/)

**Related:**
- [Getting Started](getting-started.md)
- [Script Reference](script-reference.md)
- [Future Enhancements](../planning/future-enhancements.md)
