# Dependencies

This document explains every Python package used in Resource Librarian and the rationale behind choosing each one.

---

## Overview

Resource Librarian carefully selects dependencies that are:
- **Well-maintained** - Active development and community support
- **Performant** - Fast execution for large libraries
- **Type-safe** - Support for type hints and validation
- **Minimal** - Only essential dependencies, no bloat

---

## Core Dependencies

### Data Validation & Models

#### Pydantic (`pydantic>=2.0`)

**What it does:**
- Provides data validation using Python type hints
- Automatic serialization/deserialization to/from dictionaries
- Runtime type checking and validation
- JSON schema generation

**Why we chose it:**
- **Type safety** - Catch errors at runtime before they reach the filesystem
- **Validation** - Automatically validates YAML manifests when loaded
- **Clean API** - Simple, intuitive class-based models
- **Performance** - Pydantic v2 is built on Rust for speed

**Where we use it:**
- `models/book.py` - `BookManifest` validates book metadata
- `models/video.py` - `VideoManifest` validates video metadata
- `models/catalog.py` - `Catalog` model for library catalog
- All models ensure data integrity when loading from YAML files

**Example:**

```python
from pydantic import BaseModel, Field

class BookManifest(BaseModel):
    title: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1)
    isbn: str | None = None
    categories: list[str] = Field(default_factory=list)

# Pydantic validates on creation
manifest = BookManifest(
    title="Python Programming",
    author="John Smith",
    isbn="978-0-123456-78-9"
)
# Raises ValidationError if title is empty or wrong type
```

**Alternatives considered:**
- `dataclasses` (stdlib) - No validation or serialization
- `attrs` - Less validation, no type coercion
- `marshmallow` - Verbose schema definitions

---

### YAML Processing

#### PyYAML (`pyyaml>=6.0`)

**What it does:**
- Parse YAML files to Python dictionaries
- Serialize Python objects to YAML format
- Human-readable configuration format

**Why we chose it:**
- **Industry standard** - De facto YAML library for Python
- **Human-readable** - YAML is easier to read than JSON
- **Comments** - Supports comments (unlike JSON)
- **Safe loading** - `yaml.safe_load()` prevents code execution

**Where we use it:**
- `utils/io.py` - Load/save manifest files (`manifest.yaml`)
- `core/catalog_manager.py` - Load/save catalog (`catalog.yaml`)
- All YAML I/O operations throughout the codebase

**Example:**

```python
import yaml

# Load manifest
with open("manifest.yaml") as f:
    data = yaml.safe_load(f)

# Save manifest
with open("manifest.yaml", "w") as f:
    yaml.safe_dump(data, f, default_flow_style=False)
```

**Alternatives considered:**
- JSON - Less human-readable, no comments
- TOML - Less suitable for nested structures
- XML - Verbose and complex

---

### Command-Line Interface

#### Typer (`typer>=0.9`)

**What it does:**
- Modern CLI framework built on top of Click
- Automatic argument parsing from type hints
- Built-in help text generation
- Subcommand support

**Why we chose it:**
- **Type hints** - Function signatures = CLI interface
- **Minimal boilerplate** - No manual argument parsing
- **Intuitive** - Easy to add new commands
- **Modern** - Uses Python 3.6+ type hints
- **Well-documented** - Excellent documentation and examples

**Where we use it:**
- `cli/commands.py` - All CLI commands (`rl book`, `rl video`, etc.)
- `__main__.py` - Main CLI entry point

**Example:**

```python
import typer

app = typer.Typer()

@app.command()
def add(
    file_path: str = typer.Argument(..., help="Path to book file"),
    author: str | None = typer.Option(None, "--author", "-a"),
):
    """Add a book to the library."""
    # Type hints automatically create CLI options
    # --author/-a becomes optional string parameter
```

**Alternatives considered:**
- `click` - More verbose, no type hints
- `argparse` (stdlib) - Too much boilerplate
- `fire` - Too magical, hard to debug

---

#### Rich (`rich>=13.0`)

