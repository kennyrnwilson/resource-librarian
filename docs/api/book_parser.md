# book_parser.py API Reference

> **[← Back to Development Guide](../DEVELOPMENT.md)** | **[← Back to API Index](index.md)** | **[Main README](../../README.md)**

The `BookParser` class provides methods for extracting text from various book formats and extracting metadata.

## Class Methods

### `BookParser.parse(file_path: Path) -> str`

Auto-detects format and extracts text from a book file.

```python
from pathlib import Path
from resourcelibrarian.sources.book_parser import BookParser

# Parse any supported format
text = BookParser.parse(Path("book.epub"))
```

**Parameters:**
- `file_path` - Path to book file (PDF, EPUB, or Markdown)

**Returns:** Extracted text content as string

**Raises:** `ValueError` if format is unsupported

---

### `BookParser.detect_format(file_path: Path) -> str | None`

Detect book format from file extension.

```python
format_type = BookParser.detect_format(Path("book.epub"))
# Returns: "epub"
```

**Parameters:**
- `file_path` - Path to book file

**Returns:** Format string (`'pdf'`, `'epub'`, `'markdown'`) or `None` if unsupported

---

### `BookParser.parse_pdf(file_path: Path) -> str`

Extract text from a PDF file using PyMuPDF.

```python
text = BookParser.parse_pdf(Path("book.pdf"))
```

**Parameters:**
- `file_path` - Path to PDF file

**Returns:** Extracted text content

**Note:** Pages are separated by double newlines

---

### `BookParser.parse_epub(file_path: Path) -> str`

Extract text from an EPUB file and convert to Markdown.

```python
text = BookParser.parse_epub(Path("book.epub"))
```

**Parameters:**
- `file_path` - Path to EPUB file

**Returns:** Extracted text content in Markdown format

**Note:** HTML content is converted to Markdown preserving headings, bold, italic, etc.

---

### `BookParser.parse_markdown(file_path: Path) -> str`

Read text from a Markdown file.

```python
text = BookParser.parse_markdown(Path("book.md"))
```

**Parameters:**
- `file_path` - Path to Markdown file

**Returns:** File content as-is

---

### `BookParser.extract_epub_metadata(file_path: Path) -> dict[str, str | None]`

Extract metadata from EPUB file using Dublin Core metadata.

```python
metadata = BookParser.extract_epub_metadata(Path("book.epub"))
# Returns: {
#     "title": "Python Programming",
#     "author": "John Smith",
#     "publisher": "Tech Books Inc",
#     "language": "en",
#     "isbn": "978-1234567890"
# }
```

**Parameters:**
- `file_path` - Path to EPUB file

**Returns:** Dictionary with keys: `title`, `author`, `publisher`, `language`, `isbn` (values are `None` if not found)

---

## Utility Functions

### `clean_text(text: str) -> str`

Clean extracted text by removing excessive whitespace.

```python
from resourcelibrarian.sources.book_parser import clean_text

cleaned = clean_text(raw_text)
```

**Parameters:**
- `text` - Raw extracted text

**Returns:** Cleaned text with normalized whitespace

**Transformations:**
- Removes more than 2 consecutive newlines
- Strips leading/trailing whitespace from each line

---

### `extract_metadata_from_text(text: str) -> dict[str, str | None]`

Try to extract basic metadata from text content using pattern matching.

```python
from resourcelibrarian.sources.book_parser import extract_metadata_from_text

metadata = extract_metadata_from_text(book_text)
# Returns: {"title": "...", "author": "..."}
```

**Parameters:**
- `text` - Book text content

**Returns:** Dictionary with `title` and `author` keys (values are `None` if not found)

**How it works:**
- Analyzes first 20 lines of text
- Matches author patterns like "by John Smith" or "Author: John Smith"
- Finds title from first substantial line (5-100 chars, has capital letters)
- Skips common front matter (Praise, Dedication, Copyright, etc.)

---

## See Also

- [book_ingestion.py](book_ingestion.md) - Uses BookParser for text extraction
- [book_folder_scanner.py](book_folder_scanner.md) - Uses BookParser for summary extraction
- [epub_chapter_extractor.py](epub_chapter_extractor.md) - Related EPUB processing
