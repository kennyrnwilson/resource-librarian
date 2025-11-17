"""Data models for Resource Librarian.

This module provides Pydantic models for:
- Base enums (SourceKind)
- Book metadata and manifests
- Video metadata and manifests
- Library catalog entries
"""

from resourcelibrarian.models.base import SourceKind

__all__ = ["SourceKind"]
