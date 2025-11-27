# Resource Librarian Implementation Plan

> **[← Back to Main README](../README.md)** | **[Development Guide](DEVELOPMENT.md)** | **[CLI Commands](CLI_COMMANDS_ANALYSIS.md)**

**Created:** 2025-11-16
**Status:** Planning Phase
**Source:** Porting from /home/kenne/resource-library-tools

---

## Project Goals

Build a library management system for digital resources (ebooks, YouTube transcripts) WITHOUT vector/chunking/embedding functionality. Focus on:

1. Adding and organizing books (PDF, EPUB, Markdown)
2. Fetching and storing YouTube transcripts
3. Maintaining a searchable catalog
4. Generating and storing summaries
5. Providing CLI for library management

---

## What We're Porting (15-18 modules, ~3,500 lines)

### From resource-library-tools - INCLUDE

**Core Data Models (6 files):**
- `knowledgehub/core/book.py` → Book data model
- `knowledgehub/core/video.py` → Video data model
- `knowledgehub/core/manifest.py` → YAML manifest structures
- `knowledgehub/core/metadata.py` → Metadata/catalog system (500 lines)
- `knowledgehub/core/base.py` → Enums (SourceKind only, skip ChunkKind)
- `knowledgehub/core/indexer.py` → Index generation

**Book Management (4 files):**
- `knowledgehub/sources/book_ingestion.py` → Add books to library
- `knowledgehub/sources/book_parser.py` → Parse PDF/EPUB/Markdown
- `knowledgehub/sources/book_folder_scanner.py` → Auto-detect book formats
- `knowledgehub/sources/epub_chapter_extractor.py` → Extract EPUB chapters

**YouTube Integration (3 files):**
- `knowledgehub/sources/youtube_api.py` → Fetch video metadata
- `knowledgehub/sources/youtube_transcript.py` → Get transcripts (no API key!)
- `knowledgehub/sources/video_ingestion.py` → Add videos to library

**Library Organization (2 files):**
- `knowledgehub/hub.py` → Main KnowledgeHub class
- `knowledgehub/catalog/catalog_service.py` → Search/browse library

**Utilities (3 files):**
- `knowledgehub/utils/io.py` → YAML/JSON I/O
- `knowledgehub/utils/hash.py` → Content hashing
- `knowledgehub/utils/converters.py` → PDF/Markdown conversion

**CLI (partial - 1 file):**
- `knowledgehub/cli/commands.py` → Core commands (remove vector-related)

---

## What We're Excluding (Entire Modules)

**DO NOT PORT:**
- `processing/` - All chunking, embedding, indexing
- `rag/` - All LLM/RAG functionality
- `storage/` - Vector databases
- `search/` - Vector search
- `core/chunk.py`, `core/pointer.py`, `core/search.py`
- `utils/pointer_manager.py`

---

## Dependencies Analysis

### Dependencies to ADD (14 packages)

**Core Infrastructure:**
- `pydantic>=2.0` - Data validation and models
- `pyyaml>=6.0` - YAML manifest files
- `typer>=0.9` - CLI framework
- `rich>=13.0` - Beautiful terminal output

**Book Parsing:**
- `pymupdf>=1.23` - PDF parsing
- `ebooklib>=0.18` - EPUB parsing
- `beautifulsoup4>=4.12` - HTML parsing

**YouTube Integration:**
- `google-api-python-client>=2.0` - YouTube API
- `youtube-transcript-api>=0.6` - Transcript fetching (no key needed!)
- `yt-dlp>=2023.0` - Video metadata

**Content Conversion:**
- `markdown>=3.4` - Markdown processing
- `weasyprint>=60.0` - PDF generation

**Utilities:**
- `python-dateutil>=2.8` - Date parsing
- `requests>=2.31` - HTTP requests

### Dependencies to EXCLUDE (12 packages)

**Vector/Embedding:**
- numpy, pandas, pyarrow
- sentence-transformers
- faiss-cpu

**Chunking:**
- langchain-text-splitters

**LLMs:**
- ollama, openai, anthropic, groq, google-generativeai

**Vector Databases:**
- qdrant-client

---

## Architecture Overview

### Filesystem Structure (From Existing Library)

