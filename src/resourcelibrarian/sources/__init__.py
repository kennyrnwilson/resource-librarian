"""Source ingestion modules for books and videos.

This module provides functionality for:
- Parsing PDF, EPUB, and Markdown book files
- Extracting chapters from EPUB files
- Scanning book folders for formats and summaries
- Ingesting books into the library
"""

from resourcelibrarian.sources.book_ingestion import BookIngestion
from resourcelibrarian.sources.book_parser import BookParser, clean_text, extract_metadata_from_text
from resourcelibrarian.sources.epub_chapter_extractor import EpubChapterExtractor

__all__ = [
    "BookParser",
    "clean_text",
    "extract_metadata_from_text",
    "EpubChapterExtractor",
    "BookIngestion",
]
