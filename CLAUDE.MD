# Claude Code - Resource Librarian Project Guide

**Last Updated:** 2025-11-17
**Project:** Resource Librarian - Digital library management without vectorization

---

## Quick Start for New Sessions

When starting a new session, read these files in order:

1. **This file (CLAUDE.MD)** - Project overview and navigation
2. **[docs/claude-session-state.md](docs/claude-session-state.md)** - Current progress and context
3. **[docs/IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md)** - Complete architecture and phases
4. **[docs/SESSION_RECOVERY.md](docs/SESSION_RECOVERY.md)** - Recovery instructions if context was lost

---

## Project Overview

**Goal:** Build a library management system for digital resources (ebooks, YouTube transcripts) WITHOUT vector/chunking/embedding functionality.

**CLI Name:** `rl` (Resource Librarian)

**What we're building:**
- Book ingestion (PDF, EPUB, Markdown) with metadata extraction
- YouTube transcript fetching with channel organization
- Filesystem-first architecture (no database)
- YAML manifests for metadata
- JSON catalog for search
- CLI for library management (`rl` command)
- Catalog/metadata query system (21 commands total)

**What we're NOT building:**
- Vector embeddings or vector databases
- Text chunking or splitting (except EPUB chapters)
- RAG or LLM integration
- Semantic search

**Source:** Porting from `/home/kenne/resource-library-tools` (selective port)

**Existing Library:** `/mnt/c/Users/kenne/OneDrive/resource-libary/` (for filesystem structure reference)

---

## Documentation Structure

### Planning & Progress Documents (docs/)

| File | Purpose | When to Read/Update |
|------|---------|---------------------|
| **IMPLEMENTATION_PLAN.md** | Complete architecture, phases, technology choices | Read at session start; update when architecture changes |
| **claude-session-state.md** | Current status, completed tasks, blockers | Read at session start; update after each task |
| **SESSION_RECOVERY.md** | Recovery guide with all context | Read if session interrupted or context lost |
| **claude-prompts.md** | Log of all prompts and responses | Append each user prompt/response |

### Project Documents (root)

| File | Purpose |
|------|---------|
| **README.md** | User-facing documentation, features, installation |
| **pyproject.toml** | Package configuration, dependencies |
| **CLAUDE.MD** | This file - project guide for Claude |

---

## Key User Requirements

1. **Incremental verification** - Add commands one at a time, verify every piece of code
2. **Technology understanding** - Verify and understand each technology and package used
3. **No vectorization** - Exclude all chunking, embedding, and vector database logic
4. **Keep documentation updated** - Maintain plan and progress tracking
5. **Planning first** - Stay in planning mode until user approves implementation

---

## Current Project Status

**Phase:** Implementation - `rl init` command COMPLETE ✅

**Last Completed:**
- ✅ Python package skeleton setup
- ✅ Architecture analysis of source and existing library
- ✅ README updated with feature descriptions
- ✅ IMPLEMENTATION_PLAN updated with detailed capabilities
- ✅ Dependencies added: pydantic>=2.0, pyyaml>=6.0, typer>=0.9, rich>=13.0
- ✅ Documentation organized into docs/ folder
- ✅ CLI commands analyzed (21 to port, 10 to exclude)
- ✅ **`rl init` command implemented and tested:**
  - ResourceLibrary class with initialization logic
  - Beautiful Rich terminal output
  - Complete directory structure creation
  - Error handling and validation
  - 10 comprehensive tests, all passing

**Next Phase:** Phase 1 - Core Data Models

**See [docs/claude-session-state.md](docs/claude-session-state.md) for detailed status**

---

## Architecture Quick Reference

### Filesystem Structure

```
library_root/
├── .metadata/
│   ├── catalog.json                    # Searchable catalog
│   └── video_processing_state.json     # Video processing state
├── books/
│   ├── _index/
│   │   ├── authors.md                  # Master author index
│   │   └── titles.md                   # Master title index
│   └── [author]/[book-title]/
│       ├── manifest.yaml               # Book metadata
│       ├── index.md                    # Generated book index
│       ├── full-book-formats/          # PDF, EPUB, TXT, MD
│       └── summaries/                  # Book summaries
└── videos/
    ├── _index/
    │   └── channels.md                 # Master channel index
    └── [channel__id]/[videoid__title]/
        ├── manifest.yaml               # Video metadata
        └── source/transcript.txt       # Video transcript
```

### Python Code Structure

```
src/resourcelibrarian/
├── models/                 # Pydantic data models
│   ├── base.py            # SourceKind enum
│   ├── book.py            # BookMetadata, BookManifest
│   ├── video.py           # VideoMetadata, VideoManifest
│   └── catalog.py         # LibraryCatalog, CatalogEntry
├── sources/               # Resource ingestion
│   ├── book_parser.py     # Parse PDF/EPUB/Markdown
│   ├── book_ingestion.py  # Add books to library
│   ├── youtube_api.py     # Fetch video metadata
│   └── video_ingestion.py # Add videos to library
├── catalog/               # Library management
│   └── catalog_service.py # Search/browse/filter
├── utils/                 # Utilities
│   ├── io.py             # YAML/JSON I/O
│   └── hash.py           # Content hashing
└── cli/                   # Command-line interface
    └── commands.py        # CLI commands
```