Based on analysis of `/mnt/c/Users/kenne/OneDrive/resource-libary/`:

```
library_root/
├── .knowledgehub/                          # Library metadata
│   ├── catalog.json                        # Searchable catalog (JSON)
│   └── video_processing_state.json         # Video processing state
│
├── books/
│   ├── _index/                             # Book indices
│   │   ├── authors.md                      # By author index
│   │   └── titles.md                       # By title index
│   │
│   ├── [author-normalized]/                # e.g., "ahrens-sönke"
│   │   └── [book-title-normalized]/        # e.g., "how-to-take-smart-notes"
│   │       ├── manifest.yaml               # Book metadata (YAML)
│   │       ├── index.md                    # Generated index page
│   │       │
│   │       ├── full-book-formats/          # Source files
│   │       │   ├── book.epub               # Original EPUB
│   │       │   ├── book.txt                # Extracted text
│   │       │   ├── book.md                 # Markdown version
│   │       │   └── chapters/               # Individual chapters
│   │       │       ├── 1-chapter-name.md
│   │       │       ├── 2-chapter-name.md
│   │       │       └── ...
│   │       │
│   │       ├── summaries/                  # Book summaries
│   │       │   ├── summary-source-1.pdf
│   │       │   ├── summary-source-2.md
│   │       │   └── ...
│   │       │
│   │       ├── highlights/                 # Highlights (skip for now)
│   │       └── pointers/                   # Pointers (skip - vectorization)
│   │
│   └── templates/                          # Book templates
│
├── videos/
│   ├── _index/                             # Video indices
│   │
│   ├── [channel-name__channel-id]/         # e.g., "jeff-su__UCwAnu01qlnVg1Ai2AbtTMaA"
│   │   └── [video-id__title-normalized]/   # e.g., "oO9GLC2iKy8__steal-the-prod..."
│   │       ├── manifest.yaml               # Video metadata (YAML)
│   │       ├── index.md                    # Generated index page
│   │       │
│   │       ├── source/                     # Source files
│   │       │   ├── transcript.txt          # Video transcript
│   │       │   └── video.url               # YouTube URL
│   │       │
│   │       ├── summaries/                  # Video summaries
│   │       │
│   │       ├── highlights/                 # Highlights (skip for now)
│   │       └── pointers/                   # Pointers (skip - vectorization)
│   │
│   └── templates/                          # Video templates
│
├── categories/                             # Category index pages
│   ├── index.md                            # All categories
│   ├── ai.md                               # AI category
│   ├── productivity.md                     # Productivity category
│   └── ...
│
└── processed/                              # SKIP - vectorization artifacts
```

**Key Observations:**
- **Normalized naming:** Authors/titles use lowercase with hyphens (e.g., `ahrens-sönke`)
- **Video directories:** Use `channel-name__channel-id` and `video-id__title` formats
- **Manifest files:** YAML format with comprehensive metadata
- **Index files:** Auto-generated Markdown with navigation links
- **Catalog:** Centralized JSON catalog at `.knowledgehub/catalog.json`
- **Categories:** Markdown files with backlinks to resources
- **NO database:** Everything is files (YAML + JSON + Markdown)

### Python Code Architecture

Based on analysis of `/home/kenne/resource-library-tools`:

