"""Extract chapters directly from EPUB files."""

import re
from pathlib import Path

import ebooklib
from bs4 import BeautifulSoup
from ebooklib import epub


class EpubChapterExtractor:
    """Extract chapters from EPUB based on internal structure."""

    def __init__(self, epub_path: Path):
        """Initialize extractor.

        Args:
            epub_path: Path to EPUB file
        """
        self.epub_path = Path(epub_path)
        self.book = epub.read_epub(epub_path)

    def extract_chapters(self) -> list[tuple[int, str, str]]:
        """Extract chapters from EPUB.

        Returns:
            List of (chapter_number, title, markdown_content) tuples
        """
        chapters = []
        chapter_num = 0

        # Get all document items from the EPUB spine
        # The spine defines the reading order
        for item in self.book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            # Convert HTML content to markdown
            content = item.get_content()
            markdown = self._html_to_markdown(content)

            # Skip empty or very short content
            if not markdown or len(markdown.strip()) < 100:
                continue

            # Try to extract chapter title from content
            title = self._extract_title_from_content(markdown, item)

            # Skip if this looks like front matter (copyright, dedication, etc.)
            if self._is_front_matter(title, markdown):
                continue

            chapter_num += 1
            chapters.append((chapter_num, title, markdown))

        return chapters

    def _extract_title_from_content(self, markdown: str, item) -> str:
        """Extract chapter title from content.

        Args:
            markdown: Markdown content
            item: EPUB item

        Returns:
            Chapter title
        """
        # Try to find first heading
        lines = markdown.split("\n")
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if line.startswith("#"):
                # Found a heading
                title = re.sub(r"^#+\s*", "", line).strip()
                return title

        # Fallback: use item name
        item_name = item.get_name()
        if item_name:
            # Clean up the filename
            title = Path(item_name).stem
            title = title.replace("_", " ").replace("-", " ")
            # Capitalize words
            title = " ".join(word.capitalize() for word in title.split())
            return title

        return "Untitled Chapter"

    def _is_front_matter(self, title: str, content: str) -> bool:
        """Check if this is front matter to skip.

        Args:
            title: Chapter title
            content: Chapter content

        Returns:
            True if this is front matter
        """
        skip_patterns = [
            r"^(title|cover|copyright|dedication|table\s+of\s+contents|contents|acknowledgments|preface|foreword|about\s+the\s+author)$",
        ]

        title_lower = title.lower()

        for pattern in skip_patterns:
            if re.match(pattern, title_lower):
                return True

        # Also skip very short content (likely TOC or similar)
        if len(content.strip()) < 200:
            return True

        return False

    def _html_to_markdown(self, html_content: bytes) -> str:
        """Convert HTML content to markdown.

        Args:
            html_content: HTML content as bytes

        Returns:
            Markdown text
        """
        soup = BeautifulSoup(html_content, "html.parser")

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Process the HTML tree recursively
        def process_element(element) -> str:
            """Recursively process HTML elements to markdown."""
            if isinstance(element, str):
                text = str(element).strip()
                return text if text else ""

            if not hasattr(element, "name"):
                return ""

            # Handle headings
            if element.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                level = int(element.name[1])
                text = element.get_text().strip()
                return f"\n\n{'#' * level} {text}\n\n"

            # Handle paragraphs
            elif element.name == "p":
                text = "".join(process_element(child) for child in element.children)
                return f"\n\n{text.strip()}\n\n"

            # Handle bold/strong
            elif element.name in ["b", "strong"]:
                text = "".join(process_element(child) for child in element.children)
                return f"**{text}**"

            # Handle italic/em
            elif element.name in ["i", "em"]:
                text = "".join(process_element(child) for child in element.children)
                return f"*{text}*"

            # Handle line breaks
            elif element.name == "br":
                return "\n"

            # Handle divs and other containers
            elif element.name in ["div", "section", "article", "body", "html"]:
                return "".join(process_element(child) for child in element.children)

            # For other elements, process children
            else:
                if hasattr(element, "children"):
                    return "".join(process_element(child) for child in element.children)
                else:
                    return element.get_text()

        # Process the document
        body = soup.find("body")
        if body:
            markdown = process_element(body)
        else:
            markdown = process_element(soup)

        # Clean up excessive whitespace
        markdown = re.sub(r"\n{4,}", "\n\n\n", markdown)
        markdown = re.sub(r" +", " ", markdown)

        return markdown.strip()

    def save_chapters(self, output_dir: Path) -> list[tuple[int, str, Path]]:
        """Extract and save chapters to individual files.

        Args:
            output_dir: Directory to save chapter files

        Returns:
            List of (chapter_number, title, file_path) tuples

        Raises:
            ValueError: If no chapters found in EPUB
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        chapters = self.extract_chapters()

        if not chapters:
            raise ValueError("No chapters found in EPUB")

        saved_chapters = []

        for chapter_num, title, content in chapters:
            # Create safe filename with order prefix
            # "Introduction" → "1-introduction.md"
            # "Chapter 1: Management 101" → "2-chapter-1-management-101.md"
            safe_title = re.sub(r"[^\w\s-]", "", title.lower())
            safe_title = re.sub(r"[-\s]+", "-", safe_title).strip("-")

            filename = f"{chapter_num}-{safe_title}.md"
            file_path = output_dir / filename

            # Save chapter content
            file_path.write_text(content, encoding="utf-8")

            saved_chapters.append((chapter_num, title, file_path))

        return saved_chapters
