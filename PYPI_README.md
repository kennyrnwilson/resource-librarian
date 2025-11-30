# Resource Librarian

A Python library for creating, maintaining, and indexing a personal library of digital resources. Organize your books and YouTube video transcripts in a filesystem-based structure that's perfect for AI processing.

[![PyPI version](https://badge.fury.io/py/resource-librarian.svg)](https://badge.fury.io/py/resource-librarian)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## What is Resource Librarian?

Resource Librarian helps you build a **filesystem-based knowledge library** from:
- **Books** (PDF, EPUB, Markdown)
- **YouTube videos** (transcripts and metadata)

No database required - everything is organized in plain files with YAML metadata and Markdown indices.

## Key Features

### 📚 Book Management
- Supports PDF, EPUB, and Markdown formats
- Auto-extracts metadata (title, author, ISBN)
- Automatically splits EPUB into chapters
- Preserves all original formats
- Organizes by author with normalized naming

### 🎥 YouTube Video Management
- Downloads transcripts automatically (no API key needed for transcripts)
- Captures video metadata (title, channel, publish date, tags)
- Organizes by channel
- Resumable batch processing for large collections

### 🗂️ Library Organization
- **Filesystem-first** - All content stored as files, no database
- **YAML manifests** - Structured metadata for each resource
- **Searchable catalog** - YAML-based catalog for quick lookups
- **Generated indices** - Beautiful Markdown index pages for navigation
- **Auto-regenerated** - Indices update when resources are added

## Installation

```bash
pip install resource-librarian
```

## Quick Start

### Initialize a Library

```bash
# Create a new library
rl init my-library
cd my-library
```

### Add Books

```bash
# Add a single book
rl book add /path/to/book.epub --author "Author Name"

# Import a folder of books
rl book import-folder /path/to/books/

# List all books
rl book list

# Get book details
rl book get "Book Title"
```

### Add YouTube Videos

```bash
# Set up YouTube API key (for metadata only)
export YOUTUBE_API_KEY="your-api-key-here"

# Fetch a video transcript
rl video fetch https://youtube.com/watch?v=VIDEO_ID

# List all videos
rl video list

# Get video details
rl video get "Video Title"
```

### Manage Your Library

```bash
# Rebuild catalog from filesystem
rl catalog rebuild

# Show library statistics
rl catalog stats

# Migrate old library format
rl catalog migrate --library /path/to/old-library
```

## Library Structure

Your library is organized in a clean, filesystem-based structure:

```
my-library/
├── catalog.yaml                    # Library catalog
├── _index/
│   └── README.md                   # Library overview
├── books/
│   ├── _index/
│   │   ├── authors.md              # Books by author
│   │   └── titles.md               # Books by title
│   └── author-lastname-firstname/
│       └── book-title/
│           ├── manifest.yaml       # Book metadata
│           ├── full-book-formats/
│           │   ├── book.epub       # Original EPUB
│           │   ├── book.pdf        # Original PDF
│           │   ├── book.md         # Extracted markdown
│           │   └── chapters/       # Individual chapters
│           └── summaries/          # Book summaries
└── videos/
    ├── _index/
    │   └── channels.md             # Videos by channel
    └── channel-name__CHANNEL-ID/
        └── VIDEO-ID__video-title/
            ├── manifest.yaml       # Video metadata
            └── source/
                └── transcript.txt  # Video transcript
```

## Use Cases

- **Personal knowledge management** - Organize your reading and learning
- **Research** - Collect and index academic papers and resources
- **AI/LLM projects** - Structured data ready for RAG systems
- **Content archiving** - Preserve YouTube content with transcripts
- **Book clubs** - Share organized collections with metadata

## Requirements

- Python 3.11 or higher
- YouTube Data API key (optional, for video metadata)
- Internet connection (for YouTube features)

## Documentation

Full documentation available on GitHub:

- **[GitHub Repository](https://github.com/kennyrnwilson/resource-librarian)** - Source code and issues
- **[Getting Started Guide](https://github.com/kennyrnwilson/resource-librarian/blob/main/docs/GETTING_STARTED.md)** - Developer setup
- **[Architecture](https://github.com/kennyrnwilson/resource-librarian/blob/main/docs/ARCHITECTURE.md)** - System design
- **[Dependencies](https://github.com/kennyrnwilson/resource-librarian/blob/main/docs/DEPENDENCIES.md)** - Package choices
- **[Parsing Details](https://github.com/kennyrnwilson/resource-librarian/blob/main/docs/PARSING.md)** - Document parsing

## Example Workflows

### Build a Personal Library

```bash
# Initialize library
rl init ~/my-knowledge-library
cd ~/my-knowledge-library

# Add your book collection
rl book import-folder ~/Downloads/ebooks/

# Add educational videos
rl video fetch https://youtube.com/watch?v=dQw4w9WgXcQ
rl video fetch https://youtube.com/watch?v=VIDEO_ID_2

# Generate indices
rl catalog rebuild

# View your collection
rl catalog stats
rl book list
rl video list
```

### Migrate from v0.1.0

If you have a library from version 0.1.0 with `.knowledgehub/` directory:

```bash
rl catalog migrate --library /path/to/old-library
```

This converts your library to the new format with `catalog.yaml`.

## Technologies Used

- **CLI**: [Typer](https://typer.tiangolo.com/) for command-line interface
- **Output**: [Rich](https://rich.readthedocs.io/) for beautiful terminal output
- **Data**: [Pydantic](https://docs.pydantic.dev/) for data validation
- **Parsing**: [PyMuPDF](https://pymupdf.readthedocs.io/) for PDFs, [ebooklib](https://github.com/aerkalov/ebooklib) for EPUB
- **YouTube**: [google-api-python-client](https://github.com/googleapis/google-api-python-client) for metadata, [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) for transcripts

## Contributing

Contributions are welcome! Please visit our [GitHub repository](https://github.com/kennyrnwilson/resource-librarian) to:

- Report bugs
- Request features
- Submit pull requests
- Read contribution guidelines

## License

MIT License - see [LICENSE](https://github.com/kennyrnwilson/resource-librarian/blob/main/LICENSE) for details.

Copyright (c) 2024 Kenny Wilson

## Links

- **PyPI**: https://pypi.org/project/resource-librarian/
- **GitHub**: https://github.com/kennyrnwilson/resource-librarian
- **Issues**: https://github.com/kennyrnwilson/resource-librarian/issues
- **Documentation**: https://github.com/kennyrnwilson/resource-librarian/tree/main/docs

---

**Made with ❤️ for knowledge enthusiasts and AI researchers**
