"""Book parsing utilities for PDF, EPUB, and Markdown formats."""

import re
from pathlib import Path

import ebooklib
import fitz  # PyMuPDF
from bs4 import BeautifulSoup
from ebooklib import epub


class BookParser:
    """Parser for extracting text from various book formats."""

    @staticmethod
    def parse_pdf(file_path: Path) -> str:
        """Extract text from a PDF file.

        Args:
            file_path: Path to PDF file

        Returns:
            Extracted text content
        """
        doc = fitz.open(file_path)
        text_parts = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            text_parts.append(page.get_text())

        doc.close()
        return "\n\n".join(text_parts)

    @staticmethod
    def parse_epub(file_path: Path) -> str:
        """Extract text from an EPUB file.

        Args:
            file_path: Path to EPUB file

        Returns:
            Extracted text content
        """
        book = epub.read_epub(file_path)
        text_parts = []

        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                # Get HTML content
                content = item.get_content()
                # Convert HTML to markdown
                markdown = BookParser._html_to_markdown(content)
                if markdown and markdown.strip():
                    text_parts.append(markdown)

        return "\n\n".join(text_parts)

    @staticmethod
    def _html_to_markdown(html_content: bytes) -> str:
        """Convert HTML content to markdown, preserving structure.

        Args:
            html_content: HTML content as bytes

        Returns:
            Markdown text with preserved headings and structure
        """
        soup = BeautifulSoup(html_content, "html.parser")

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Process the HTML tree recursively
        def process_element(element) -> str:
            """Recursively process HTML elements to markdown."""
            if isinstance(element, str):
                return element.strip()

            # Handle headings
            if element.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                level = int(element.name[1])
                text = element.get_text().strip()
                return f"\n\n{'#' * level} {text}\n\n"

            # Handle paragraphs
            elif element.name == "p":
                text = "".join(
                    str(child) if isinstance(child, str) else process_element(child)
                    for child in element.children
                )
                return f"\n\n{text.strip()}\n\n"

            # Handle bold/strong
            elif element.name in ["b", "strong"]:
                text = "".join(
                    str(child) if isinstance(child, str) else process_element(child)
                    for child in element.children
                )
                return f"**{text}**"

            # Handle italic/em
            elif element.name in ["i", "em"]:
                text = "".join(
                    str(child) if isinstance(child, str) else process_element(child)
                    for child in element.children
                )
                return f"*{text}*"

            # Handle line breaks
            elif element.name == "br":
                return "\n"

            # Handle divs and other containers - process children
            elif element.name in ["div", "section", "article", "body", "html"]:
                return "".join(
                    str(child) if isinstance(child, str) else process_element(child)
                    for child in element.children
                )

            # For other elements, just process children
            else:
                if hasattr(element, "children"):
                    return "".join(
                        str(child) if isinstance(child, str) else process_element(child)
                        for child in element.children
                    )
                else:
                    return element.get_text()

        # Process the entire document
        body = soup.find("body")
        if body:
            markdown = process_element(body)
        else:
            markdown = process_element(soup)

        # Clean up excessive whitespace
        markdown = re.sub(r"\n{4,}", "\n\n\n", markdown)
        markdown = re.sub(r" +", " ", markdown)

        return markdown.strip()

    @staticmethod
    def extract_epub_metadata(file_path: Path) -> dict[str, str | None]:
        """Extract metadata from EPUB file.

        Args:
            file_path: Path to EPUB file

        Returns:
            Dictionary with title, author, publisher, language, isbn
        """
        book = epub.read_epub(file_path)
        metadata = {
            "title": None,
            "author": None,
            "publisher": None,
            "language": None,
            "isbn": None,
        }

        # Extract title
        title = book.get_metadata("DC", "title")
        if title:
            metadata["title"] = title[0][0] if title else None

        # Extract author(s)
        creators = book.get_metadata("DC", "creator")
        if creators:
            # Join multiple authors with commas
            authors = [creator[0] for creator in creators]
            metadata["author"] = ", ".join(authors) if authors else None

        # Extract publisher
        publisher = book.get_metadata("DC", "publisher")
        if publisher:
            metadata["publisher"] = publisher[0][0] if publisher else None

        # Extract language
        language = book.get_metadata("DC", "language")
        if language:
            metadata["language"] = language[0][0] if language else None

        # Extract ISBN
        identifier = book.get_metadata("DC", "identifier")
        if identifier:
            for ident in identifier:
                # Look for ISBN in identifiers
                if "isbn" in str(ident).lower():
                    metadata["isbn"] = ident[0]
                    break

        return metadata

    @staticmethod
    def parse_markdown(file_path: Path) -> str:
        """Read text from a Markdown file.

        Args:
            file_path: Path to Markdown file

        Returns:
            File content
        """
        return file_path.read_text(encoding="utf-8")

    @staticmethod
    def detect_format(file_path: Path) -> str | None:
        """Detect book format from file extension.

        Args:
            file_path: Path to book file

        Returns:
            Format string ('pdf', 'epub', 'markdown') or None if unsupported
        """
        ext = file_path.suffix.lower()
        if ext == ".pdf":
            return "pdf"
        elif ext == ".epub":
            return "epub"
        elif ext in [".md", ".markdown"]:
            return "markdown"
        return None

    @classmethod
    def parse(cls, file_path: Path) -> str:
        """Auto-detect format and extract text.

        Args:
            file_path: Path to book file

        Returns:
            Extracted text content

        Raises:
            ValueError: If format is unsupported
        """
        format_type = cls.detect_format(file_path)

        if format_type == "pdf":
            return cls.parse_pdf(file_path)
        elif format_type == "epub":
            return cls.parse_epub(file_path)
        elif format_type == "markdown":
            return cls.parse_markdown(file_path)
        else:
            raise ValueError(f"Unsupported book format: {file_path.suffix}")


def clean_text(text: str) -> str:
    """Clean extracted text by removing excessive whitespace.

    Args:
        text: Raw extracted text

    Returns:
        Cleaned text
    """
    # Remove excessive blank lines (more than 2 in a row)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(lines)

    return text.strip()


def extract_metadata_from_text(text: str) -> dict[str, str | None]:
    """Try to extract basic metadata from text content.

    Args:
        text: Book text content

    Returns:
        Dictionary with potential title and author
    """
    lines = text.split("\n")[:20]  # Look at first 20 lines

    metadata = {"title": None, "author": None}

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Look for author patterns
        author_match = re.search(r"(?:by|author:?)\s+([A-Z][a-zA-Z\s.]+)", line, re.IGNORECASE)
        if author_match and not metadata["author"]:
            metadata["author"] = author_match.group(1).strip()

        # First substantial line might be the title (strip markdown headers)
        # Skip common front matter like "Praise for", "Dedication", etc.
        skip_patterns = [
            r"^praise\s+for",
            r"^dedication",
            r"^copyright",
            r"^table\s+of\s+contents",
            r"^contents",
            r"^foreword",
            r"^preface",
            r"^acknowledgments",
        ]

        should_skip = any(re.match(pattern, line, re.IGNORECASE) for pattern in skip_patterns)

        if not metadata["title"] and not should_skip and len(line) > 5 and len(line) < 100:
            # Remove markdown header symbols
            title = re.sub(r"^#+\s*", "", line)
            # Only use if it looks like a title (has capital letters)
            if re.search(r"[A-Z]", title):
                metadata["title"] = title

    return metadata
