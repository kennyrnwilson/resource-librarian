# book_ingestion.py API Reference

> **[← Back to Development Guide](../DEVELOPMENT.md)** | **[← Back to API Index](index.md)** | **[Main README](../../README.md)**

The `BookIngestion` class handles adding books to the library with automatic organization.

## Class: BookIngestion

### `__init__(library_path: Path)`

Initialize book ingestion.

```python
from pathlib import Path
from resourcelibrarian.sources.book_ingestion import BookIngestion

ingestion = BookIngestion(library_path=Path("/path/to/library"))
```

**Parameters:**
- `library_path` - Path to library root

---

### `add_book(...)`

Add a book to the library from file(s).

```python
# Add with auto-detection
book = ingestion.add_book(
    file_path=Path("book.epub")
)

# Add with manual metadata
book = ingestion.add_book(
    file_path=Path("book.pdf"),
    title="Python Programming",
    author="John Smith",
    categories=["Programming", "Python"],
    tags=["beginner", "tutorial"]
)

# Add multiple formats
book = ingestion.add_book(
    file_path=[Path("book.epub"), Path("book.pdf")],
    prefer_format="epub"
)
```

**Parameters:**
- `file_path` - Path to book file(s). Can be single `Path` or list of `Path` objects
- `title` - Book title (optional, auto-detected if not provided)
- `author` - Book author (optional, auto-detected if not provided)
- `categories` - List of categories (optional)
- `tags` - List of tags (optional)
- `isbn` - ISBN number (optional, auto-detected from EPUB)
- `prefer_format` - Preferred format for text extraction (`"epub"`, `"pdf"`, or `"markdown"`)

**Returns:** `Book` instance

**Raises:**
- `FileNotFoundError` - If book file not found
- `ValueError` - If format unsupported or required metadata missing

**What it does:**
1. Validates files exist
2. Selects preferred format for text extraction
3. Parses content and extracts metadata
4. Creates folder structure: `lastname-firstname/book-title/`
   - `full-book-formats/` - All book file formats
   - `full-book-formats/chapters/` - Individual chapters (from EPUB)
5. Copies source files to `full-book-formats/`
6. Generates Markdown version
7. Extracts EPUB chapters to `full-book-formats/chapters/` (if applicable)
8. Creates `manifest.yaml` with format paths
9. Updates library catalog

---

### `add_book_from_folder(...)`

Add a book from a structured folder with auto-detection of formats and summaries.

```python
# Folder structure:
# my-book/
#   ├── my-book.epub
#   ├── my-book.pdf
#   ├── my-book-summary-shortform.pdf
#   └── my-book-summary-claude.md

book = ingestion.add_book_from_folder(
    folder_path=Path("/path/to/my-book"),
    categories=["Technology"],
    prefer_format="epub"
)
```

**Parameters:**
- `folder_path` - Path to book folder
- `title` - Book title (optional, auto-detected)
- `author` - Book author (optional, auto-detected)
- `categories` - List of categories (optional)
- `tags` - List of tags (optional)
- `isbn` - ISBN number (optional)
- `prefer_format` - Preferred format for text extraction

**Returns:** `Book` instance

**Raises:**
- `ValueError` - If no book formats found or metadata missing

**Folder Detection Rules:**
- Book formats: Files named `{folder-name}.{ext}` where ext is pdf, epub, md, txt
- Summary files: Match patterns like `{folder-name}-summary-{type}.{ext}`

**What it does:**
1. Scans folder for book formats and summaries
2. Extracts text from preferred format
3. Extracts metadata from EPUB or text
4. Creates organized structure in library:
   - `full-book-formats/` - All book file formats
   - `full-book-formats/chapters/` - Individual chapters (from EPUB)
   - `summaries/` - Converted summary files
5. Copies all book formats to `full-book-formats/`
6. Converts summaries to Markdown in `summaries/`
7. Extracts EPUB chapters to `full-book-formats/chapters/`
8. Creates manifest with all format paths and updates catalog

---

## Helper Functions

### `slugify(text: str) -> str`

Convert text to URL-safe slug.

```python
from resourcelibrarian.sources.book_ingestion import slugify

slug = slugify("Python Programming!")
# Returns: "python-programming"
```

**Parameters:**
- `text` - Text to slugify

**Returns:** Slugified text (lowercase, alphanumeric + hyphens)

**Transformations:**
- Converts to lowercase
- Removes non-alphanumeric characters (except spaces and hyphens)
- Replaces spaces/multiple hyphens with single hyphen
- Strips leading/trailing hyphens

---

### `parse_author_name(author: str) -> tuple[str, str]`

Parse author name into first and last name.

```python
from resourcelibrarian.sources.book_ingestion import parse_author_name

firstname, lastname = parse_author_name("John Smith")
# Returns: ("John", "Smith")

firstname, lastname = parse_author_name("Smith, John")
# Returns: ("John", "Smith")

firstname, lastname = parse_author_name("Jane Doe Jr.")
# Returns: ("Jane", "Doe Jr.")
```

**Parameters:**
- `author` - Author name in any common format

**Returns:** Tuple of `(firstname, lastname)`

**Supported Formats:**
- "First Last" → (First, Last)
- "Last, First" → (First, Last)
- Single name → ("", Name)
- Names with suffixes (Jr., Sr., III) are preserved in lastname

---

### `create_book_folder_path(title: str, author: str) -> str`

Create folder path for a book.

```python
from resourcelibrarian.sources.book_ingestion import create_book_folder_path

path = create_book_folder_path("Python Programming", "John Smith")
# Returns: "smith-john/python-programming"
```

**Parameters:**
- `title` - Book title
- `author` - Book author

**Returns:** Folder path in format: `lastname-firstname/book-title`

**Examples:**
- ("Python Programming", "John Smith") → `"smith-john/python-programming"`
- ("The Great Book", "Jane Doe Jr.") → `"doe-jr-jane/the-great-book"`
- ("Solo", "Madonna") → `"madonna/solo"`

---

## See Also

- [book_parser.py](book_parser.md) - Text extraction and metadata parsing
- [book_folder_scanner.py](book_folder_scanner.md) - Folder scanning for add_book_from_folder()
- [epub_chapter_extractor.py](epub_chapter_extractor.md) - Chapter extraction for EPUB files