```
src/resourcelibrarian/
├── __init__.py                     # Package initialization
│
├── models/                         # Data models (Pydantic)
│   ├── __init__.py
│   ├── base.py                     # Base enums: SourceKind
│   ├── book.py                     # BookMetadata, BookManifest
│   ├── video.py                    # VideoMetadata, VideoManifest
│   └── catalog.py                  # LibraryCatalog, CatalogEntry
│
├── sources/                        # Resource ingestion
│   ├── __init__.py
│   ├── book_parser.py              # Parse PDF/EPUB/Markdown
│   ├── book_ingestion.py           # Add books to library
│   ├── book_folder_scanner.py      # Scan folders for books
│   ├── epub_chapter_extractor.py   # Extract EPUB chapters
│   ├── youtube_api.py              # YouTube API integration
│   ├── youtube_transcript.py       # Transcript fetching
│   └── video_ingestion.py          # Add videos to library
│
├── core/                           # Core library management
│   ├── __init__.py
│   ├── hub.py                      # KnowledgeHub main class
│   ├── indexer.py                  # Generate indices/catalogs
│   └── metadata.py                 # Metadata management (500 lines)
│
├── catalog/                        # Search and browse
│   ├── __init__.py
│   └── catalog_service.py          # Search/filter/browse
│
├── utils/                          # Utilities
│   ├── __init__.py
│   ├── io.py                       # YAML/JSON I/O
│   ├── hash.py                     # Content hashing
│   ├── converters.py               # PDF/Markdown conversion
│   └── path_utils.py               # Path normalization
│
└── cli/                            # Command-line interface
    ├── __init__.py
    └── commands.py                 # Typer CLI commands

tests/                              # Test suite
├── __init__.py
├── test_models/                    # Model tests
├── test_sources/                   # Ingestion tests
├── test_core/                      # Core tests
├── test_catalog/                   # Catalog tests
├── test_utils/                     # Utility tests
└── test_cli/                       # CLI tests
```

**Design Principles:**
1. **Pydantic models** for all data validation
2. **Separation of concerns:** sources → core → catalog → CLI
3. **Filesystem-first:** No database, all YAML/JSON/Markdown
4. **Test-driven:** Write tests before implementation
5. **Type hints:** Full type annotations
6. **Error handling:** Graceful failures with clear messages

### Key Data Models

**BookMetadata (Pydantic):**
- title: str
- author: str
- categories: List[str]
- tags: List[str]
- isbn: Optional[str]
- source_folder: str
- formats: Dict[str, str]  # {format_name: relative_path}
- summaries: Dict[str, str]  # {summary_name: relative_path}
- date_added: datetime
- last_modified: datetime
- content_hash: str

**VideoMetadata (Pydantic):**
- videoId: str
- title: str
- description: str
- url: str
- channelId: str
- channelTitle: str
- publishedAt: datetime
- categories: List[str]
- tags: List[str]
- thumbnails: Dict[str, ThumbnailInfo]
- source: Dict[str, str]  # transcript_path, url_file
- summaries: Dict[str, str]
- duration: Optional[str]

**BookManifest (YAML structure):**
```yaml
title: str
author: str
categories: List[str]
tags: List[str]
isbn: Optional[str]
source_folder: str
formats:
  epub: path
  txt: path
  markdown: path
  chapter-01: path
  chapter-02: path
summaries:
  summary-name: path
embedding_status: str  # REMOVE in our version
```

**VideoManifest (YAML structure):**
```yaml
videoId: str
title: str
description: str
url: str
channelId: str
channelTitle: str
publishedAt: str
categories: List[str]
tags: List[str]
thumbnails: Dict
source:
  transcript_path: str
  url_file: str
summaries: Dict
pointers: Dict  # REMOVE - vectorization
```

**LibraryCatalog (JSON structure at `.knowledgehub/catalog.json`):**
```json
{
  "books": [
    {
      "title": str,
      "author": str,
      "categories": List[str],
      "path": str,
      "formats": List[str],
      "date_added": str
    }
  ],
  "videos": [
    {
      "videoId": str,
      "title": str,
      "channelTitle": str,
      "categories": List[str],
      "path": str,
      "date_added": str
    }
  ],
  "last_updated": str
}
```

---

## Implementation Phases (Incremental, Test-Driven)

### Phase 1: Core Data Models (Week 1)

**Goal:** Establish data structures and validation

**Tasks:**
1. Add pydantic to dependencies
2. Create `resourcelibrarian/models/` directory
3. Port and adapt:
   - `models/base.py` - SourceKind enum
   - `models/book.py` - BookMetadata, BookManifest
   - `models/video.py` - VideoMetadata, VideoManifest
   - `models/catalog.py` - LibraryCatalog
4. Write tests for each model (validation, serialization)

**Deliverable:** Validated data models with 100% test coverage

---

### Phase 2: File I/O Utilities (Week 1)

**Goal:** Handle YAML/JSON persistence and content hashing

**Tasks:**
1. Add pyyaml to dependencies
2. Create `resourcelibrarian/utils/` directory
3. Port and adapt:
   - `utils/io.py` - load_yaml, save_yaml, load_json, save_json
   - `utils/hash.py` - content_hash_file, content_hash_string
