# epub_chapter_extractor.py API Reference

> **[← Back to Development Guide](../DEVELOPMENT.md)** | **[← Back to API Index](index.md)** | **[Main README](../../README.md)**

The `EpubChapterExtractor` class extracts individual chapters from EPUB files.

## Class: EpubChapterExtractor

### `__init__(epub_path: Path)`

Initialize extractor.

```python
from pathlib import Path
from resourcelibrarian.sources.epub_chapter_extractor import EpubChapterExtractor

extractor = EpubChapterExtractor(Path("book.epub"))
```

**Parameters:**
- `epub_path` - Path to EPUB file

---

### `extract_chapters() -> list[tuple[int, str, str]]`

Extract chapters from EPUB.

```python
extractor = EpubChapterExtractor(Path("book.epub"))
chapters = extractor.extract_chapters()

# Returns:
# [
#     (1, "Introduction", "# Introduction\n\nContent..."),
#     (2, "Chapter 1: Getting Started", "# Chapter 1: Getting Started\n\nContent..."),
#     ...
# ]
```

**Returns:** List of `(chapter_number, title, markdown_content)` tuples

**How it works:**
1. Follows EPUB spine (reading order)
2. Converts HTML to Markdown
3. Skips empty/short content (< 100 characters)
4. Extracts chapter titles from headings
5. Filters out front matter (copyright, TOC, dedication, etc.)
6. Numbers chapters sequentially starting from 1

**Front Matter Detection:**

The extractor automatically skips common front matter sections:
- Title/Cover pages
- Copyright notices
- Dedications
- Table of Contents
- Acknowledgments
- Preface/Foreword
- About the Author
- Very short content (< 200 characters)

---

### `save_chapters(output_dir: Path) -> list[tuple[int, str, Path]]`

Extract and save chapters to individual files.

```python
extractor = EpubChapterExtractor(Path("book.epub"))
saved = extractor.save_chapters(Path("chapters/"))

# Returns:
# [
#     (1, "Introduction", Path("chapters/1-introduction.md")),
#     (2, "Chapter 1: Getting Started", Path("chapters/2-chapter-1-getting-started.md")),
#     ...
# ]
```

**Parameters:**
- `output_dir` - Directory to save chapter files (created if doesn't exist)

**Returns:** List of `(chapter_number, title, file_path)` tuples

**Raises:** `ValueError` if no chapters found in EPUB

**Filename Format:** `{number}-{slugified-title}.md`

**Examples:**
- "Introduction" → `1-introduction.md`
- "Chapter 1: Getting Started" → `2-chapter-1-getting-started.md`
- "Chapter 2: Advanced Topics!" → `3-chapter-2-advanced-topics.md`

**Slugification Rules:**
- Converts to lowercase
- Removes non-alphanumeric characters (except spaces/hyphens)
- Replaces spaces with hyphens
- Removes multiple consecutive hyphens

---

## HTML to Markdown Conversion

The extractor converts EPUB HTML content to clean Markdown format.

**Supported Elements:**

| HTML | Markdown | Example |
|------|----------|---------|
| `<h1>` through `<h6>` | `#` through `######` | `<h1>Title</h1>` → `# Title` |
| `<p>` | Paragraph with spacing | `<p>Text</p>` → `Text` |
| `<b>`, `<strong>` | `**bold**` | `<b>text</b>` → `**text**` |
| `<i>`, `<em>` | `*italic*` | `<i>text</i>` → `*text*` |
| `<br>` | Line break | `<br>` → `\n` |
| `<div>`, `<section>` | Container (children processed) | Content extracted |

**Cleaning:**
- Scripts and styles are removed
- Excessive whitespace is normalized (max 3 consecutive newlines)
- Multiple spaces are collapsed to single space

---

## Chapter Title Extraction

The extractor tries to find meaningful chapter titles in this order:

### 1. From First Heading
Searches the first 10 lines for markdown headings (`#`, `##`, etc.):
```markdown
# Introduction
Content...
```
Title = "Introduction"

### 2. From Filename
If no heading found, uses the EPUB item filename:
```
chapter_01_introduction.html → "Chapter 01 Introduction"
```
- Removes file extension
- Replaces underscores/hyphens with spaces
- Capitalizes words

### 3. Fallback
If neither method works:
```
Title = "Chapter {number}"
```

---

## Usage Examples

### Extract All Chapters

```python
from pathlib import Path
from resourcelibrarian.sources.epub_chapter_extractor import EpubChapterExtractor

extractor = EpubChapterExtractor(Path("python-book.epub"))
chapters = extractor.extract_chapters()

for num, title, content in chapters:
    print(f"Chapter {num}: {title}")
    print(f"Length: {len(content)} characters")
    print(f"Preview: {content[:100]}...")
    print()
```

### Save to Organized Directory

```python
extractor = EpubChapterExtractor(Path("python-book.epub"))
output_dir = Path("library/books/smith-john/python-programming/chapters")

saved_chapters = extractor.save_chapters(output_dir)

print(f"Saved {len(saved_chapters)} chapters:")
for num, title, path in saved_chapters:
    print(f"  {num}. {title}")
    print(f"     → {path}")
```

### Handle Errors

```python
from resourcelibrarian.sources.epub_chapter_extractor import EpubChapterExtractor

try:
    extractor = EpubChapterExtractor(Path("book.epub"))
    chapters = extractor.save_chapters(Path("chapters/"))
except ValueError as e:
    print(f"No chapters found: {e}")
    # EPUB might not have clear chapter structure
```

---

## See Also

- [book_parser.py](book_parser.md) - General EPUB parsing (whole book)
- [book_ingestion.py](book_ingestion.md) - Uses EpubChapterExtractor during book import
