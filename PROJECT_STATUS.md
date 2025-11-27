# Resource Librarian - Project Status

**Last Updated:** 2025-11-27
**Status:** ✅ Phase 3 Complete - Production Ready
**Test Coverage:** 193 tests passing

## Overview

Resource Librarian is a CLI tool for managing a digital library of books and YouTube video transcripts. The project is built with modern Python best practices using Typer, Pydantic, and Rich for a professional user experience.

## Project Structure

```
resource-librarian/
├── src/resourcelibrarian/
│   ├── cli/              # CLI commands and interface
│   ├── core/             # Library management
│   ├── models/           # Data models (Pydantic)
│   ├── sources/          # Book & video ingestion
│   └── utils/            # Utilities (I/O, hashing)
├── tests/                # Comprehensive test suite
├── docs/                 # Documentation
├── pyproject.toml        # Project metadata
└── MANUAL_TESTING.md     # Manual testing guide
```

## Completed Phases

### Phase 1: Data Models ✅
- Implemented comprehensive Pydantic models
- Created VideoManifest, BookManifest, LibraryCatalog
- Full test coverage for all models
- **Commits:** f2dca75

### Phase 2: File I/O and Utilities ✅
- Implemented YAML/JSON I/O utilities
- Created hashing utilities for content verification
- Added book parsing (PDF, EPUB, Markdown)
- Full test coverage for all utilities
- **Commits:** 692771f

### Phase 3: Book and Video Management ✅
- Implemented book ingestion and CLI commands
- Implemented video ingestion with YouTube API integration
- Created comprehensive CLI with `rl` command
- Full test coverage including CLI tests
- **Commits:** 367d889

## Available Commands

### Library Management
```bash
# Initialize a new library
rl init /path/to/library

# Shows library structure and next steps
```

### Book Commands
```bash
# Add a book to the library
rl book add /path/to/book.{pdf,epub,md} \
  --library /path/to/library \
  --author "Author Name" \
  --categories "Programming,Tutorial" \
  --tags "python,advanced"

# List books with optional filters
rl book list --library /path/to/library \
  --author "Author" \
  --category "Programming" \
  --tag "python"

# Get book content
rl book get "Book Title" \
  --library /path/to/library \
  --output /path/to/output.md
```

### Video Commands
```bash
# Fetch a YouTube video and its transcript
rl video fetch "https://www.youtube.com/watch?v=VIDEO_ID" \
  --library /path/to/library \
  --categories "Education,Programming" \
  --tags "tutorial,python"

# Also accepts video IDs and youtu.be URLs
rl video fetch VIDEO_ID --library /path/to/library
rl video fetch "https://youtu.be/VIDEO_ID" --library /path/to/library

# List videos with optional filters
rl video list --library /path/to/library \
  --channel "Channel Name" \
  --category "Education" \
  --tag "tutorial"

# Get video transcript
rl video get "Video Title" \
  --library /path/to/library \
  --output /path/to/transcript.txt
```

## Technical Implementation

### YouTube Integration
- **YouTube Data API v3** for video metadata
  - Requires `YOUTUBE_API_KEY` environment variable
  - Get key from: https://console.cloud.google.com/
- **YouTube Transcript API** for transcripts (no API key needed)
- Automatic fallback through language preferences
- Support for auto-generated transcripts

### Folder Structure
```
library/
├── books/
│   ├── _index/
│   └── author-slug__authorId/
│       └── bookId__title-slug/
│           ├── manifest.yaml
│           └── formats/
│               ├── original.{pdf,epub,md}
│               └── markdown.md
├── videos/
│   ├── _index/
│   └── channel-slug__channelId/
│       └── videoId__title-slug/
│           ├── manifest.yaml
│           ├── source/
│           │   ├── transcript.txt
│           │   └── video.url
│           ├── summaries/
│           └── pointers/
├── catalog.yaml
└── _index/
```

### Data Models
- **Pydantic** for data validation and serialization
- **YAML** for manifest files (human-readable)
- **JSON** for catalog (performance)
- **SHA-256** hashing for content verification

## Test Coverage

**Total Tests:** 193 passing

### Test Breakdown
- **CLI Tests:** 50 tests
  - Book commands: 22 tests
  - Video commands: 22 tests
  - Init command: 9 tests
- **Model Tests:** 44 tests
- **Source Tests:** 44 tests
- **Utils Tests:** 53 tests
- **Library Tests:** 9 tests