4. Write tests for I/O operations

**Deliverable:** Reliable I/O utilities with error handling

---

### Phase 3: Book Management (Week 2)

**Goal:** Add and parse books with automatic metadata extraction and chapter splitting

**Capabilities:**
- **Multiple format support:** PDF, EPUB, Markdown
- **Auto-extract metadata:** Title, author, ISBN from file content
- **Automatic chapter splitting:** Extract chapters from EPUB structure
- **Preserve all formats:** Keep originals + generate txt/md versions
- **Normalized organization:** Store by author/title with consistent naming

**Tasks:**
1. Add pymupdf, ebooklib, beautifulsoup4 to dependencies
2. Create `resourcelibrarian/sources/` directory
3. Port and adapt:
   - `sources/book_parser.py` - Parse PDF/EPUB/Markdown, extract metadata
   - `sources/epub_chapter_extractor.py` - Auto-split chapters from EPUB
   - `sources/book_folder_scanner.py` - Detect available formats
   - `sources/book_ingestion.py` - Orchestrate ingestion, create manifest
4. Write tests with sample books (PDF, EPUB, Markdown)

**Deliverable:** Working book ingestion pipeline with metadata extraction

**Technology Deep Dive:**
- **PyMuPDF:** Fast, reliable PDF parsing and metadata extraction
- **ebooklib:** EPUB parsing, chapter structure detection
- **BeautifulSoup4:** HTML parsing for EPUB content and metadata

---

### Phase 4: YouTube Integration (Week 2)

**Goal:** Fetch and store YouTube transcripts with channel organization

**Capabilities:**
- **YouTube video ingestion:** Single videos or entire channels
- **Automatic transcript download:** No API key required
- **Rich metadata capture:** Title, channel, publish date, tags, thumbnails
- **Channel-based organization:** Group videos by channel
- **Resumable batch processing:** Process large playlists/channels incrementally
- **State tracking:** Resume interrupted downloads, avoid duplicates

**Tasks:**
1. Add google-api-python-client, youtube-transcript-api, yt-dlp
2. Port and adapt:
   - `sources/youtube_api.py` - Fetch video metadata via YouTube API
   - `sources/youtube_transcript.py` - Download transcripts (no API key!)
   - `sources/video_ingestion.py` - Orchestrate ingestion, create manifests
3. Add state tracking for resumable batch processing
4. Write tests with real YouTube videos (public domain)

**Deliverable:** YouTube transcript fetching with resumable batch processing

**Technology Deep Dive:**
- **youtube-transcript-api:** How it works without API keys (scraping fallback)
- **yt-dlp:** Metadata extraction without downloading video files
- **google-api-python-client:** YouTube API integration for metadata
- **Batch processing:** State management for interrupted operations

---

### Phase 5: Library Organization (Week 3)

**Goal:** Centralized library management with traditional catalog browsing

**Capabilities:**
- **List all resources** - Browse entire library like a traditional catalog
- **Filter by metadata** - Author, category, tags for books; channel for videos
- **View available formats** - See all formats for each resource (PDF, EPUB, Markdown, chapters)
- **Retrieve content** - Access full books or specific chapters on demand
- **Access summaries** - List and retrieve existing summaries for any resource
- **Master indices** - Library-wide navigation files:
  - `books/_index/authors.md` - All books organized by author
  - `books/_index/titles.md` - All books organized by title
  - `videos/_index/channels.md` - All videos organized by channel
- **Individual resource indices** - Each book/video gets a beautiful `index.md` file
- **JSON catalog** - Fast searchable catalog at `.knowledgehub/catalog.json`

**Tasks:**
1. Create `resourcelibrarian/hub.py`
2. Port and adapt:
   - `hub.py` - Main KnowledgeHub class with catalog queries
   - `catalog/catalog_service.py` - Search/browse/filter functionality
   - `core/indexer.py` - Generate master and individual index files
3. Write tests for:
   - Library operations (add, list, search, delete)
   - Filtering by author, category, tags
   - Format queries (list available formats)
   - Content retrieval (full book, specific chapter)
   - Index generation (master indices, individual indices)

