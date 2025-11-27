"""Base models and enums for Resource Librarian."""

from enum import Enum


class SourceKind(str, Enum):
    """Type of resource source."""

    BOOK = "book"
    VIDEO = "video"