**What it does:**
- Beautiful terminal output formatting
- Tables, panels, syntax highlighting
- Progress bars, spinners
- Color and style support

**Why we chose it:**
- **User experience** - Makes CLI output beautiful and readable
- **Tables** - Perfect for `rl book list` and `rl video list`
- **Panels** - Great for success/error messages
- **Markdown** - Can render markdown in terminal
- **Integrates with Typer** - Seamless integration

**Where we use it:**
- `cli/commands.py` - All command output formatting
- Tables for listing books/videos
- Panels for success/error messages
- Syntax highlighting for code/text output

**Example:**

```python
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

# Beautiful tables
table = Table(title="Books in Library")
table.add_column("Title", style="cyan")
table.add_column("Author", style="green")
table.add_row("Python Programming", "John Smith")
console.print(table)

# Styled panels
console.print(Panel.fit(
    "[green]✓[/green] Book added successfully!",
    title="Success",
    border_style="green"
))
```

**Alternatives considered:**
- Plain `print()` - No formatting, ugly output
- `colorama` - Only colors, no tables/panels
- `tabulate` - Tables only, no styling

---

### PDF Processing

#### PyMuPDF (`pymupdf>=1.23.0`)

**What it does:**
- Fast PDF text extraction
- Access to PDF metadata
- Page-by-page processing
- Image extraction (not currently used)

**Why we chose it:**
- **Speed** - Significantly faster than alternatives
- **Accuracy** - Better text extraction quality
- **Active development** - Regular updates and bug fixes
- **Full-featured** - Can handle complex PDFs
- **Well-tested** - Production-ready library

**Where we use it:**
- `sources/book_parser.py` - `parse_pdf()` method extracts text from PDFs

**Example:**

```python
import fitz  # PyMuPDF

# Open PDF
doc = fitz.open("book.pdf")

# Extract text from all pages
text = ""
for page in doc:
    text += page.get_text()

# Access metadata
metadata = doc.metadata
title = metadata.get("title", "")
author = metadata.get("author", "")
```

**Alternatives considered:**
- `PyPDF2` - Slower, less accurate text extraction
- `pdfplumber` - Slower, more focused on tables
- `pdfminer.six` - Complex API, slower
- `pypdf` - Newer fork of PyPDF2, but still slower than PyMuPDF

**Performance comparison** (extracting 100-page PDF):
- PyMuPDF: ~0.5 seconds
- PyPDF2: ~3 seconds
- pdfminer.six: ~5 seconds

---

### EPUB Processing

#### ebooklib (`ebooklib>=0.18`)

**What it does:**
- Read EPUB files (EPUB 2 and EPUB 3)
- Access EPUB structure (spine, table of contents)
- Extract metadata (title, author, ISBN)
- Extract individual chapters/sections

**Why we chose it:**
- **Industry standard** - Most widely used EPUB library for Python
- **Complete** - Supports EPUB 2 and 3 specifications
- **Metadata** - Easy access to Dublin Core metadata
- **Chapter extraction** - Can parse table of contents and spine
- **Well-maintained** - Active development

**Where we use it:**
- `sources/book_parser.py` - `parse_epub()` extracts full text
- `sources/book_parser.py` - `extract_epub_metadata()` gets title/author/ISBN
- `sources/epub_chapter_extractor.py` - Extracts individual chapters

**Example:**

```python
from ebooklib import epub

# Read EPUB
book = epub.read_epub("book.epub")

# Extract metadata
title = book.get_metadata('DC', 'title')[0][0]
author = book.get_metadata('DC', 'creator')[0][0]

# Extract text from all chapters
text = ""
for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
    text += item.get_content().decode('utf-8')
```

**Alternatives considered:**
- Manual ZIP parsing - EPUB is ZIP, but complex structure
- `epub` - Abandoned, not maintained
- Custom implementation - Too complex, not worth it

---

#### BeautifulSoup4 (`beautifulsoup4>=4.12.0`)

**What it does:**
- Parse HTML and XML documents
- Extract text from HTML
- Clean up malformed HTML
- Navigate document structure