---

## Key Technologies

| Technology | Purpose | Version |
|-----------|---------|---------|
| **Pydantic** | Runtime data validation for YAML/JSON | >=2.0 |
| **PyYAML** | YAML manifest parsing | >=6.0 |
| **Typer** | CLI framework | >=0.9 |
| **Rich** | Beautiful terminal output | >=13.0 |
| **PyMuPDF** | PDF parsing and metadata | >=1.23 |
| **ebooklib** | EPUB parsing and chapters | >=0.18 |
| **youtube-transcript-api** | Transcript download (no API key) | >=0.6 |
| **yt-dlp** | Video metadata extraction | >=2023.0 |

**See [docs/IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md) for complete dependency list**

---

## Implementation Phases

| Phase | Status | Description |
|-------|--------|-------------|
| **Phase 0** | ✅ Complete | CLI setup and `rl init` command |
| **Phase 1** | Pending | Core Data Models (base, book, video, catalog) |
| **Phase 2** | Pending | File I/O utilities (YAML, JSON, hashing) |
| **Phase 3** | Pending | Book parsing (PDF, EPUB, Markdown, chapters) |
| **Phase 4** | Pending | YouTube integration (metadata, transcripts) |
| **Phase 5** | Pending | Library organization (KnowledgeHub, Catalog) |
| **Phase 6** | Pending | CLI commands (add, fetch, catalog, list) |
| **Phase 7** | Pending | Testing and documentation |

**See [docs/IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md) for detailed tasks per phase**

---

## What to Port vs Exclude

### INCLUDE (from /home/kenne/resource-library-tools)

**Core Models:**
- `core/book.py`, `core/video.py`, `core/manifest.py`, `core/base.py` (SourceKind only)

**Book Management:**
- `sources/book_ingestion.py`, `sources/book_parser.py`, `sources/epub_chapter_extractor.py`

**YouTube Integration:**
- `sources/youtube_api.py`, `sources/youtube_transcript.py`, `sources/video_ingestion.py`

**Library Organization:**
- `hub.py`, `catalog/catalog_service.py`, `core/indexer.py`

**Utilities:**
- `utils/io.py`, `utils/hash.py`, `utils/converters.py`

### EXCLUDE (from /home/kenne/resource-library-tools)

- `processing/` - All chunking, embedding, indexing
- `rag/` - All LLM/RAG functionality
- `storage/` - Vector databases
- `search/` - Vector search
- `core/chunk.py`, `core/pointer.py`

---

## Common Commands

### Development
```bash
# Activate venv
source venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Lint and format
ruff check .
ruff format .
```

### Git
```bash
# Current branch
git branch --show-current

# Status
git status

# Commit (when user approves)
git add .
git commit -m "message"
```

---

## User Preferences

1. **Always ask before implementing** - Stay in planning mode until approved
2. **One command at a time** - Verify each piece of code
3. **Explain technologies** - Help user understand each package/tool
4. **Update documentation** - Keep plan and progress current
5. **Deep thinking** - Think through architecture decisions carefully

---

## Session Workflow

1. **Session Start:**
   - Read CLAUDE.MD (this file)
   - Read docs/claude-session-state.md
   - Acknowledge previous progress
   - Ask user if continuing previous work or new task

2. **During Session:**
   - Log prompts to docs/claude-prompts.md
   - Update todos in docs/claude-session-state.md
   - Mark tasks complete immediately after finishing

3. **Session End:**
   - Update docs/claude-session-state.md with latest status
   - Update "Last Updated" timestamp
   - Document any blockers or next steps

---

## Important Notes

- **`rl init` complete** - First command implemented and tested
- **CLI commands analyzed** - 21 commands documented in [docs/CLI_COMMANDS_ANALYSIS.md](docs/CLI_COMMANDS_ANALYSIS.md)
- **Test-driven development** - Write tests before/with implementation
- **No emojis** - Unless user explicitly requests them
- **Metadata directory** - Using `.metadata` (not `.knowledgehub`)
- **Core class** - Using `library.py` (not `hub.py`)

---

## Questions to Explore (Planning Phase)

- [x] What CLI commands exist in source project? ✅ See [docs/CLI_COMMANDS_ANALYSIS.md](docs/CLI_COMMANDS_ANALYSIS.md)
- [x] Which commands relate to vectorization (exclude)? ✅ 10 commands excluded
- [x] Which commands relate to library management (include)? ✅ 21 commands to port
- [ ] What catalog query patterns do we need?
- [ ] What index generation logic exists?

---

## Quick Links

- **Source project:** `/home/kenne/resource-library-tools/`
- **Existing library:** `/mnt/c/Users/kenne/OneDrive/resource-libary/`
- **Planning docs:** `docs/`
- **Python code:** `src/resourcelibrarian/`
- **Tests:** `tests/`

---

**For detailed implementation plan, see [docs/IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md)**

**For current progress, see [docs/claude-session-state.md](docs/claude-session-state.md)**

**For recovery instructions, see [docs/SESSION_RECOVERY.md](docs/SESSION_RECOVERY.md)**
