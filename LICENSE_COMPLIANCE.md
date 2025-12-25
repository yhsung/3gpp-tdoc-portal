# License Compliance Analysis

## Project License

**3GPP TDoc Portal** is licensed under **Apache License 2.0**.

## Dependency License Compatibility

This document analyzes all project dependencies for license compatibility with Apache 2.0.

### Summary

✅ **All dependencies are compatible with Apache 2.0**

All third-party libraries use permissive licenses (Apache 2.0, MIT, MPL-2.0/MIT dual-license) that are fully compatible with the project's Apache 2.0 license.

## Dependency Licenses

### 1. requests (>=2.31.0)

**License:** Apache License 2.0
**Compatibility:** ✅ **Compatible**
**Analysis:** Same license as the project. Full compatibility.

**Sources:**
- [requests on PyPI](https://pypi.org/project/requests/)
- [Requests Documentation](https://3.python-requests.org/user/intro/)

**Details:**
- Requests is one of the most popular Python HTTP libraries
- ~30M downloads per week
- Maintained by Kenneth Reitz and the Python Software Foundation
- Apache 2.0 allows use in both open-source and proprietary projects

---

### 2. beautifulsoup4 (>=4.12.0)

**License:** MIT License
**Compatibility:** ✅ **Compatible**
**Analysis:** MIT is permissive and compatible with Apache 2.0. No restrictions on use.

**Sources:**
- [beautifulsoup4 on PyPI](https://pypi.org/project/beautifulsoup4/)
- [Beautiful Soup Documentation](https://beautiful-soup-4.readthedocs.io/en/latest/)
- [Is BeautifulSoup open-source?](https://proxiesapi.com/articles/is-beautifulsoup-open-source)

**Details:**
- MIT is one of the most permissive licenses
- Allows commercial use, modification, distribution
- Can be incorporated into Apache 2.0 licensed projects without issue
- Only requires copyright notice preservation

**MIT License Compatibility with Apache 2.0:**
- ✅ Can include MIT-licensed code in Apache 2.0 projects
- ✅ No copyleft requirements
- ✅ No additional restrictions

---

### 3. docling (>=1.0.0)

**License:** MIT License (core library)
**Component Licenses:**
- **Core Library (docling):** MIT
- **IBM Models (docling-ibm-models):** MIT
- **Granite-Docling Model:** Apache 2.0

**Compatibility:** ✅ **Compatible**
**Analysis:** Core library is MIT licensed. Optional AI models use MIT or Apache 2.0.

**Sources:**
- [docling on PyPI](https://pypi.org/project/docling/)
- [Docling GitHub Repository](https://github.com/docling-project/docling)
- [IBM Research - Docling Announcement](https://research.ibm.com/blog/docling-generative-AI)
- [Granite-Docling on Hugging Face](https://huggingface.co/ibm-granite/granite-docling-258M)

**Details:**
- Developed by IBM Research Zurich
- Hosted by LF AI & Data Foundation
- MIT license for main toolkit
- Apache 2.0 for Granite-Docling AI model
- Both licenses are fully compatible with Apache 2.0

**Components:**
1. **docling (core):** MIT - Document conversion toolkit
2. **docling-ibm-models:** MIT - IBM-specific models
3. **granite-docling-258M:** Apache 2.0 - AI model for document understanding

**Note:** While the core library is MIT, some optional AI models may have different licenses. Always check specific model licenses when using them.

---

### 4. tqdm (>=4.66.0)

**License:** MPL-2.0 OR MIT (Dual Licensed)
**Compatibility:** ✅ **Compatible**
**Analysis:** Can be used under MIT license terms, which is compatible with Apache 2.0.

**Sources:**
- [tqdm on PyPI](https://pypi.org/project/tqdm/)
- [tqdm Documentation](https://tqdm.github.io/)
- [tqdm LICENSE on GitHub](https://github.com/tqdm/tqdm/blob/master/LICENCE)

**Details:**
- Dual-licensed under MPL-2.0 or MIT
- Users can choose either license
- MIT option provides full compatibility with Apache 2.0
- MPL-2.0 is also generally compatible but MIT is simpler

**Dual License Choice:**
- We choose to use tqdm under **MIT License** terms
- MIT is more permissive and simpler for Apache 2.0 projects
- No additional obligations beyond copyright notice

**MPL-2.0 Note:**
- Mozilla Public License 2.0 is a weak copyleft license
- Compatible with Apache 2.0 but requires source availability for modifications
- Using MIT license option avoids these requirements

---

## License Compatibility Matrix

| Dependency | License | Compatible with Apache 2.0 | Notes |
|------------|---------|----------------------------|-------|
| requests | Apache 2.0 | ✅ Yes | Same license |
| beautifulsoup4 | MIT | ✅ Yes | Permissive, no restrictions |
| docling | MIT (core) | ✅ Yes | Core library is MIT |
| docling AI models | MIT or Apache 2.0 | ✅ Yes | All compatible |
| tqdm | MPL-2.0 OR MIT | ✅ Yes | Use under MIT terms |

## Apache 2.0 Compatible Licenses

The following licenses are generally compatible with Apache 2.0:

**Fully Compatible (No Issues):**
- ✅ Apache 2.0
- ✅ MIT
- ✅ BSD (2-clause, 3-clause)
- ✅ ISC
- ✅ MPL-2.0 (when used as library)

**Incompatible Licenses:**
- ❌ GPL v2 (copyleft conflict)
- ❌ GPL v3 (copyleft conflict)
- ❌ AGPL (copyleft conflict)
- ❌ LGPL (complex compatibility)

**Our Dependencies:** All use fully compatible licenses ✅

## Compliance Requirements

### For Apache 2.0 License

When using this project, you must:

1. **Provide License Copy**: Include copy of Apache 2.0 license
2. **State Changes**: Document any modifications made
3. **Preserve Notices**: Keep copyright, patent, trademark, and attribution notices
4. **Include NOTICE**: If NOTICE file exists, include it in distributions

### For Dependencies

**requests (Apache 2.0):**
- Same requirements as project license
- Include Apache 2.0 license notice

**beautifulsoup4 (MIT):**
- Include MIT license notice
- Preserve copyright notice

**docling (MIT):**
- Include MIT license notice for core library
- Check individual model licenses if using specific AI models

**tqdm (MIT - chosen license):**
- Include MIT license notice
- Preserve copyright notice

## NOTICE File

Apache 2.0 projects should include a NOTICE file for attribution. We will create one listing all dependencies and their licenses.

## Recommended Actions

### ✅ Completed

1. ✅ Added Apache 2.0 LICENSE file
2. ✅ Verified all dependency licenses
3. ✅ Confirmed compatibility

### 📋 To Do

1. **Create NOTICE file** - List all dependencies and their licenses
2. **Add license headers** - Add Apache 2.0 boilerplate to source files
3. **Update README** - Add license badge and section
4. **Document third-party licenses** - Create THIRD_PARTY_LICENSES.md

## No Violations Found

**Result:** ✅ **All dependencies are compatible with Apache 2.0**

There are **no licensing violations** or conflicts. All dependencies use permissive licenses that can be freely incorporated into Apache 2.0 licensed projects.

## Future Dependency Additions

When adding new dependencies, verify they use compatible licenses:

**Compatible:**
- Apache 2.0
- MIT
- BSD (2-clause, 3-clause)
- ISC

**Incompatible (Avoid):**
- GPL (any version)
- AGPL
- LGPL
- Any copyleft license

**Check License:**
```bash
# Install pip-licenses
pip install pip-licenses

# Check all installed packages
pip-licenses

# Or check specific package
pip show <package-name>
```

## References

### License Resources

- [Apache License 2.0](http://www.apache.org/licenses/LICENSE-2.0)
- [MIT License](https://opensource.org/licenses/MIT)
- [MPL-2.0 License](https://www.mozilla.org/en-US/MPL/2.0/)
- [Choose a License](https://choosealicense.com/)
- [Apache 2.0 Compatibility](https://www.apache.org/legal/resolved.html)

### Dependency Links

- [requests on PyPI](https://pypi.org/project/requests/)
- [beautifulsoup4 on PyPI](https://pypi.org/project/beautifulsoup4/)
- [docling on PyPI](https://pypi.org/project/docling/)
- [tqdm on PyPI](https://pypi.org/project/tqdm/)

---

**Last Updated:** December 2024
**Status:** ✅ All dependencies compatible, no violations
