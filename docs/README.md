# Resource Librarian Documentation

Welcome to the Resource Librarian developer documentation. This documentation provides comprehensive technical details about the architecture, implementation, and design decisions of the Resource Librarian project.

---

## 📚 Documentation Map

### New to the Project?

Start here to get up and running:

1. **[Getting Started](GETTING_STARTED.md)** - Developer onboarding, setup, and first steps
2. **[Architecture](ARCHITECTURE.md)** - System overview and design philosophy
3. **[Dependencies](DEPENDENCIES.md)** - Python packages we use and why

### Core Architecture

Understanding how Resource Librarian works:

- **[Architecture Overview](architecture/overview.md)** - Detailed system architecture with diagrams
- **[Data Flow](architecture/data-flow.md)** - How data flows through the system
- **[Filesystem Layout](architecture/filesystem-layout.md)** - Library folder structure explained
- **[Catalog System](architecture/catalog-system.md)** - How cataloging and indexing works

### Module Documentation

Deep dives into specific modules:

- **[CLI Module](modules/cli.md)** - Command-line interface architecture
- **[Models Module](modules/models.md)** - Data models (Book, Video, Catalog)
- **[Sources Module](modules/sources.md)** - Ingestion systems (books, videos)
- **[Core Module](modules/core.md)** - Catalog manager and index generator
- **[Utils Module](modules/utils.md)** - Utility functions

### Parsing & Processing

Technical details on document processing:

- **[Parsing Overview](PARSING.md)** - Document parsing architecture
- **[EPUB Parsing](parsing/epub.md)** - EPUB processing and chapter extraction
- **[PDF Parsing](parsing/pdf.md)** - PDF text extraction
- **[Metadata Extraction](parsing/metadata-extraction.md)** - Metadata extraction strategies
- **[Chapter Extraction](parsing/chapter-extraction.md)** - Chapter splitting from EPUBs

### External Integrations

Working with external services:

- **[YouTube API](integrations/youtube-api.md)** - YouTube Data API integration
- **[YouTube Transcripts](integrations/youtube-transcripts.md)** - Transcript fetching

### Development

Development resources:

- **[Testing](TESTING.md)** - Testing strategy and running tests

---

## 🎯 Quick Navigation by Task

### "I want to understand the system"

→ Start with [Architecture](ARCHITECTURE.md), then read [Data Flow](architecture/data-flow.md)

### "I want to add a new CLI command"

→ Read [CLI Module](modules/cli.md) and [Getting Started](GETTING_STARTED.md)

### "I want to understand book ingestion"

→ Read [Sources Module](modules/sources.md) and [Parsing Overview](PARSING.md)

### "I want to add support for a new book format"

→ Read [Parsing Overview](PARSING.md) and [Sources Module](modules/sources.md)

### "I want to modify the catalog system"

→ Read [Catalog System](architecture/catalog-system.md) and [Core Module](modules/core.md)

### "I want to understand index generation"

→ Read [Catalog System](architecture/catalog-system.md) and [Core Module](modules/core.md)

### "I want to work with the code"

→ Read [Getting Started](GETTING_STARTED.md) for development setup

---

## 📖 Documentation Status

| Document | Status | Last Updated |
|----------|--------|--------------|
| README.md (this file) | ✅ Complete | 2025-11-29 |
| GETTING_STARTED.md | ✅ Complete | 2025-11-29 |
| DEPENDENCIES.md | ✅ Complete | 2025-11-29 |
| ARCHITECTURE.md | 🚧 Coming soon | - |
| PARSING.md | 🚧 Coming soon | - |
| TESTING.md | 🚧 Coming soon | - |

---

## 🏗️ Project Structure

```text
resource-librarian/
├── src/resourcelibrarian/       # Main source code
│   ├── cli/                     # CLI commands (Typer)
│   ├── core/                    # Catalog & indexing
│   ├── models/                  # Data models (Pydantic)
│   ├── sources/                 # Ingestion (books, videos)
│   └── utils/                   # Utilities
├── tests/                       # Test suite (pytest)
├── docs/                        # Documentation (you are here)
└── README.md                    # User-facing documentation
```

---

## 💡 Key Concepts

### Filesystem-First Design

Resource Librarian stores everything as files - no database required. This makes the library:
- **Portable** - Copy the folder, move the library
- **Inspectable** - Open any file in a text editor
- **Version-controllable** - Track changes with git
- **AI-friendly** - LLMs can read files directly

### YAML Manifests

Each resource (book/video) has a `manifest.yaml` file containing:
- Metadata (title, author, dates)
- Available formats
- Categories and tags
- File locations (relative paths)

### Generated Indices

Markdown index files are auto-generated for navigation:
- Library root: Overall stats and recent additions
- Authors/Channels: Grouped by creator
- Titles: Alphabetical listing
- Categories: Topic-based navigation

These indices are regenerated when resources are added or the catalog is rebuilt.

---

## 🔗 Related Resources

- **[User Documentation](../README.md)** - User-facing README for end users
- **[GitHub Repository](https://github.com/kennyrnwilson/resource-librarian)** - Source code
- **[PyPI Package](https://pypi.org/project/resource-librarian/)** - Package distribution (when available)

---

## 📝 Documentation Guidelines

Documentation style:

1. **Be clear and concise** - No fluff, get to the point
2. **Include code examples** - Show, don't just tell
3. **Use diagrams** - Mermaid diagrams for complex relationships
4. **Cross-reference** - Link to related documentation
5. **Keep it up-to-date** - Update docs with code changes

---

**Questions or feedback on documentation?** [Open an issue](https://github.com/kennyrnwilson/resource-librarian/issues) on GitHub.
