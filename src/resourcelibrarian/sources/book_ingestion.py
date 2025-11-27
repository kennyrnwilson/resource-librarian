"""Book ingestion - add books to the resource library."""

import re
import shutil
from pathlib import Path

from resourcelibrarian.models import Book, BookManifest
from resourcelibrarian.sources.book_folder_scanner import BookFolderScanner
from resourcelibrarian.sources.book_parser import (
    BookParser,
    clean_text,
    extract_metadata_from_text,
)
from resourcelibrarian.sources.epub_chapter_extractor import EpubChapterExtractor
from resourcelibrarian.utils import compute_file_hash, save_book_manifest


def slugify(text: str) -> str:
    """Convert text to a URL-safe slug.

    Args:
        text: Text to slugify

    Returns:
        Slugified text
    """
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-")


def parse_author_name(author: str) -> tuple[str, str]:
    """Parse author name into first and last name.

    Handles various formats:
    - "John Smith" -> ("John", "Smith")
    - "Smith, John" -> ("John", "Smith")
    - "Jane Doe Jr." -> ("Jane", "Doe Jr.")
    - "Single" -> ("", "Single")

    Args:
        author: Author name

    Returns:
        Tuple of (firstname, lastname)
    """
    author = author.strip()

    # Handle "Last, First" format
    if "," in author:
        parts = author.split(",", 1)
        lastname = parts[0].strip()
        firstname = parts[1].strip()
        return (firstname, lastname)

    # Handle "First Last" format
    parts = author.split()
    if len(parts) == 0:
        return ("", "")
    elif len(parts) == 1:
        return ("", parts[0])
    else:
        # First part is firstname, rest is lastname
        firstname = parts[0]
        lastname = " ".join(parts[1:])
        return (firstname, lastname)


def create_book_folder_path(title: str, author: str) -> str:
    """Create folder path for a book.

    Args:
        title: Book title
        author: Book author

    Returns:
        Folder path in format: lastname-firstname/book-title
        Example: "smith-john/python-programming"
    """
    title_slug = slugify(title)

    # Parse author name
    firstname, lastname = parse_author_name(author)

    # Create author folder name (lastname-firstname)
    if firstname and lastname:
        author_slug = f"{slugify(lastname)}-{slugify(firstname)}"
    elif lastname:
        author_slug = slugify(lastname)
    else:
        author_slug = "unknown"

    return f"{author_slug}/{title_slug}"


