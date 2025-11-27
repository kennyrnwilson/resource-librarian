# book_folder_scanner.py API Reference

> **[← Back to Development Guide](../DEVELOPMENT.md)** | **[← Back to API Index](index.md)** | **[Main README](../../README.md)**

The `BookFolderScanner` class scans structured book folders to detect formats and summaries.

## Class: BookFolderScanner

### `__init__(folder_path: Path)`

Initialize scanner.

```python
from pathlib import Path
from resourcelibrarian.sources.book_folder_scanner import BookFolderScanner

scanner = BookFolderScanner(Path("/path/to/book-folder"))
```

**Parameters:**
- `folder_path` - Path to book folder

**Raises:**
- `ValueError` - If folder doesn't exist or is not a directory

---

### `scan() -> dict`

Scan folder and categorize files.

```python
scanner = BookFolderScanner(Path("/path/to/book-folder"))
result = scanner.scan()

# Returns:
# {
#     "book_formats": [("epub", Path("book.epub")), ("pdf", Path("book.pdf"))],
#     "summaries": [("shortform", "pdf", Path("book-summary-shortform.pdf"))],
#     "other_files": [Path("notes.txt")]
# }
```

**Returns:** Dictionary with:
- `book_formats` - List of `(format, path)` tuples for main book files
- `summaries` - List of `(summary_type, format, path)` tuples
- `other_files` - List of other files found

**Detection Rules:**

**Book Formats:**
- Files named `{folder-name}.{ext}` where ext is `.pdf`, `.epub`, `.md`, `.txt`
- Example: In folder `my-book/`, file `my-book.epub` is detected as book format

**Summary Files:**
- Pattern 1: `{folder-name}-summary-{type}.{ext}` → type = summary type
- Pattern 2: `{folder-name}_summary_{type}.{ext}` → type = summary type
- Pattern 3: `{folder-name}-{type}-summary.{ext}` → type = summary type

**Examples:**
- `my-book-summary-shortform.pdf` → summary type = "shortform"
- `my-book_summary_claude.md` → summary type = "claude"
- `my-book-detailed-summary.epub` → summary type = "detailed"

---

### `get_preferred_format(book_formats: list[tuple[str, Path]], prefer: str = "epub") -> Path | None`

Get preferred format for text extraction.

```python
book_formats = [("epub", Path("book.epub")), ("pdf", Path("book.pdf"))]
preferred = scanner.get_preferred_format(book_formats, prefer="epub")
# Returns: Path("book.epub")
```

**Parameters:**
- `book_formats` - List of `(format, path)` tuples
- `prefer` - Preferred format (`"epub"`, `"pdf"`, `"md"`)

**Returns:** `Path` to preferred format or `None`

**Fallback order:** epub → pdf → md → txt

If preferred format is not available, falls back to the next best format in priority order.

---

### `extract_markdown_from_summary(summary_path: Path) -> str`

Extract markdown text from summary file (any format).

```python
markdown = scanner.extract_markdown_from_summary(Path("summary.pdf"))
```

**Parameters:**
- `summary_path` - Path to summary file (md, txt, pdf, or epub)

**Returns:** Markdown text

**Raises:** `ValueError` if format unsupported

**Supported Formats:**
- `.md` - Returns content as-is
- `.txt` - Returns plain text (can be wrapped in markdown)
- `.pdf` - Extracts text using BookParser.parse_pdf()
- `.epub` - Extracts text using BookParser.parse_epub()

---

### `get_summary_output_name(summary_type: str, original_format: str) -> str`

Get output filename for summary.

```python
filename = scanner.get_summary_output_name("shortform", "pdf")
# Returns: "shortform-summary.md"
```

**Parameters:**
- `summary_type` - Type of summary (e.g., `"shortform"`, `"claude-sonnet-4.5"`)
- `original_format` - Original format (`"pdf"`, `"epub"`, `"md"`)

**Returns:** Output filename (always `.md` extension)

**Examples:**
- ("shortform", "pdf") → `"shortform-summary.md"`
- ("claude-sonnet-4.5", "epub") → `"claude-sonnet-4.5-summary.md"`
- ("detailed_notes", "txt") → `"detailed-notes-summary.md"`

**Note:** Underscores in summary type are converted to hyphens.

---

## Summary Pattern Details

The scanner recognizes three summary filename patterns:

### Pattern 1: `{book}-summary-{type}`
- Example: `python-book-summary-shortform.pdf`
- Extracts: type = "shortform"

### Pattern 2: `{book}_summary_{type}`
- Example: `python_book_summary_claude.md`
- Extracts: type = "claude"

### Pattern 3: `{book}-{type}-summary`
- Example: `python-book-detailed-summary.epub`
- Extracts: type = "detailed"

All patterns are case-insensitive and work with any supported file extension.

---

## See Also

- [book_ingestion.py](book_ingestion.md) - Uses BookFolderScanner in add_book_from_folder()
- [book_parser.py](book_parser.md) - Used for extracting text from summaries
