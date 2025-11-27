"""Scan and import books from structured folders with summaries."""

import re
from pathlib import Path

from resourcelibrarian.sources.book_parser import BookParser


class BookFolderScanner:
    """Scan a book folder and detect formats, summaries, and other files."""

    # Summary type patterns
    SUMMARY_PATTERNS = [
        r"^(.+?)-summary-(.+)$",  # book-summary-type
        r"^(.+?)_summary_(.+)$",  # book_summary_type
        r"^(.+?)-(.+?)-summary$",  # book-type-summary
    ]

    def __init__(self, folder_path: Path):
        """Initialize scanner.

        Args:
            folder_path: Path to book folder

        Raises:
            ValueError: If folder doesn't exist or is not a directory
        """
        self.folder_path = Path(folder_path)
        if not self.folder_path.exists():
            raise ValueError(f"Folder does not exist: {folder_path}")
        if not self.folder_path.is_dir():
            raise ValueError(f"Not a directory: {folder_path}")

        self.folder_name = self.folder_path.name

    def scan(self) -> dict[str, list]:
        """Scan folder and categorize files.

        Returns:
            Dict with:
                - book_formats: List of (format, path) for main book files
                - summaries: List of (summary_type, format, path) for summaries
                - other_files: List of other files found
        """
        result = {
            "book_formats": [],
            "summaries": [],
            "other_files": [],
        }

        for file_path in self.folder_path.iterdir():
            if not file_path.is_file():
                continue

            # Get stem and extension
            stem = file_path.stem
            ext = file_path.suffix.lower()

            # Check if it's a book format file (folder-name.ext)
            if stem.lower() == self.folder_name.lower():
                if ext in [".pdf", ".epub", ".md", ".txt"]:
                    format_name = ext[1:]  # Remove the dot
                    result["book_formats"].append((format_name, file_path))
                else:
                    result["other_files"].append(file_path)
                continue

            # Check if it's a summary file
            summary_info = self._parse_summary_filename(stem, ext)
            if summary_info:
                result["summaries"].append(summary_info + (file_path,))
                continue

            # Everything else
            result["other_files"].append(file_path)

        return result

    def _parse_summary_filename(self, stem: str, ext: str) -> tuple[str, str] | None:
        """Parse summary filename to extract type.

        Args:
            stem: Filename without extension
            ext: File extension (with dot)

        Returns:
            Tuple of (summary_type, format) or None
        """
        # Try each pattern
        for pattern in self.SUMMARY_PATTERNS:
            match = re.match(pattern, stem, re.IGNORECASE)
            if match:
                # Extract the summary type (second group)
                summary_type = match.group(2)

                # Clean up the summary type
                summary_type = summary_type.replace("_", "-").lower()

                # Remove any file extension from summary type
                for file_ext in [".pdf", ".epub", ".md", ".txt"]:
                    if summary_type.endswith(file_ext):
                        summary_type = summary_type[: -len(file_ext)]
                        break

                # Get format
                if ext in [".pdf", ".epub", ".md", ".txt"]:
                    format_name = ext[1:]
                    return (summary_type, format_name)

        return None

    def get_preferred_format(
        self, book_formats: list[tuple[str, Path]], prefer: str = "epub"
    ) -> Path | None:
        """Get preferred format for text extraction.

        Args:
            book_formats: List of (format, path) tuples
            prefer: Preferred format (epub, pdf, md)

        Returns:
            Path to preferred format or None
        """
        # Create format map
        format_map = {fmt: path for fmt, path in book_formats}

        # Try preferred first
        if prefer in format_map:
            return format_map[prefer]

        # Fallback order: epub -> pdf -> md -> txt
        for fallback in ["epub", "pdf", "md", "txt"]:
            if fallback in format_map:
                return format_map[fallback]

        return None

    def extract_markdown_from_summary(self, summary_path: Path) -> str:
        """Extract markdown text from summary file.

        Args:
            summary_path: Path to summary file

        Returns:
            Markdown text

        Raises:
            ValueError: If summary format is unsupported
        """
        ext = summary_path.suffix.lower()

        if ext == ".md":
            # Already markdown
            return summary_path.read_text(encoding="utf-8")

        elif ext == ".txt":
            # Plain text - wrap in markdown
            return summary_path.read_text(encoding="utf-8")

        elif ext == ".pdf":
            # Extract from PDF
            text = BookParser.parse_pdf(summary_path)
            return text

        elif ext == ".epub":
            # Extract from EPUB
            text = BookParser.parse_epub(summary_path)
            return text

        else:
            raise ValueError(f"Unsupported summary format: {ext}")

    def get_summary_output_name(self, summary_type: str, original_format: str) -> str:
        """Get output filename for summary.

        Args:
            summary_type: Type of summary (e.g., 'shortform', 'claude-sonnet-4.5')
            original_format: Original format (pdf, epub, md)

        Returns:
            Output filename (e.g., 'shortform-summary.md')
        """
        # Clean summary type
        clean_type = summary_type.replace("_", "-").lower()

        # Always output as markdown
        return f"{clean_type}-summary.md"