**Deliverable:** Working KnowledgeHub with full catalog browsing capabilities

**Technology Deep Dive:**
- **Catalog design:** In-memory catalog built from manifest files
- **Index generation:** Markdown templates for navigation
- **Query patterns:** Filter, sort, and retrieve operations

---

### Phase 6: CLI Interface (Week 3)

**Goal:** User-friendly command-line interface

**Tasks:**
1. ✅ Add typer, rich to dependencies
2. ✅ Create `resourcelibrarian/cli/` directory
3. Port and adapt commands:
   - ✅ `init` - Initialize library
   - `status` - Show library stats
   - `add book [path]` - Add book
   - `add book-folder [path]` - Add folder of books
   - `fetch video [url]` - Fetch YouTube video
   - `fetch channel [url]` - Fetch channel videos
   - `catalog list-books` - List all books
   - `catalog search [query]` - Search library
4. Write integration tests for CLI

**Deliverable:** Complete CLI with rich output

**Technology Deep Dive:**
- **Typer:** CLI framework advantages
- **Rich:** Beautiful terminal formatting

---

### Phase 7: Content Conversion (Week 4)

**Goal:** PDF/Markdown conversion utilities

**Tasks:**
1. Add markdown, weasyprint to dependencies
2. Port and adapt:
   - `utils/converters.py` - PDF to Markdown, Markdown to PDF
3. Write tests for conversions

**Deliverable:** Conversion utilities

**Technology Deep Dive:**
- **Weasyprint:** PDF generation from HTML/Markdown

---

### Phase 8: Testing & Documentation (Week 4)

**Goal:** Comprehensive testing and user documentation

**Tasks:**
1. Ensure all modules have >80% test coverage
2. Write integration tests for end-to-end workflows
3. Update README with:
   - Installation instructions
   - Usage examples
   - CLI command reference
4. Create docs/:
   - Architecture overview
   - Data model documentation
   - Development guide

**Deliverable:** Production-ready package

---

## Verification Strategy (Every Step)

For each module we port:

1. **Review Source Code:**
   - Read original file from resource-library-tools
   - Identify vector/chunking logic to exclude
   - Understand dependencies

2. **Adapt and Simplify:**
   - Rename to match resourcelibrarian package
   - Remove vector-related imports/logic
   - Update paths and references

3. **Write Tests First:**
   - Create test file in tests/
   - Write test cases for happy path
   - Write test cases for error handling

4. **Implement:**
   - Port code incrementally
   - Run tests after each function
   - Fix issues immediately

5. **Verify:**
   - Run pytest with coverage
   - Verify no regressions
   - Update documentation

6. **Commit:**
   - Git commit with clear message
   - Update session state

---

## Technology Deep Dives (As We Go)

For each new technology/package:

1. **What is it?** - Package purpose and alternatives
2. **Why use it?** - Advantages over alternatives
3. **How does it work?** - Core concepts
4. **Example usage** - Simple examples
5. **Best practices** - Common patterns
6. **Pitfalls** - What to avoid

**Technologies to explain:**
- Pydantic (data validation)
- PyMuPDF (PDF parsing)
- ebooklib (EPUB parsing)
- youtube-transcript-api (no API key!)
- Typer (CLI framework)
- Rich (terminal output)
- Weasyprint (PDF generation)

---

## Success Criteria

**Phase Complete When:**
- [ ] All modules ported and adapted
- [ ] All tests passing (>80% coverage)
- [ ] CLI commands working
- [ ] Can add books (PDF, EPUB, Markdown)
- [ ] Can fetch YouTube transcripts
- [ ] Can search/browse library
- [ ] Documentation complete
- [ ] No vector/chunking dependencies
- [ ] Clean git history

---

## Next Steps

1. **Review this plan** - Discuss and adjust
2. **Start Phase 1** - Core data models
3. **One module at a time** - Verify each step
4. **Update progress** - Keep session state current

---

## Questions to Resolve

1. Do we need summary generation in v1? (Or just store summaries?)
2. Should we support multiple library roots?
3. Do we need a database or is YAML sufficient?
4. Should we support custom metadata fields?
5. Do we need book/video deletion commands?

---

**Last Updated:** 2025-11-16
