"""Index generation for Resource Librarian.

This module generates beautiful Markdown index files for navigation:
- Root README.md with library overview
- Master indices: authors.md, titles.md, channels.md
- Individual resource indices: index.md for each book/video
- Channel-level indices for videos
- Category indices
"""

from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import List, Dict

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
        self.categories_dir = self.library_root / "categories"

    def generate_all_indices(self, catalog: LibraryCatalog) -> None:
        """Generate all index files.

        Args:
            catalog: LibraryCatalog instance
        """
        # Generate root README
        self.generate_root_readme(catalog)

        # Generate master indices
        self.generate_authors_index(catalog)
        self.generate_titles_index(catalog)
        self.generate_channels_index(catalog)
        self.generate_video_titles_index(catalog)

        # Generate category indices
        self.generate_category_index(catalog)

        # Generate channel-level indices
        self.generate_channel_indices(catalog)

        # Generate individual resource indices
        for book in catalog.books:
            self.generate_book_index(book)

        for video in catalog.videos:
            self.generate_video_index(video)

    def _get_timestamp(self) -> str:
        """Get formatted timestamp for index files."""
        return datetime.now().strftime("%Y-%m-%d %H:%M")

    def _count_book_formats(self, catalog: LibraryCatalog) -> int:
        """Count total book format files."""
        count = 0
        for book in catalog.books:
            count += len(book.list_formats())
        return count

    def _count_summaries(self, catalog: LibraryCatalog) -> int:
        """Count total summary files (books + videos)."""
        count = 0
        for book in catalog.books:
            count += len(book.list_summaries())
        for video in catalog.videos:
            count += len(video.list_summaries())
        return count

    def _count_chapters(self, catalog: LibraryCatalog) -> int:
        """Count total chapter files."""
        count = 0
        for book in catalog.books:
            chapters_dir = book.folder_path / "full-book-formats" / "chapters"
            if chapters_dir.exists():
                count += len(list(chapters_dir.glob("*.md")))
        return count

    def _get_recent_additions(self, catalog: LibraryCatalog, limit: int = 5) -> List[Book]:
        """Get most recently added books based on folder modification time."""
        books_with_time = []
        for book in catalog.books:
            if book.folder_path.exists():
                mtime = book.folder_path.stat().st_mtime
                books_with_time.append((book, mtime))

        # Sort by modification time, most recent first
        books_with_time.sort(key=lambda x: x[1], reverse=True)
        return [book for book, _ in books_with_time[:limit]]

    def generate_root_readme(self, catalog: LibraryCatalog) -> None:
        """Generate root README.md with polished library overview.

        Args:
            catalog: LibraryCatalog instance
        """
        stats = catalog.get_stats()
        total_formats = self._count_book_formats(catalog)
        total_summaries = self._count_summaries(catalog)
        total_chapters = self._count_chapters(catalog)
        recent_books = self._get_recent_additions(catalog)

        lines = [
            "# 📚 KnowledgeHub Library",
            "",
            "*Welcome to your personal knowledge library*",
            "",
            f"**Last updated:** {self._get_timestamp()}",
            "",
            "---",
            "",
            "## 📊 Library Statistics",
            "",
            f"- **Total Books:** {stats['total_books']}",
            f"- **Total Videos:** {stats['total_videos']}",
            f"- **Authors:** {stats['unique_authors']}",
            f"- **Book Formats:** {total_formats}",
            f"- **Summaries:** {total_summaries}",
            f"- **Chapters:** {total_chapters}",
            "",
            "---",
            "",
            "## 🗂️ Browse Your Library",
            "",
            "### 📖 Books",
            "",
            f"Browse {stats['total_books']} books in your collection:",
            "",
            "- **[Browse by Author](books/_index/authors.md)** 👤",
            "  - Books organized by author name",
            "  - See all works from each author",
            "",
            "- **[Browse by Title](books/_index/titles.md)** 🔤",
            "  - Alphabetical listing of all books",
            "  - Quick reference by book name",
            "",
        ]

        if stats["total_videos"] > 0:
            lines.extend(
                [
                    "### 🎥 Videos",
                    "",
                    f"Browse {stats['total_videos']} videos in your collection:",
                    "",
                    "- **[Browse by Channel](videos/_index/channels.md)** 📺",
                    "  - Videos organized by YouTube channel",
                    "  - See all videos from each creator",
                    "",
                    "- **[Browse by Title](videos/_index/titles.md)** 🔤",
                    "  - Alphabetical listing of all videos",
                    "  - Quick reference by video name",
                    "",
                ]
            )

        if stats["unique_categories"] > 0:
            lines.extend(
                [
                    "### 🏷️ Categories",
                    "",
                    f"Explore content across {stats['unique_categories']} categories:",
                    "",
                    "- **[Browse by Category](categories/index.md)** 🗂️",
                    "  - Find books and videos by topic",
                    "  - Discover content across your interests",
                    "",
                ]
            )

        lines.extend(
            [
                "---",
                "",
                "## 🆕 Recent Additions",
                "",
            ]
        )

        # Add recent books
        for book in recent_books:
            formats = book.list_formats()
            formats_str = ", ".join(f.upper() for f in formats)
            rel_path = f"books/{book.folder_path.relative_to(self.library_root / 'books')}/index.md"
            lines.append(f"- **[{book.title}]({rel_path})** by {book.author}")
            if formats_str:
                lines.append(f"  - *{formats_str}*")

        lines.extend(
            [
                "",
                "---",
                "",
                "## 🚀 Quick Start",
                "",
                "### For Readers",
                "",
                "1. **Browse** - Start with [Authors](books/_index/authors.md) or [Titles](books/_index/titles.md)",
                "2. **Explore** - Click on a book to see available formats and summaries",
                "3. **Read** - Access books in EPUB, PDF, or Markdown format",
                "",
                "### For Developers",
                "",
                "```bash",
                "# Search the library semantically",
                'rl search "your query here"',
                "",
                "# Ask questions with RAG",
                'rl ask "What does this book say about...?"',
                "",
                "# List books via CLI",
                "rl catalog list",
                "```",
                "",
                "---",
                "",
                "*This index was automatically generated by KnowledgeHub.*",
                "",
                "📚 Happy reading!",
                "",
            ]
        )

        # Write to root
        (self.library_root / "README.md").write_text("\n".join(lines))

    def generate_authors_index(self, catalog: LibraryCatalog) -> None:
        """Generate books/_index/authors.md file with emojis and rich formatting.

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
            "# 📚 Books by Author",
            "",
            "⬅️ [Back to Library Home](../../README.md)",
            "",
            f"*Last updated: {self._get_timestamp()}*",
            "",
            "---",
            "",
        ]

        for author in sorted(books_by_author.keys()):
            books = books_by_author[author]
            lines.extend(
                [
                    f"## {author}",
                    "",
                ]
            )

            for book in books:
                # Create relative path from books/_index/ to the book folder
                rel_path = (
                    f"../{book.folder_path.relative_to(self.library_root / 'books')}/index.md"
                )

                # Count formats, summaries, chapters
                formats = book.list_formats()
                summaries = book.list_summaries()
                chapters_dir = book.folder_path / "full-book-formats" / "chapters"
                chapter_count = len(list(chapters_dir.glob("*.md"))) if chapters_dir.exists() else 0

                lines.append(f"### [{book.title}]({rel_path})")

                # Build stats line
                stats_parts = []
                if formats:
                    stats_parts.append(f"{len(formats)} formats")
                if summaries:
                    stats_parts.append(f"{len(summaries)} summaries")
                if chapter_count > 0:
                    stats_parts.append(f"{chapter_count} chapters")

                if stats_parts:
                    lines.append(f"*{' • '.join(stats_parts)}*")
                else:
                    lines.append("")

                # Add categories if present
                if book.categories:
                    lines.append("")
                    lines.append(f"**Categories:** {', '.join(book.categories)}")

                lines.extend(["", "---", ""])

        lines.extend(
            [
                "",
                "*This index was automatically generated by KnowledgeHub.*",
                "",
            ]
        )

        # Write file
        (self.books_index_dir / "authors.md").write_text("\n".join(lines))

    def generate_titles_index(self, catalog: LibraryCatalog) -> None:
        """Generate books/_index/titles.md file with emojis and rich formatting.

        Args:
            catalog: LibraryCatalog instance
        """
        self.books_index_dir.mkdir(parents=True, exist_ok=True)

        # Sort books by title
        sorted_books = sorted(catalog.books, key=lambda b: b.title.lower())

        # Generate markdown
        lines = [
            "# 🔤 Books by Title",
            "",
            "⬅️ [Back to Library Home](../../README.md)",
            "",
            f"*Last updated: {self._get_timestamp()}*",
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
            lines.extend(
                [
                    f"## {letter}",
                    "",
                ]
            )

            for book in books:
                # Create relative path
                rel_path = (
                    f"../{book.folder_path.relative_to(self.library_root / 'books')}/index.md"
                )

                # Count formats, summaries
                formats = book.list_formats()
                summaries = book.list_summaries()

                lines.append(f"### [{book.title}]({rel_path})")
                lines.append(f"*by {book.author}*")
                lines.append("")

                # Build stats line
                stats_parts = []
                if formats:
                    stats_parts.append(f"{len(formats)} formats")
                if summaries:
                    stats_parts.append(f"{len(summaries)} summaries")

                if stats_parts:
                    lines.append(f"**{' • '.join(stats_parts)}**")
                    lines.append("")

                # Add categories if present
                if book.categories:
                    lines.append(f"**Categories:** {', '.join(book.categories)}")
                    lines.append("")

                lines.extend(["---", ""])

            lines.append("")

        lines.extend(
            [
                "",
                "*This index was automatically generated by KnowledgeHub.*",
                "",
            ]
        )

        # Write file
        (self.books_index_dir / "titles.md").write_text("\n".join(lines))

    def generate_channels_index(self, catalog: LibraryCatalog) -> None:
        """Generate videos/_index/channels.md file with emojis and rich formatting.

        Args:
            catalog: LibraryCatalog instance
        """
        if not catalog.videos:
            return

        self.videos_index_dir.mkdir(parents=True, exist_ok=True)

        # Group videos by channel
        videos_by_channel = defaultdict(list)
        channel_ids = {}  # Track channel ID for each channel title
        for video in sorted(catalog.videos, key=lambda v: v.title):
            videos_by_channel[video.channel_title].append(video)
            channel_ids[video.channel_title] = video.channel_id

        # Generate markdown
        lines = [
            "# 🎥 Videos by Channel",
            "",
            "⬅️ [Back to Library Home](../../README.md)",
            "",
            f"*Last updated: {self._get_timestamp()}*",
            "",
            "---",
            "",
        ]

        for channel in sorted(videos_by_channel.keys()):
            videos = videos_by_channel[channel]
            channel_id = channel_ids[channel]

            # Get channel folder from first video (all videos in same channel share parent folder)
            first_video = videos[0]
            channel_folder = first_video.folder_path.parent
            # Create relative path from videos/_index/ to channel folder
            # Channel folder is like: videos/channel-name__UCxxxxx
            # We're in: videos/_index/channels.md
            # So we need: ../channel-name__UCxxxxx/index.md
            channel_folder_name = channel_folder.name
            rel_channel_path = f"../{channel_folder_name}/index.md"

            lines.extend(
                [
                    f"## 📺 {channel}",
                    "",
                    f"**[📑 View Channel Index]({rel_channel_path})**",
                    "",
                    f"[View Channel on YouTube](https://www.youtube.com/channel/{channel_id})",
                    "",
                    f"**{len(videos)} video{'s' if len(videos) != 1 else ''}**",
                    "",
                ]
            )

            for video in videos:
                # Create relative path from videos/_index/channels.md to video index.md
                # We're in: videos/_index/channels.md
                # Video is at: videos/channel-folder/video-folder/index.md
                # So we need: ../channel-folder/video-folder/index.md
                channel_folder_name = video.folder_path.parent.name
                video_folder_name = video.folder_path.name
                rel_path = f"../{channel_folder_name}/{video_folder_name}/index.md"

                # Get emoji tags
                emoji_tags = " ".join(
                    [f"{cat}" for cat in video.manifest.categories if len(cat) <= 2]
                )
                if not emoji_tags:
                    emoji_tags = ""

                # Format date
                date_str = video.published_at.strftime("%b %d, %Y") if video.published_at else ""

                lines.append(f"### [{video.title}]({rel_path})")
                lines.append(f"*📅 {date_str} • {emoji_tags}*")
                lines.append("")

                # Add description if present
                if video.manifest.description:
                    desc_preview = video.manifest.description[:150]
                    if len(video.manifest.description) > 150:
                        desc_preview += "..."
                    lines.append(f"> {desc_preview}")
                    lines.append("")

                lines.extend(["---", ""])

            lines.append("")

        lines.extend(
            [
                "",
                "*This index was automatically generated by KnowledgeHub.*",
                "",
            ]
        )

        # Write file
        (self.videos_index_dir / "channels.md").write_text("\n".join(lines))

    def generate_video_titles_index(self, catalog: LibraryCatalog) -> None:
        """Generate videos/_index/titles.md file with emojis and rich formatting.

        Args:
            catalog: LibraryCatalog instance
        """
        if not catalog.videos:
            return

        self.videos_index_dir.mkdir(parents=True, exist_ok=True)

        # Sort videos by title
        sorted_videos = sorted(catalog.videos, key=lambda v: v.title.lower())

        # Generate markdown
        lines = [
            "# 🔤 Videos by Title",
            "",
            "⬅️ [Back to Library Home](../../README.md)",
            "",
            f"*Last updated: {self._get_timestamp()}*",
            "",
            "---",
            "",
        ]

        # Group by first letter
        videos_by_letter = defaultdict(list)
        for video in sorted_videos:
            first_letter = video.title[0].upper() if video.title else "#"
            if not first_letter.isalpha():
                first_letter = "#"
            videos_by_letter[first_letter].append(video)

        for letter in sorted(videos_by_letter.keys()):
            videos = videos_by_letter[letter]
            lines.extend(
                [
                    f"## {letter}",
                    "",
                ]
            )

            for video in videos:
                # Create relative path
                rel_path = (
                    f"../{video.folder_path.relative_to(self.library_root / 'videos')}/index.md"
                )

                # Get emoji tags
                emoji_tags = " ".join(
                    [f"{cat}" for cat in video.manifest.categories if len(cat) <= 2]
                )

                # Format date
                date_str = video.published_at.strftime("%b %d, %Y") if video.published_at else ""

                lines.append(f"### [{video.title}]({rel_path})")
                lines.append(f"*by {video.channel_title}*")
                lines.append("")
                lines.append(f"📅 {date_str} • {emoji_tags}")
                lines.append("")
                lines.extend(["---", ""])

            lines.append("")

        lines.extend(
            [
                "",
                "*This index was automatically generated by KnowledgeHub.*",
                "",
            ]
        )

        # Write file
        (self.videos_index_dir / "titles.md").write_text("\n".join(lines))

    def generate_channel_indices(self, catalog: LibraryCatalog) -> None:
        """Generate individual index.md files for each channel.

        The channel index.md is placed in the channel folder that contains all videos.
        This is the parent directory of the video folders.

        Args:
            catalog: LibraryCatalog instance
        """
        if not catalog.videos:
            return

        # Group videos by channel, using their folder's parent as the channel directory
        channel_dirs = {}
        videos_by_channel_dir = defaultdict(list)

        for video in catalog.videos:
            # The channel folder is the parent of the video folder
            channel_folder = video.folder_path.parent
            videos_by_channel_dir[channel_folder].append(video)
            # Store channel metadata from the first video in that folder
            if channel_folder not in channel_dirs:
                channel_dirs[channel_folder] = {
                    "title": video.channel_title,
                    "id": video.channel_id,
                }

        for channel_dir, videos in videos_by_channel_dir.items():
            channel_info = channel_dirs[channel_dir]
            channel_title = channel_info["title"]
            channel_id = channel_info["id"]

            # Sort videos by date, most recent first
            sorted_videos = sorted(
                videos,
                key=lambda v: v.published_at if v.published_at else datetime.min,
                reverse=True,
            )

            lines = [
                f"# 📺 {channel_title}",
                "",
                "⬅️ [Back to Videos](../_index/channels.md) • [🏠 Library Home](../../README.md)",
                "",
                f"[View Channel on YouTube](https://www.youtube.com/channel/{channel_id})",
                "",
                f"**{len(videos)} video{'s' if len(videos) != 1 else ''} in collection**",
                "",
                f"*Last updated: {self._get_timestamp()}*",
                "",
                "---",
                "",
            ]

            for video in sorted_videos:
                # Create relative path from channel index to video index
                # We're in: videos/channel-folder/index.md
                # Video is at: videos/channel-folder/video-folder/index.md
                # So we need: video-folder/index.md (just the video folder name)
                rel_path = f"{video.folder_path.name}/index.md"

                # Get emoji tags
                emoji_tags = " ".join(
                    [f"{cat}" for cat in video.manifest.categories if len(cat) <= 2]
                )

                # Format date
                date_str = video.published_at.strftime("%b %d, %Y") if video.published_at else ""

                lines.append(f"## [{video.title}]({rel_path})")
                lines.append("")
                lines.append(f"📅 {date_str} • {emoji_tags}")
                lines.append("")

                # Add description
                if video.manifest.description:
                    desc_preview = video.manifest.description[:200]
                    if len(video.manifest.description) > 200:
                        desc_preview += "..."
                    lines.append(f"> {desc_preview}")
                    lines.append("")

                # Add video link
                lines.append(
                    f"[Watch on YouTube](https://www.youtube.com/watch?v={video.video_id})"
                )
                lines.append("")
                lines.extend(["---", ""])

            lines.extend(
                [
                    "",
                    "*This index was automatically generated by KnowledgeHub.*",
                    "",
                ]
            )

            # Write index.md to the channel directory (parent of video folders)
            (channel_dir / "index.md").write_text("\n".join(lines))

    def generate_category_index(self, catalog: LibraryCatalog) -> None:
        """Generate categories/index.md with all categories.

        Args:
            catalog: LibraryCatalog instance
        """
        self.categories_dir.mkdir(parents=True, exist_ok=True)

        # Collect all categories with their resources
        category_items: Dict[str, List] = defaultdict(list)

        for book in catalog.books:
            for cat in book.categories:
                category_items[cat].append(("book", book))

        for video in catalog.videos:
            for cat in video.manifest.categories:
                category_items[cat].append(("video", video))

        if not category_items:
            return

        lines = [
            "# 🏷️ Browse by Category",
            "",
            "⬅️ [Back to Library Home](../README.md)",
            "",
            f"*Last updated: {self._get_timestamp()}*",
            "",
            f"**{len(category_items)} categories** • **{sum(len(items) for items in category_items.values())} items**",
            "",
            "---",
            "",
        ]

        for category in sorted(category_items.keys()):
            items = category_items[category]
            book_count = sum(1 for t, _ in items if t == "book")
            video_count = sum(1 for t, _ in items if t == "video")

            lines.append(f"## {category}")
            lines.append("")
            lines.append(f"📚 {book_count} books • 🎥 {video_count} videos")
            lines.append("")

            # List books
            if book_count > 0:
                lines.append("### Books")
                lines.append("")
                for item_type, item in items:
                    if item_type == "book":
                        rel_path = f"../books/{item.folder_path.relative_to(self.library_root / 'books')}/index.md"
                        lines.append(f"- **[{item.title}]({rel_path})** by {item.author}")
                lines.append("")

            # List videos
            if video_count > 0:
                lines.append("### Videos")
                lines.append("")
                for item_type, item in items:
                    if item_type == "video":
                        rel_path = f"../videos/{item.folder_path.relative_to(self.library_root / 'videos')}/index.md"
                        lines.append(f"- **[{item.title}]({rel_path})** by {item.channel_title}")
                lines.append("")

            lines.extend(["---", ""])

        lines.extend(
            [
                "",
                "*This index was automatically generated by KnowledgeHub.*",
                "",
            ]
        )

        # Write file
        (self.categories_dir / "index.md").write_text("\n".join(lines))

    def generate_book_index(self, book: Book) -> None:
        """Generate individual index.md for a book with rich formatting.

        Args:
            book: Book instance
        """
        lines = [
            f"# {book.title}",
            "",
            f"**Author:** {book.author}",
            "",
            "---",
            "",
            "**Browse:** [📚 Library Home](../../../README.md) • [👤 By Author](../../_index/authors.md) • [🔤 By Title](../../_index/titles.md) • [🏷️ By Category](../../../categories/index.md)",
            "",
            "---",
            "",
        ]

        # Metadata section
        lines.append("## Metadata")
        lines.append("")

        if book.categories:
            cat_links = [
                f"[{cat}](../../../categories/index.md#{cat.lower().replace(' ', '-')})"
                for cat in book.categories
            ]
            lines.append(f"**Categories:** {', '.join(cat_links)}")
            lines.append("")

        # Full book formats
        formats = book.list_formats()
        if formats:
            lines.append("## Full Book Formats")
            lines.append("")
            for fmt in formats:
                format_path = book.get_format_path(fmt)
                if format_path and format_path.exists():
                    rel_path = format_path.relative_to(book.folder_path)
                    lines.append(f"- **{fmt.upper()}**: [{format_path.name}]({rel_path})")
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
                    # Clean up the summary name for display
                    display_name = summary_path.stem.replace("-", " ").title()
                    lines.append(f"- **{display_name}**: [{summary_path.name}]({rel_path})")
            lines.append("")

        # Chapters
        chapters_dir = book.folder_path / "full-book-formats" / "chapters"
        if chapters_dir.exists():
            chapter_files = sorted(chapters_dir.glob("*.md"))
            if chapter_files:
                lines.append("## Chapters")
                lines.append("")
                lines.append(f"This book has **{len(chapter_files)} chapters**.")
                lines.append("")
                lines.append(
                    "Chapters are available in the [`full-book-formats/chapters/`](full-book-formats/chapters/) directory."
                )
                lines.append("")

        lines.extend(
            [
                "---",
                "",
                "*This index was automatically generated by KnowledgeHub.*",
                "",
            ]
        )

        # Write file
        (book.folder_path / "index.md").write_text("\n".join(lines))

    def generate_video_index(self, video: Video) -> None:
        """Generate individual index.md for a video with rich formatting.

        Args:
            video: Video instance
        """
        lines = [
            f"# {video.title}",
            "",
            f"**Channel:** {video.channel_title}",
            "",
            "---",
            "",
            "**Browse:** [📚 Library Home](../../../README.md) • [📺 By Channel](../../_index/channels.md) • [🔤 By Title](../../_index/titles.md) • [🏷️ By Category](../../../categories/index.md)",
            "",
            "---",
            "",
        ]

        # Metadata section
        lines.append("## Metadata")
        lines.append("")

        if video.published_at:
            lines.append(f"**Published:** {video.published_at.strftime('%B %d, %Y')}")
            lines.append("")

        if video.manifest.categories:
            cat_links = [
                f"[{cat}](../../../categories/index.md#{cat.lower().replace(' ', '-')})"
                for cat in video.manifest.categories
            ]
            lines.append(f"**Categories:** {', '.join(cat_links)}")
            lines.append("")

        # Video link
        video_url = f"https://www.youtube.com/watch?v={video.video_id}"
        lines.append(f"🎥 **[Watch on YouTube]({video_url})**")
        lines.append("")

        # Description
        if video.manifest.description:
            lines.append("## Description")
            lines.append("")
            lines.append(f"> {video.manifest.description}")
            lines.append("")

        # Transcript
        transcript_path = video.get_transcript_path()
        if transcript_path and transcript_path.exists():
            rel_path = transcript_path.relative_to(video.folder_path)
            lines.append("## Transcript")
            lines.append("")
            lines.append(f"- **Full Transcript**: [{transcript_path.name}]({rel_path})")
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
                    display_name = summary_path.stem.replace("-", " ").title()
                    lines.append(f"- **{display_name}**: [{summary_path.name}]({rel_path})")
            lines.append("")

        lines.extend(
            [
                "---",
                "",
                "*This index was automatically generated by KnowledgeHub.*",
                "",
            ]
        )

        # Write file
        (video.folder_path / "index.md").write_text("\n".join(lines))