### Test Features
- Unit tests for all core functions
- Integration tests for CLI commands
- Mocked tests for external APIs (YouTube)
- Edge case and error handling tests
- Test fixtures and factories

## Dependencies

### Runtime Dependencies
```toml
pydantic>=2.0          # Data validation
pyyaml>=6.0            # YAML parsing
typer>=0.9             # CLI framework
rich>=13.0             # Terminal formatting
pymupdf>=1.23.0        # PDF parsing
ebooklib>=0.18         # EPUB parsing
beautifulsoup4>=4.12.0 # HTML parsing
google-api-python-client>=2.0.0  # YouTube API
youtube-transcript-api>=0.6.0    # Transcript fetching
```

### Development Dependencies
```toml
pytest>=7.0            # Testing framework
pytest-cov>=4.0        # Coverage reporting
ruff>=0.1              # Linting and formatting
```

## Environment Setup

### Prerequisites
- Python 3.11+
- YouTube API key (for video fetching)

### Installation
```bash
# Clone the repository
cd /home/kenne/code/resource-librarian

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# .\venv\Scripts\Activate.ps1  # Windows

# Install dependencies
pip install -e ".[dev]"

# Set up YouTube API key
export YOUTUBE_API_KEY="your-api-key-here"
```

### Running Tests
```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=src/resourcelibrarian --cov-report=html

# Specific test file
pytest tests/test_cli_video.py -v

# Specific test
pytest tests/test_cli_video.py::test_video_fetch_successfully_adds_video_with_mocks -v
```

## Documentation

- **[MANUAL_TESTING.md](MANUAL_TESTING.md)** - Comprehensive manual testing guide
  - 16 test scenarios
  - Prerequisites and setup
  - Error cases and edge cases
  - Troubleshooting guide
  - Sample videos for testing

- **[README.md](README.md)** - Project overview and quick start

## Code Quality

### Linting and Formatting
- **Ruff** for fast Python linting and formatting
- Line length: 100 characters
- Target: Python 3.11+
- Auto-formatting on save (VS Code)

### Configuration
```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "W"]
ignore = ["E501"]
```

## Git History

Recent commits:
```
367d889 feat: complete Phase 3 - Book Management with parsing and ingestion
692771f feat: complete Phase 2 - File I/O utilities with full test coverage
f2dca75 feat: complete Phase 1 - comprehensive data models with full test coverage
4ba1d3a Add basic Catalog extension
0f451f7 Added basic book and video files
```

## Known Limitations

1. **YouTube API Quota**: YouTube Data API has daily quotas (10,000 units/day by default)
   - Video fetch uses ~3 units per video
   - Can fetch ~3,000 videos per day
   - Transcripts use a separate API with no quota limits

2. **Book Formats**: Currently supports PDF, EPUB, and Markdown
   - MOBI and other formats not yet supported
   - Some complex PDFs may not parse correctly

3. **Video Downloads**: Does not download actual video files
   - Stores URL and transcript only
   - Intended for transcript/content management, not video archiving

## Potential Next Steps

While the core functionality is complete, future enhancements could include:

1. **Batch Operations**
   - `rl video fetch-channel` - Fetch all videos from a channel
   - `rl video fetch-playlist` - Fetch all videos from a playlist
   - `rl video fetch-file` - Fetch videos from a text file list

2. **Summarization Features**
   - `rl video summarize` - Generate summary from transcript
   - `rl book summarize` - Generate summary from book content
   - Integration with AI APIs (OpenAI, Anthropic)

3. **Search and Discovery**
   - Full-text search across transcripts and books
   - Semantic search using embeddings
   - Tag-based recommendations

4. **Export and Sharing**
   - Export catalog to JSON/CSV
   - Generate HTML documentation site
   - Share summaries and highlights

5. **Advanced Book Features**
   - Chapter extraction and management
   - Highlight and annotation support
   - MOBI and other format support

6. **Performance Optimizations**
   - Async video fetching for multiple videos
   - Caching for catalog operations
   - Incremental indexing

## Support and Contribution

This is a personal project for managing digital knowledge resources. For issues or questions:
- Review [MANUAL_TESTING.md](MANUAL_TESTING.md) for common issues
- Check test files for implementation examples
- Review source code in `src/resourcelibrarian/`

## License

[Add license information]

---

**Project Maintainer:** Kenny Wilson
**Last Test Run:** 2025-11-27 (193 tests passing)
**Python Version:** 3.11+
**Status:** Production Ready ✅
