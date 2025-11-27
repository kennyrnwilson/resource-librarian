"""Index generation for Resource Librarian.

This module generates beautiful Markdown index files for navigation:
- Master indices: authors.md, titles.md, channels.md
- Individual resource indices: index.md for each book/video
"""

from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Optional

from resourcelibrarian.models.catalog import LibraryCatalog
from resourcelibrarian.models.book import Book
from resourcelibrarian.models.video import Video


class IndexGenerator:
    """Generates Markdown index files for library navigation."""

    def __init__(self, library_root: Path):
        """Initialize index generator.

        Args:
            library_root: Root path of the library
        """
        self.library_root = Path(library_root)
        self.books_index_dir = self.library_root / "books" / "_index"
        self.videos_index_dir = self.library_root / "videos" / "_index"
        self.library_index_dir = self.library_root / "_index"

    def generate_all_indices(self, catalog: LibraryCatalog) -> None:
        """Generate all index files.

        Args:
            catalog: LibraryCatalog instance
        """
        # Generate master indices
        self.generate_authors_index(catalog)
        self.generate_titles_index(catalog)
        self.generate_channels_index(catalog)
        self.generate_library_index(catalog)

        # Generate individual resource indices
        for book in catalog.books:
            self.generate_book_index(book)

        for video in catalog.videos:
            self.generate_video_index(video)

    def generate_authors_index(self, catalog: LibraryCatalog) -> None:
        """Generate books/_index/authors.md file.

        Args:
            catalog: LibraryCatalog instance
        """
        self.books_index_dir.mkdir(parents=True, exist_ok=True)

        # Group books by author
        books_by_author = defaultdict(list)
        for book in sorted(catalog.books, key=lambda b: b.title):
            books_by_author[book.author].append(book)

        # Generate markdown
        lines = [
            "# Authors Index",
            "",
            f"**Total Authors:** {len(books_by_author)}",
            f"**Total Books:** {len(catalog.books)}",
            f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "---",
            "",
        ]

        for author in sorted(books_by_author.keys()):
            books = books_by_author[author]
            lines.append(f"## {author}")
            lines.append("")
            lines.append(f"**Books:** {len(books)}")
            lines.append("")

            for book in books:
                # Create relative path from books/_index/ to the book folder
                rel_path = f"../{book.folder_path.relative_to(self.library_root / 'books')}"

                # Format book entry
                formats = book.list_formats()
                formats_str = f" [{', '.join(formats)}]" if formats else ""
                categories_str = f" · {', '.join(book.categories)}" if book.categories else ""

                lines.append(f"- **[{book.title}]({rel_path})**{formats_str}{categories_str}")

            lines.append("")

        # Write file
        (self.books_index_dir / "authors.md").write_text("\n".join(lines))

    def generate_titles_index(self, catalog: LibraryCatalog) -> None:
        """Generate books/_index/titles.md file.

        Args:
            catalog: LibraryCatalog instance
        """
        self.books_index_dir.mkdir(parents=True, exist_ok=True)

        # Sort books by title
        sorted_books = sorted(catalog.books, key=lambda b: b.title.lower())

        # Generate markdown
        lines = [
            "# Titles Index",
            "",
            f"**Total Books:** {len(catalog.books)}",
            f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "---",
            "",
        ]

        # Group by first letter
        books_by_letter = defaultdict(list)
        for book in sorted_books:
            first_letter = book.title[0].upper() if book.title else "#"
            if not first_letter.isalpha():
                first_letter = "#"
            books_by_letter[first_letter].append(book)

        for letter in sorted(books_by_letter.keys()):
            books = books_by_letter[letter]
            lines.append(f"## {letter}")
            lines.append("")

            for book in books:
                # Create relative path
                rel_path = f"../{book.folder_path.relative_to(self.library_root / 'books')}"

                # Format book entry
                formats = book.list_formats()
                formats_str = f" [{', '.join(formats)}]" if formats else ""

                lines.append(f"- **[{book.title}]({rel_path})** by {book.author}{formats_str}")

            lines.append("")

        # Write file
        (self.books_index_dir / "titles.md").write_text("\n".join(lines))

    def generate_channels_index(self, catalog: LibraryCatalog) -> None:
        """Generate videos/_index/channels.md file.

        Args:
            catalog: LibraryCatalog instance
        """
        self.videos_index_dir.mkdir(parents=True, exist_ok=True)

        # Group videos by channel
        videos_by_channel = defaultdict(list)
        for video in sorted(catalog.videos, key=lambda v: v.title):
            videos_by_channel[video.channel_title].append(video)

        # Generate markdown
        lines = [
            "# Channels Index",
            "",
            f"**Total Channels:** {len(videos_by_channel)}",
            f"**Total Videos:** {len(catalog.videos)}",
            f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "---",
            "",
        ]

        for channel in sorted(videos_by_channel.keys()):
            videos = videos_by_channel[channel]
            lines.append(f"## {channel}")
            lines.append("")
            lines.append(f"**Videos:** {len(videos)}")
            lines.append("")

            for video in videos:
                # Create relative path
                rel_path = f"../{video.folder_path.relative_to(self.library_root / 'videos')}"

                # Format video entry
                categories_str = f" · {', '.join(video.manifest.categories)}" if video.manifest.categories else ""
                published = video.published_at or "Unknown date"

                lines.append(f"- **[{video.title}]({rel_path})** ({published}){categories_str}")

            lines.append("")

        # Write file
        (self.videos_index_dir / "channels.md").write_text("\n".join(lines))

    def generate_library_index(self, catalog: LibraryCatalog) -> None:
        """Generate main library index at _index/README.md.

        Args:
            catalog: LibraryCatalog instance
        """
        self.library_index_dir.mkdir(parents=True, exist_ok=True)

        stats = catalog.get_stats()

        lines = [
            "# Library Index",
            "",
            f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Statistics",
            "",
            f"- **Total Books:** {stats['total_books']}",
            f"- **Total Videos:** {stats['total_videos']}",
            f"- **Total Items:** {stats['total_items']}",
            f"- **Unique Authors:** {stats['unique_authors']}",
            f"- **Unique Channels:** {len(catalog.videos) and len({v.channel_title for v in catalog.videos}) or 0}",
            f"- **Categories:** {stats['unique_categories']}",
            f"- **Tags:** {stats['unique_tags']}",
            "",
            "## Quick Links",
            "",
            "### Books",
            "- [Browse by Author](../books/_index/authors.md)",
            "- [Browse by Title](../books/_index/titles.md)",
            "",
            "### Videos",
            "- [Browse by Channel](../videos/_index/channels.md)",
            "",
            "## Categories",
            "",
        ]

        # List all categories with counts
        category_counts = defaultdict(int)
        for book in catalog.books:
            for cat in book.categories:
                category_counts[cat] += 1
        for video in catalog.videos:
            for cat in video.manifest.categories:
                category_counts[cat] += 1

        for category in sorted(category_counts.keys()):
            count = category_counts[category]
            lines.append(f"- **{category}** ({count} items)")

        lines.append("")
        lines.append("## Tags")
        lines.append("")

        # List all tags with counts
        tag_counts = defaultdict(int)
        for book in catalog.books:
            for tag in book.tags:
                tag_counts[tag] += 1
        for video in catalog.videos:
            for tag in video.tags:
                tag_counts[tag] += 1

        for tag in sorted(tag_counts.keys()):
            count = tag_counts[tag]
            lines.append(f"- **{tag}** ({count} items)")

        # Write file
        (self.library_index_dir / "README.md").write_text("\n".join(lines))

    def generate_book_index(self, book: Book) -> None:
        """Generate individual index.md for a book.

        Args:
            book: Book instance
        """
        lines = [
            f"# {book.title}",
            "",
            f"**Author:** {book.author}",
        ]

        if book.manifest.isbn:
            lines.append(f"**ISBN:** {book.manifest.isbn}")

        if book.categories:
            lines.append(f"**Categories:** {', '.join(book.categories)}")

        if book.tags:
            lines.append(f"**Tags:** {', '.join(book.tags)}")

        lines.extend(["", "---", ""])

        # Available formats
        formats = book.list_formats()
        if formats:
            lines.append("## Available Formats")
            lines.append("")
            for fmt in formats:
                format_path = book.get_format_path(fmt)
                if format_path and format_path.exists():
                    rel_path = format_path.relative_to(book.folder_path)
                    lines.append(f"- [{fmt.upper()}]({rel_path})")
            lines.append("")

        # Summaries
        summaries = book.list_summaries()
        if summaries:
            lines.append("## Summaries")
            lines.append("")
            for summary in summaries:
                summary_path = book.get_summary_path(summary)
                if summary_path and summary_path.exists():
                    rel_path = summary_path.relative_to(book.folder_path)
                    lines.append(f"- [{summary}]({rel_path})")
            lines.append("")

        # Metadata
        lines.extend([
            "## Metadata",
            "",
            f"- **Location:** `{book.folder_path.relative_to(self.library_root)}`",
            f"- **Manifest:** [manifest.yaml](manifest.yaml)",
            "",
        ])

        # Write file
        (book.folder_path / "index.md").write_text("\n".join(lines))

    def generate_video_index(self, video: Video) -> None:
        """Generate individual index.md for a video.

        Args:
            video: Video instance
        """
        lines = [
            f"# {video.title}",
            "",
            f"**Channel:** {video.channel_title}",
            f"**Video ID:** {video.video_id}",
        ]

        if video.published_at:
            lines.append(f"**Published:** {video.published_at}")

        if video.manifest.categories:
            lines.append(f"**Categories:** {', '.join(video.manifest.categories)}")

        if video.tags:
            lines.append(f"**Tags:** {', '.join(video.tags)}")

        lines.extend(["", "---", ""])

        # Video link
        video_url = f"https://www.youtube.com/watch?v={video.video_id}"
        lines.append(f"**Watch on YouTube:** [{video_url}]({video_url})")
        lines.append("")

        # Transcript
        transcript_path = video.get_transcript_path()
        if transcript_path and transcript_path.exists():
            rel_path = transcript_path.relative_to(video.folder_path)
            lines.append("## Transcript")
            lines.append("")
            lines.append(f"- [Full Transcript]({rel_path})")
            lines.append("")

        # Summaries
        summaries = video.list_summaries()
        if summaries:
            lines.append("## Summaries")
            lines.append("")
            for summary in summaries:
                summary_path = video.get_summary_path(summary)
                if summary_path and summary_path.exists():
                    rel_path = summary_path.relative_to(video.folder_path)
                    lines.append(f"- [{summary}]({rel_path})")
            lines.append("")

        # Metadata
        lines.extend([
            "## Metadata",
            "",
            f"- **Location:** `{video.folder_path.relative_to(self.library_root)}`",
            f"- **Manifest:** [manifest.yaml](manifest.yaml)",
            f"- **Channel ID:** {video.channel_id}",
            "",
        ])

        # Write file
        (video.folder_path / "index.md").write_text("\n".join(lines))