**Why we chose it:**
- **EPUB HTML** - EPUB chapters are XHTML, need parsing
- **Robust** - Handles malformed HTML gracefully
- **Clean API** - Simple, intuitive interface
- **Text extraction** - Easy to get clean text from HTML
- **Well-maintained** - Industry standard for HTML parsing

**Where we use it:**
- `sources/book_parser.py` - Extract text from EPUB HTML content
- `sources/epub_chapter_extractor.py` - Clean chapter HTML

**Example:**

```python
from bs4 import BeautifulSoup

# Parse EPUB chapter HTML
html = """
<html>
<body>
    <h1>Chapter 1</h1>
    <p>This is some text.</p>
</body>
</html>
"""

soup = BeautifulSoup(html, 'html.parser')
text = soup.get_text()  # "Chapter 1\nThis is some text."
```

**Alternatives considered:**
- `lxml` - Faster but less forgiving of malformed HTML
- `html.parser` (stdlib) - Less robust
- Regular expressions - Too fragile for HTML

---

### YouTube Integration

#### Google API Python Client (`google-api-python-client>=2.0.0`)

**What it does:**
- Official Google API client library
- Access to YouTube Data API v3
- Fetch video metadata (title, description, channel, etc.)
- Search videos, get channel info

**Why we chose it:**
- **Official** - Google's official client library
- **Complete** - Full API coverage
- **Well-maintained** - Regular updates
- **Type hints** - Good type hint support
- **Documentation** - Excellent documentation

**Where we use it:**
- `sources/youtube_api.py` - Fetch video metadata from YouTube Data API

**Example:**

```python
from googleapiclient.discovery import build

youtube = build('youtube', 'v3', developerKey=api_key)

# Get video metadata
response = youtube.videos().list(
    part='snippet,contentDetails',
    id='video_id'
).execute()

title = response['items'][0]['snippet']['title']
channel = response['items'][0]['snippet']['channelTitle']
```

**Alternatives considered:**
- `youtube-dl` - Focused on downloading, not metadata
- Custom HTTP requests - Too much boilerplate
- Scraping - Against YouTube TOS, unreliable

---

#### YouTube Transcript API (`youtube-transcript-api>=0.6.0`)

**What it does:**
- Fetch video transcripts/captions
- Support for auto-generated and manual captions
- Multiple language support
- No API key required

**Why we chose it:**
- **No API key** - Uses YouTube's internal API (public data)
- **Simple** - One function call to get transcript
- **Reliable** - Well-tested, widely used
- **Free** - No quota limits (unlike YouTube Data API)

**Where we use it:**
- `sources/youtube_transcript.py` - Fetch video transcripts

**Example:**

```python
from youtube_transcript_api import YouTubeTranscriptApi

# Get transcript
transcript = YouTubeTranscriptApi.get_transcript('video_id')

# Transcript is list of segments
for segment in transcript:
    text = segment['text']
    start = segment['start']
    duration = segment['duration']
```

**Alternatives considered:**
- YouTube Data API captions endpoint - Requires OAuth, complex
- Scraping - Against TOS, unreliable
- Manual download - Too manual, not automatable

---

## Development Dependencies

### Testing

#### pytest (`pytest>=7.0`)

**What it does:**
- Modern Python testing framework
- Simple assertion syntax
- Fixture system for test setup
- Plugin ecosystem

**Why we chose it:**
- **Industry standard** - Most popular Python test framework
- **Simple** - Just write functions with `test_` prefix
- **Powerful** - Fixtures, parametrization, plugins
- **Great output** - Clear failure messages

**Example:**

```python
def test_book_parsing():
    parser = BookParser()
    text = parser.parse("book.epub")
    assert len(text) > 0
    assert "Chapter" in text
```

---

#### pytest-cov (`pytest-cov>=4.0`)

**What it does:**
- Code coverage reporting for pytest
- Shows which lines are tested
- HTML reports for visualization

**Why we chose it:**
- **Coverage tracking** - See what code is tested
- **HTML reports** - Visual coverage reports
- **CI integration** - Easy to use in CI/CD

