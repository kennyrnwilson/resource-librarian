"""Utility functions for Resource Librarian.

This module provides:
- I/O operations for YAML and JSON files
- Content hashing for file integrity
"""

from resourcelibrarian.utils.hash import (
    compute_file_hash,
    compute_text_hash,
    short_hash,
)
from resourcelibrarian.utils.io import (
    load_book_manifest,
    load_json,
    load_video_manifest,
    load_yaml,
    save_book_manifest,
    save_json,
    save_video_manifest,
    save_yaml,
)

__all__ = [
    # I/O functions
    "load_yaml",
    "save_yaml",
    "load_json",
    "save_json",
    "load_book_manifest",
    "save_book_manifest",
    "load_video_manifest",
    "save_video_manifest",
    # Hash functions
    "compute_text_hash",
    "compute_file_hash",
    "short_hash",
]