class BookIngestion:
    """Handle book ingestion into the resource library."""

    def __init__(self, library_path: Path):
        """Initialize book ingestion.

        Args:
            library_path: Path to library root
        """
        self.library_path = Path(library_path)
        self.books_dir = self.library_path / "books"

    def add_book(
        self,
        file_path: Path | list[Path],
        title: str | None = None,
        author: str | None = None,
        categories: list[str] | None = None,
        tags: list[str] | None = None,
        isbn: str | None = None,
        prefer_format: str = "epub",
    ) -> Book:
        """Add a book to the library.

        Args:
            file_path: Path to book file(s). Can be single file or list of files
            title: Book title (auto-detected if not provided)
            author: Book author (auto-detected if not provided)
            categories: List of categories
            tags: List of tags
            isbn: ISBN number
            prefer_format: Preferred format for text extraction (epub, pdf, markdown)

        Returns:
            Book instance

        Raises:
            FileNotFoundError: If book file not found
            ValueError: If format unsupported or required metadata missing
        """
        # Normalize to list of paths
        file_paths = (
            [Path(file_path)] if not isinstance(file_path, list) else [Path(p) for p in file_path]
        )

        # Validate all files exist
        for fp in file_paths:
            if not fp.exists():
                raise FileNotFoundError(f"Book file not found: {fp}")

        # Determine which file to use for text extraction
        extraction_file = None
        format_priority = {"epub": 3, "pdf": 2, "markdown": 1}

        # Sort files by preferred format
        for fp in file_paths:
            fmt = BookParser.detect_format(fp)
            if fmt == prefer_format:
                extraction_file = fp
                break

        # If preferred format not found, use highest priority available
        if not extraction_file:
            extraction_file = max(
                file_paths,
                key=lambda p: format_priority.get(BookParser.detect_format(p) or "", 0),
            )

        # Parse the book content
        text_content = BookParser.parse(extraction_file)
        text_content = clean_text(text_content)

        # Extract metadata if not provided
        if not title or not author:
            # Try EPUB metadata first if available
            if extraction_file.suffix.lower() == ".epub":
                epub_metadata = BookParser.extract_epub_metadata(extraction_file)
                if not title and epub_metadata.get("title"):
                    title = epub_metadata["title"]
                if not author and epub_metadata.get("author"):
                    author = epub_metadata["author"]
                if not isbn and epub_metadata.get("isbn"):
                    isbn = epub_metadata["isbn"]

            # Fallback to text-based extraction
            if not title or not author:
                extracted_metadata = extract_metadata_from_text(text_content)
                if not title:
                    title = extracted_metadata.get("title")
                if not author:
                    author = extracted_metadata.get("author")

        # Validate required fields
        if not title:
            raise ValueError("Could not determine book title. Please provide it explicitly.")
        if not author:
            raise ValueError("Could not determine book author. Please provide it explicitly.")

        # Create folder structure
        folder_path = create_book_folder_path(title, author)
        book_folder = self.books_dir / folder_path

        if book_folder.exists():
            raise ValueError(f"Book already exists: {folder_path}")

        book_folder.mkdir(parents=True, exist_ok=True)

        # Copy all source files
        formats = {}
        for fp in file_paths:
            format_type = BookParser.detect_format(fp)
            if format_type in ["pdf", "epub"]:
                filename = f"{slugify(title)}.{format_type}"
                dest_path = book_folder / filename
                shutil.copy(fp, dest_path)
                formats[format_type] = filename

        # Save extracted text as Markdown
        md_filename = f"{slugify(title)}.md"
        md_path = book_folder / md_filename
        md_path.write_text(text_content, encoding="utf-8")
        formats["markdown"] = md_filename

        # Create manifest
        manifest = BookManifest(
            title=title,
            author=author,
            categories=categories or [],
            isbn=isbn,
            source_folder=folder_path,
            formats=formats,
            summaries={},
            tags=tags or [],
        )

        # Save manifest
        save_book_manifest(manifest, book_folder)

        # Create Book instance
        book = Book(folder_path=book_folder, manifest=manifest)

        return book

    def add_book_from_folder(
        self,
        folder_path: Path,
        title: str | None = None,
        author: str | None = None,
        categories: list[str] | None = None,
        tags: list[str] | None = None,
        isbn: str | None = None,
        prefer_format: str = "epub",
    ) -> Book:
        """Add a book from a structured folder.

        Automatically detects:
        - Book formats (folder-name.pdf, folder-name.epub, etc.)
        - Summary files (folder-name-summary-type.pdf, etc.)
        - Converts summaries to markdown if needed

        Args:
            folder_path: Path to book folder
            title: Book title (auto-detected if not provided)
            author: Book author (auto-detected if not provided)
            categories: List of categories
            tags: List of tags
            isbn: ISBN number
            prefer_format: Preferred format for text extraction

        Returns:
            Book instance

        Raises:
            ValueError: If no book formats found or metadata missing
        """
        folder_path = Path(folder_path)

        # Scan the folder
        scanner = BookFolderScanner(folder_path)
        scan_result = scanner.scan()

        if not scan_result["book_formats"]:
            raise ValueError(f"No book format files found in {folder_path}")

        # Get preferred file for text extraction
        extraction_file = scanner.get_preferred_format(scan_result["book_formats"], prefer=prefer_format)
        if not extraction_file:
            raise ValueError("No suitable format found for text extraction")

        # Parse the book content
        text_content = BookParser.parse(extraction_file)
        text_content = clean_text(text_content)

        # Extract metadata if not provided
        if not title or not author or not isbn:
            # Try EPUB metadata first if available
            if extraction_file.suffix.lower() == ".epub":
                epub_metadata = BookParser.extract_epub_metadata(extraction_file)
                if not title and epub_metadata.get("title"):
                    title = epub_metadata["title"]
                if not author and epub_metadata.get("author"):
                    author = epub_metadata["author"]
                if not isbn and epub_metadata.get("isbn"):
                    isbn = epub_metadata["isbn"]

        # Fallback to text-based extraction
        if not title or not author:
            extracted_metadata = extract_metadata_from_text(text_content)
            if not title:
                title = extracted_metadata.get("title")
            if not author:
                author = extracted_metadata.get("author")

        # Validate required fields
        if not title:
            raise ValueError("Could not determine book title. Please provide it explicitly.")
        if not author:
            raise ValueError("Could not determine book author. Please provide it explicitly.")

        # Create folder structure
        dest_folder_path = create_book_folder_path(title, author)
        book_folder = self.books_dir / dest_folder_path

        if book_folder.exists():
            raise ValueError(f"Book already exists: {dest_folder_path}")

        book_folder.mkdir(parents=True, exist_ok=True)
        summaries_dir = book_folder / "summaries"
        summaries_dir.mkdir(exist_ok=True)

        # Copy all book format files
        formats = {}

        for fmt, source_path in scan_result["book_formats"]:
            if fmt in ["md", "markdown"]:
                dest_name = f"{slugify(title)}.md"
            elif fmt == "epub":
                dest_name = f"{slugify(title)}.epub"
            elif fmt == "pdf":
                dest_name = f"{slugify(title)}.pdf"
            elif fmt == "txt":
                dest_name = f"{slugify(title)}.txt"
            else:
                continue

            dest_path = book_folder / dest_name
            shutil.copy2(source_path, dest_path)
            formats[fmt] = dest_name

        # Generate markdown if not present
        if "md" not in formats and "markdown" not in formats:
            md_dest = book_folder / f"{slugify(title)}.md"
            md_dest.write_text(text_content, encoding="utf-8")
            formats["markdown"] = f"{slugify(title)}.md"

        # Extract chapters from EPUB if available
        epub_file = None
        for fmt, path in scan_result["book_formats"]:
            if fmt == "epub":
                epub_file = path
                break

        if epub_file:
            try:
                extractor = EpubChapterExtractor(epub_file)
                chapters_dir = book_folder / "chapters"
                saved_chapters = extractor.save_chapters(chapters_dir)

                # Add chapters to formats
                for chapter_num, chapter_title, chapter_path in saved_chapters:
                    key = f"chapter-{chapter_num:02d}"
                    relative_path = chapter_path.relative_to(book_folder)
                    formats[key] = str(relative_path)
            except ValueError:
                # No chapters found, skip
                pass

        # Process summary files
        summary_manifest = {}

        for summary_type, summary_fmt, summary_path in scan_result["summaries"]:
            # Extract markdown text
            summary_text = scanner.extract_markdown_from_summary(summary_path)

            # Get output filename for markdown
            output_name = scanner.get_summary_output_name(summary_type, summary_fmt)
            output_path = summaries_dir / output_name

            # Save as markdown
            output_path.write_text(summary_text, encoding="utf-8")

            # Add to manifest
            summary_manifest[summary_type] = f"summaries/{output_name}"

        # Create manifest
        manifest = BookManifest(
            title=title,
            author=author,
            categories=categories or [],
            isbn=isbn,
            source_folder=dest_folder_path,
            formats=formats,
            summaries=summary_manifest,
            tags=tags or [],
        )

        # Save manifest
        save_book_manifest(manifest, book_folder)

        # Create Book instance
        book = Book(folder_path=book_folder, manifest=manifest)

        return book