---

### Code Quality

#### Ruff (`ruff>=0.1`)

**What it does:**
- Fast Python linter (replaces flake8, pylint, isort, etc.)
- Code formatter (replaces black)
- Written in Rust - extremely fast
- Auto-fix for many issues

**Why we chose it:**
- **Speed** - 10-100x faster than alternatives
- **All-in-one** - Linter + formatter in one tool
- **Auto-fix** - Automatically fixes many issues
- **Modern** - Active development, frequent updates
- **Configuration** - Simple configuration in `pyproject.toml`

**Configuration in `pyproject.toml`:**

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "W"]  # Error, Flake8, Warning
ignore = ["E501"]  # Ignore line length (formatter handles it)
```

**Alternatives considered:**
- `black` - Formatter only, separate tool
- `flake8` - Slower, less features
- `pylint` - Very slow, overly strict
- `isort` - Import sorting only

---

## Dependency Philosophy

### Why So Few Dependencies?

We intentionally keep dependencies minimal:

1. **Maintenance burden** - Each dependency can break or become unmaintained
2. **Security** - Fewer dependencies = smaller attack surface
3. **Stability** - Fewer moving parts = more stable system
4. **Performance** - Fewer imports = faster startup time

### When We Add Dependencies

We only add a new dependency when:

1. **Significant value** - Saves substantial development time
2. **Well-maintained** - Active development and community
3. **No good alternative** - Can't reasonably implement ourselves
4. **Widely used** - Proven in production environments

### When We Don't Add Dependencies

We avoid dependencies for:

1. **Simple utilities** - Easy to implement ourselves
2. **Abandoned packages** - No recent updates
3. **Over-engineered** - Too complex for our needs
4. **Unstable APIs** - Frequent breaking changes

---

## Dependency Update Policy

### Regular Updates

We update dependencies:
- **Monthly** - Check for new versions
- **Security patches** - Immediately apply security updates
- **Major versions** - Test thoroughly before upgrading

### Version Constraints

We use `>=` constraints:
```toml
dependencies = [
    "pydantic>=2.0",  # Allow 2.x updates
    "typer>=0.9",     # Allow 0.x updates
]
```

This allows:
- Bug fixes and security patches
- Minor version updates
- User flexibility

We don't pin exact versions (`==`) because:
- Users may need newer versions for other projects
- Security patches should be automatic
- Prevents dependency conflicts

---

## Future Dependencies

Packages we might add in the future:

- **aiofiles** - Async file I/O for large libraries
- **httpx** - Modern async HTTP client (if we add web features)
- **watchdog** - File system monitoring (for auto-rebuild)
- **pillow** - Image processing (for cover image extraction)

We'll only add these when the need arises and benefits outweigh costs.

---

## Summary Table

| Package | Version | Purpose | Why Chosen |
|---------|---------|---------|------------|
| pydantic | >=2.0 | Data validation | Type safety, validation, performance |
| pyyaml | >=6.0 | YAML parsing | Standard, human-readable, comments |
| typer | >=0.9 | CLI framework | Type hints, minimal code, modern |
| rich | >=13.0 | Terminal formatting | Beautiful output, tables, panels |
| pymupdf | >=1.23.0 | PDF parsing | Fast, accurate, full-featured |
| ebooklib | >=0.18 | EPUB parsing | Standard, complete EPUB support |
| beautifulsoup4 | >=4.12.0 | HTML parsing | Robust, clean API, EPUB HTML |
| google-api-python-client | >=2.0.0 | YouTube API | Official, complete API coverage |
| youtube-transcript-api | >=0.6.0 | YouTube transcripts | Simple, free, no API key |
| pytest | >=7.0 | Testing | Industry standard, simple, powerful |
| pytest-cov | >=4.0 | Coverage | Track test coverage |
| ruff | >=0.1 | Linting/formatting | Fast, all-in-one, auto-fix |

---

**Questions about dependencies?** See the [Getting Started](GETTING_STARTED.md) guide or check the [Architecture](ARCHITECTURE.md) to understand how these fit together.
