"""Book models for Resource Librarian."""

from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field


class BookManifest(BaseModel):
    """Manifest file for a book source.

    Stores metadata and file paths for a book in the library.
    Serialized to/from YAML in the book's manifest.yaml file.
    """

    title: str
    author: str
    categories: list[str] = Field(default_factory=list)
    isbn: Optional[str] = None
    source_folder: str

    # File paths (relative to book folder)
    formats: dict[str, str] = Field(default_factory=dict)
    summaries: dict[str, str] = Field(default_factory=dict)

    tags: list[str] = Field(default_factory=list)
    embedding_status: str = "pending"  # pending, ready, error

    model_config = {"json_encoders": {Path: str}}

    def to_yaml_dict(self) -> dict[str, Any]:
        """Convert to YAML-serializable dictionary.

        Returns:
            Dictionary suitable for YAML serialization
        """
        return {
            "title": self.title,
            "author": self.author,
            "categories": self.categories,
            "isbn": self.isbn,
            "source_folder": self.source_folder,
            "formats": self.formats,
            "summaries": self.summaries,
            "tags": self.tags,
            "embedding_status": self.embedding_status,
        }


class Book(BaseModel):
    """Represents a book in the resource library.

    Combines the book's folder path with its manifest data,
    providing convenience methods for accessing book files.
    """

    folder_path: Path
    manifest: BookManifest

    model_config = {"arbitrary_types_allowed": True}

    @property
    def title(self) -> str:
        """Book title from manifest."""
        return self.manifest.title

    @property
    def author(self) -> str:
        """Book author from manifest."""
        return self.manifest.author

    @property
    def categories(self) -> list[str]:
        """Book categories from manifest."""
        return self.manifest.categories

    @property
    def tags(self) -> list[str]:
        """Book tags from manifest."""
        return self.manifest.tags

    @property
    def source_folder(self) -> str:
        """Source folder name from manifest."""
        return self.manifest.source_folder

    def get_format_path(self, format_type: str) -> Optional[Path]:
        """Get absolute path to a specific format file.

        Args:
            format_type: Format type (e.g., 'pdf', 'epub', 'markdown')

        Returns:
            Absolute path to the format file, or None if not found
        """
        if format_type in self.manifest.formats:
            rel_path = self.manifest.formats[format_type]
            return self.folder_path / rel_path
        return None

    def get_summary_path(self, summary_type: str) -> Optional[Path]:
        """Get absolute path to a specific summary file.

        Args:
            summary_type: Summary type (e.g., 'shortform', 'ai_claude_sonnet_4_5')

        Returns:
            Absolute path to the summary file, or None if not found
        """
        if summary_type in self.manifest.summaries:
            rel_path = self.manifest.summaries[summary_type]
            return self.folder_path / rel_path
        return None

    def list_formats(self) -> list[str]:
        """List available format types.

        Returns:
            List of format type names
        """
        return list(self.manifest.formats.keys())

    def list_summaries(self) -> list[str]:
        """List available summary types.

        Returns:
            List of summary type names
        """
        return list(self.manifest.summaries.keys())

    @classmethod
    def from_folder(cls, folder_path: Path) -> "Book":
        """Load a book from its folder.

        Args:
            folder_path: Path to book folder containing manifest.yaml

        Returns:
            Book instance

        Raises:
            FileNotFoundError: If folder or manifest doesn't exist
        """
        # Import here to avoid circular dependency
        from resourcelibrarian.utils.io import load_book_manifest

        if not folder_path.exists():
            raise FileNotFoundError(f"Book folder not found: {folder_path}")

        manifest = load_book_manifest(folder_path)
        return cls(folder_path=folder_path, manifest=manifest)
