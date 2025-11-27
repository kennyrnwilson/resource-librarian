"""Catalog models for Resource Librarian."""

from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field

from .book import Book
from .video import Video


class LibraryCatalog(BaseModel):
    """Complete catalog of all books and videos in the library.

    The catalog provides a central index for all resources, supporting
    search and filtering operations across the entire library.
    """

    books: list[Book] = Field(default_factory=list)
    videos: list[Video] = Field(default_factory=list)
    library_path: Optional[Path] = None
    last_updated: Optional[str] = None

    model_config = {"arbitrary_types_allowed": True}

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization.

        Returns:
            Dictionary representation suitable for JSON serialization
        """
        return {
            "books": [
                {
                    "folder_path": str(book.folder_path),
                    "manifest": book.manifest.to_yaml_dict(),
                }
                for book in self.books
            ],
            "videos": [
                {
                    "folder_path": str(video.folder_path),
                    "manifest": video.manifest.to_yaml_dict(),
                }
                for video in self.videos
            ],
            "library_path": str(self.library_path) if self.library_path else None,
            "last_updated": self.last_updated,
            "stats": {
                "total_books": len(self.books),
                "total_videos": len(self.videos),
                "total_items": len(self.books) + len(self.videos),
            },
        }

    def find_book(self, title: str) -> Optional[Book]:
        """Find a book by title (case-insensitive).

        Args:
            title: Book title to search for

        Returns:
            Book instance if found, None otherwise
        """
        title_lower = title.lower()
        for book in self.books:
            if book.title.lower() == title_lower:
                return book
        return None

    def find_video(self, video_id: str) -> Optional[Video]:
        """Find a video by YouTube video ID.

        Args:
            video_id: YouTube video ID

        Returns:
            Video instance if found, None otherwise
        """
        for video in self.videos:
            if video.video_id == video_id:
                return video
        return None

    def search_books(
        self,
        author: Optional[str] = None,
        category: Optional[str] = None,
        tag: Optional[str] = None,
        title: Optional[str] = None,
    ) -> list[Book]:
        """Search books with optional filters.

        Args:
            author: Filter by author (case-insensitive substring match)
            category: Filter by category (case-insensitive substring match)
            tag: Filter by tag (case-insensitive substring match)
            title: Filter by title (case-insensitive substring match)

        Returns:
            List of matching Book instances
        """
        results = []

        for book in self.books:
            # Check author filter
            if author and author.lower() not in book.author.lower():
                continue

            # Check category filter
            if category:
                if not any(category.lower() in cat.lower() for cat in book.categories):
                    continue

            # Check tag filter
            if tag:
                if not any(tag.lower() in t.lower() for t in book.tags):
                    continue

            # Check title filter
            if title and title.lower() not in book.title.lower():
                continue

            results.append(book)

        return results

    def search_videos(
        self,
        channel: Optional[str] = None,
        category: Optional[str] = None,
        tag: Optional[str] = None,
        title: Optional[str] = None,
    ) -> list[Video]:
        """Search videos with optional filters.

        Args:
            channel: Filter by channel title (case-insensitive substring match)
            category: Filter by category (case-insensitive substring match)
            tag: Filter by tag (case-insensitive substring match)
            title: Filter by title (case-insensitive substring match)

        Returns:
            List of matching Video instances
        """
        results = []

        for video in self.videos:
            # Check channel filter
            if channel and channel.lower() not in video.channel_title.lower():
                continue

            # Check category filter
            if category:
                if not any(category.lower() in cat.lower() for cat in video.manifest.categories):
                    continue

            # Check tag filter
            if tag:
                if not any(tag.lower() in t.lower() for t in video.tags):
                    continue

            # Check title filter
            if title and title.lower() not in video.title.lower():
                continue

            results.append(video)

        return results

    def get_all_authors(self) -> list[str]:
        """Get sorted list of unique authors.

        Returns:
            Sorted list of unique author names
        """
        authors = {book.author for book in self.books}
        return sorted(authors)

    def get_all_categories(self) -> list[str]:
        """Get sorted list of unique categories from all resources.

        Returns:
            Sorted list of unique category names
        """
        categories = set()

        for book in self.books:
            categories.update(book.categories)

        for video in self.videos:
            categories.update(video.manifest.categories)

        return sorted(categories)

    def get_all_tags(self) -> list[str]:
        """Get sorted list of unique tags from all resources.

        Returns:
            Sorted list of unique tag names
        """
        tags = set()

        for book in self.books:
            tags.update(book.tags)

        for video in self.videos:
            tags.update(video.tags)

        return sorted(tags)

    def get_stats(self) -> dict[str, Any]:
        """Get library statistics.

        Returns:
            Dictionary with various library statistics
        """
        total_book_formats = sum(len(book.list_formats()) for book in self.books)
        total_book_summaries = sum(len(book.list_summaries()) for book in self.books)
        total_video_summaries = sum(len(video.list_summaries()) for video in self.videos)

        return {
            "total_books": len(self.books),
            "total_videos": len(self.videos),
            "total_items": len(self.books) + len(self.videos),
            "unique_authors": len(self.get_all_authors()),
            "unique_categories": len(self.get_all_categories()),
            "unique_tags": len(self.get_all_tags()),
            "book_formats": total_book_formats,
            "book_summaries": total_book_summaries,
            "video_summaries": total_video_summaries,
            "last_updated": self.last_updated,
        }
