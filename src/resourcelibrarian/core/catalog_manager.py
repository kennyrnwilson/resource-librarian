"""Catalog management for Resource Librarian.

This module provides functionality for:
- Saving and updating the library catalog
- Rebuilding catalog from filesystem
- Managing catalog metadata
"""

from pathlib import Path
from datetime import datetime
from typing import Optional

from resourcelibrarian.models.catalog import LibraryCatalog
from resourcelibrarian.models.book import Book
from resourcelibrarian.models.video import Video
from resourcelibrarian.utils.io import save_yaml, load_yaml


class CatalogManager:
    """Manages library catalog operations."""

    def __init__(self, library_root: Path):
        """Initialize catalog manager.

        Args:
            library_root: Root path of the library
        """
        self.library_root = Path(library_root)
        self.catalog_path = self.library_root / "catalog.yaml"
        self.books_dir = self.library_root / "books"
        self.videos_dir = self.library_root / "videos"

    def save_catalog(self, catalog: LibraryCatalog) -> None:
        """Save catalog to disk as YAML.

        Args:
            catalog: LibraryCatalog instance to save
        """
        # Update last_updated timestamp
        catalog.last_updated = datetime.now().isoformat()

        # Build catalog data
        catalog_data = {
            "version": "1.0",
            "last_updated": catalog.last_updated,
            "books": [
                {
                    "title": book.title,
                    "author": book.author,
                    "folder_path": str(book.folder_path),
                    "categories": book.categories,
                    "tags": book.tags,
                }
                for book in catalog.books
            ],
            "videos": [
                {
                    "video_id": video.video_id,
                    "title": video.title,
                    "channel_id": video.channel_id,
                    "channel_title": video.channel_title,
                    "folder_path": str(video.folder_path),
                    "categories": video.manifest.categories,
                    "tags": video.tags,
                    "published_at": video.published_at,
                }
                for video in catalog.videos
            ],
            "stats": catalog.get_stats(),
        }

        # Save as YAML
        save_yaml(catalog_data, self.catalog_path)

    def load_catalog(self) -> LibraryCatalog:
        """Load catalog from disk.

        Returns:
            LibraryCatalog instance

        Raises:
            FileNotFoundError: If catalog file doesn't exist
        """
        if not self.catalog_path.exists():
            # Return empty catalog if file doesn't exist
            return LibraryCatalog(
                books=[],
                videos=[],
                library_path=self.library_root,
                last_updated=None,
            )

        catalog_data = load_yaml(self.catalog_path)

        # Load books
        books = []
        for book_data in catalog_data.get("books", []):
            folder_path = Path(book_data["folder_path"])
            if folder_path.exists():
                books.append(Book.from_folder(folder_path))

        # Load videos
        videos = []
        for video_data in catalog_data.get("videos", []):
            folder_path = Path(video_data["folder_path"])
            if folder_path.exists():
                videos.append(Video.from_folder(folder_path))

        return LibraryCatalog(
            books=books,
            videos=videos,
            library_path=self.library_root,
            last_updated=catalog_data.get("last_updated"),
        )

    def rebuild_catalog(self) -> LibraryCatalog:
        """Rebuild catalog by scanning the filesystem.

        Scans books/ and videos/ directories to find all resources
        and rebuilds the catalog from scratch.

        Returns:
            Rebuilt LibraryCatalog instance
        """
        books = []
        videos = []

        # Scan books directory
        if self.books_dir.exists():
            for author_dir in self.books_dir.iterdir():
                # Skip _index directory
                if author_dir.name == "_index" or not author_dir.is_dir():
                    continue

                # Scan each book folder
                for book_dir in author_dir.iterdir():
                    if not book_dir.is_dir():
                        continue

                    manifest_path = book_dir / "manifest.yaml"
                    if manifest_path.exists():
                        try:
                            book = Book.from_folder(book_dir)
                            books.append(book)
                        except Exception as e:
                            # Log error but continue scanning
                            print(f"Warning: Failed to load book from {book_dir}: {e}")
                            continue

        # Scan videos directory
        if self.videos_dir.exists():
            for channel_dir in self.videos_dir.iterdir():
                # Skip _index directory
                if channel_dir.name == "_index" or not channel_dir.is_dir():
                    continue

                # Scan each video folder
                for video_dir in channel_dir.iterdir():
                    if not video_dir.is_dir():
                        continue

                    manifest_path = video_dir / "manifest.yaml"
                    if manifest_path.exists():
                        try:
                            video = Video.from_folder(video_dir)
                            videos.append(video)
                        except Exception as e:
                            # Log error but continue scanning
                            print(f"Warning: Failed to load video from {video_dir}: {e}")
                            continue

        # Create and save catalog
        catalog = LibraryCatalog(
            books=books,
            videos=videos,
            library_path=self.library_root,
            last_updated=datetime.now().isoformat(),
        )

        self.save_catalog(catalog)
        return catalog

    def add_book(self, book: Book) -> None:
        """Add a book to the catalog.

        Args:
            book: Book instance to add
        """
        catalog = self.load_catalog()

        # Check if book already exists (by folder path)
        existing = next(
            (b for b in catalog.books if b.folder_path == book.folder_path),
            None
        )

        if existing:
            # Update existing book
            catalog.books = [b if b.folder_path != book.folder_path else book for b in catalog.books]
        else:
            # Add new book
            catalog.books.append(book)

        self.save_catalog(catalog)

    def add_video(self, video: Video) -> None:
        """Add a video to the catalog.

        Args:
            video: Video instance to add
        """
        catalog = self.load_catalog()

        # Check if video already exists (by video_id)
        existing = next(
            (v for v in catalog.videos if v.video_id == video.video_id),
            None
        )

        if existing:
            # Update existing video
            catalog.videos = [v if v.video_id != video.video_id else video for v in catalog.videos]
        else:
            # Add new video
            catalog.videos.append(video)

        self.save_catalog(catalog)

    def remove_book(self, folder_path: Path) -> bool:
        """Remove a book from the catalog.

        Args:
            folder_path: Path to the book folder

        Returns:
            True if book was removed, False if not found
        """
        catalog = self.load_catalog()
        original_count = len(catalog.books)

        catalog.books = [b for b in catalog.books if b.folder_path != folder_path]

        if len(catalog.books) < original_count:
            self.save_catalog(catalog)
            return True
        return False

    def remove_video(self, video_id: str) -> bool:
        """Remove a video from the catalog.

        Args:
            video_id: YouTube video ID

        Returns:
            True if video was removed, False if not found
        """
        catalog = self.load_catalog()
        original_count = len(catalog.videos)

        catalog.videos = [v for v in catalog.videos if v.video_id != video_id]

        if len(catalog.videos) < original_count:
            self.save_catalog(catalog)
            return True
        return False
