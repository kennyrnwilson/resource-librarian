"""PDF converter utility for markdown to PDF conversion.

Uses PyMuPDF (fitz) to create PDF documents from markdown content.
Supports basic markdown formatting: headings, bold, italic, lists, code blocks.
"""

import re
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF


class MarkdownToPDFConverter:
    """Converts markdown files to PDF format with formatting support."""

    def __init__(
        self,
        font_size: int = 12,
        font_name: str = "helv",  # Helvetica
        line_height: float = 1.5,
        margin: int = 72,  # 1 inch = 72 points
    ):
        """Initialize the PDF converter.

        Args:
            font_size: Base font size for body text
            font_name: Font name (helv=Helvetica, times=Times, cour=Courier)
            line_height: Line height multiplier
            margin: Page margin in points (72 points = 1 inch)
        """
        self.font_size = font_size
        self.font_name = font_name
        self.line_height = line_height
        self.margin = margin

    def convert(
        self,
        markdown_path: Path,
        output_path: Path,
        title: Optional[str] = None,
        author: Optional[str] = None,
    ) -> Path:
        """Convert a markdown file to PDF.

        Args:
            markdown_path: Path to the markdown file
            output_path: Path where the PDF should be saved
            title: Optional title for PDF metadata
            author: Optional author for PDF metadata

        Returns:
            Path to the created PDF file

        Raises:
            FileNotFoundError: If markdown file doesn't exist
            ValueError: If markdown file is empty
        """
        if not markdown_path.exists():
            raise FileNotFoundError(f"Markdown file not found: {markdown_path}")

        # Read markdown content
        content = markdown_path.read_text(encoding="utf-8")
        if not content.strip():
            raise ValueError(f"Markdown file is empty: {markdown_path}")

        # Create PDF document
        doc = fitz.open()

        # Set metadata
        if title:
            doc.metadata["title"] = title
        else:
            doc.metadata["title"] = markdown_path.stem

        if author:
            doc.metadata["author"] = author

        doc.metadata["creator"] = "Resource Librarian"
        doc.metadata["producer"] = "PyMuPDF"

        # Add content to pages
        self._add_text_to_pdf(doc, content)

        # Save PDF
        doc.save(str(output_path))
        doc.close()

        return output_path

    def _add_text_to_pdf(self, doc: fitz.Document, text: str) -> None:
        """Add text content to PDF document, handling pagination and formatting.

        Args:
            doc: PyMuPDF document object
            text: Text content to add
        """
        # Page dimensions (US Letter: 8.5 x 11 inches)
        page_width = 612  # 8.5 inches * 72 points/inch
        page_height = 792  # 11 inches * 72 points/inch
        max_width = page_width - (2 * self.margin)

        # Start first page
        page = doc.new_page(width=page_width, height=page_height)
        y_position = self.margin

        # Split text into lines
        lines = text.split("\n")
        in_code_block = False
        in_list = False

        i = 0
        while i < len(lines):
            line = lines[i]

            # Check for code blocks
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                i += 1
                continue

            # Handle code block content
            if in_code_block:
                # Check if we need a new page
                if y_position + self.font_size * self.line_height > page_height - self.margin:
                    page = doc.new_page(width=page_width, height=page_height)
                    y_position = self.margin

                # Code blocks use courier font
                page.insert_text(
                    (self.margin + 20, y_position),
                    line,
                    fontsize=self.font_size - 1,
                    fontname="cour",
                    color=(0.2, 0.2, 0.2),
                )
                y_position += self.font_size * self.line_height
                i += 1
                continue

            # Check if this is a heading (starts with #)
            if line.startswith("#"):
                in_list = False
                heading_level = len(line) - len(line.lstrip("#"))
                heading_text = line.lstrip("#").strip()

                if not heading_text:
                    i += 1
                    continue

                # Adjust font size based on heading level
                if heading_level == 1:
                    font_size = self.font_size + 8
                elif heading_level == 2:
                    font_size = self.font_size + 6
                elif heading_level == 3:
                    font_size = self.font_size + 4
                else:
                    font_size = self.font_size + 2

                # Add spacing before heading
                y_position += font_size * 0.5

                # Check if we need a new page
                if y_position + font_size * self.line_height > page_height - self.margin:
                    page = doc.new_page(width=page_width, height=page_height)
                    y_position = self.margin

                # Insert heading (regular font - bold not available in basic PyMuPDF)
                page.insert_text(
                    (self.margin, y_position),
                    heading_text,
                    fontsize=font_size,
                    fontname="helv",
                )

                y_position += font_size * self.line_height
                y_position += font_size * 0.3
                i += 1
                continue

            # Check for bullet list
            if line.strip().startswith(("- ", "* ", "+ ")):
                in_list = True
                # Remove bullet marker
                list_text = line.strip()[2:]
                indent = 20

                # Parse inline formatting in list item
                formatted_segments = self._parse_inline_formatting(list_text)

                # Check if we need a new page
                if y_position + self.font_size * self.line_height > page_height - self.margin:
                    page = doc.new_page(width=page_width, height=page_height)
                    y_position = self.margin

                # Add bullet
                page.insert_text(
                    (self.margin + indent - 10, y_position),
                    "•",
                    fontsize=self.font_size,
                    fontname=self.font_name,
                )

                # Add formatted text
                x_position = self.margin + indent
                for text_seg, is_bold, is_italic, is_code in formatted_segments:
                    font = self._get_font_name(is_bold, is_italic, is_code)
                    font_size_seg = self.font_size - 1 if is_code else self.font_size

                    page.insert_text(
                        (x_position, y_position),
                        text_seg,
                        fontsize=font_size_seg,
                        fontname=font,
                        color=(0.2, 0.2, 0.2) if is_code else (0, 0, 0),
                    )

                    # Estimate text width and move x position
                    x_position += len(text_seg) * (font_size_seg * 0.5)

                y_position += self.font_size * self.line_height
                i += 1
                continue

            # Check for numbered list
            if re.match(r"^\d+\.\s", line.strip()):
                in_list = True
                # Extract number and text
                match = re.match(r"^(\d+)\.\s(.+)", line.strip())
                if match:
                    number = match.group(1)
                    list_text = match.group(2)
                    indent = 20

                    # Parse inline formatting
                    formatted_segments = self._parse_inline_formatting(list_text)

                    # Check if we need a new page
                    if y_position + self.font_size * self.line_height > page_height - self.margin:
                        page = doc.new_page(width=page_width, height=page_height)
                        y_position = self.margin

                    # Add number
                    page.insert_text(
                        (self.margin + indent - 15, y_position),
                        f"{number}.",
                        fontsize=self.font_size,
                        fontname=self.font_name,
                    )

                    # Add formatted text
                    x_position = self.margin + indent
                    for text_seg, is_bold, is_italic, is_code in formatted_segments:
                        font = self._get_font_name(is_bold, is_italic, is_code)
                        font_size_seg = self.font_size - 1 if is_code else self.font_size

                        page.insert_text(
                            (x_position, y_position),
                            text_seg,
                            fontsize=font_size_seg,
                            fontname=font,
                            color=(0.2, 0.2, 0.2) if is_code else (0, 0, 0),
                        )

                        x_position += len(text_seg) * (font_size_seg * 0.5)

                    y_position += self.font_size * self.line_height
                    i += 1
                    continue

            # Regular text
            if not line.strip():
                # Empty line - add spacing
                if in_list:
                    y_position += self.font_size * self.line_height * 0.3
                    in_list = False
                else:
                    y_position += self.font_size * self.line_height * 0.5
                i += 1
                continue

            in_list = False

            # Parse inline formatting (bold, italic, code)
            formatted_segments = self._parse_inline_formatting(line)

            # Render formatted text with wrapping
            x_position = self.margin
            current_line_segments = []
            current_line_width = 0

            for text_seg, is_bold, is_italic, is_code in formatted_segments:
                words = text_seg.split()
                font_size_seg = self.font_size - 1 if is_code else self.font_size

                for word in words:
                    word_with_space = word + " "
                    word_width = len(word_with_space) * (font_size_seg * 0.5)

                    # Check if adding this word exceeds line width
                    if current_line_width + word_width > max_width and current_line_segments:
                        # Render current line
                        if (
                            y_position + self.font_size * self.line_height
                            > page_height - self.margin
                        ):
                            page = doc.new_page(width=page_width, height=page_height)
                            y_position = self.margin

                        # Draw all segments in current line
                        x_pos = self.margin
                        for seg_text, seg_bold, seg_italic, seg_code in current_line_segments:
                            seg_font = self._get_font_name(seg_bold, seg_italic, seg_code)
                            seg_size = self.font_size - 1 if seg_code else self.font_size

                            page.insert_text(
                                (x_pos, y_position),
                                seg_text,
                                fontsize=seg_size,
                                fontname=seg_font,
                                color=(0.2, 0.2, 0.2) if seg_code else (0, 0, 0),
                            )
                            x_pos += len(seg_text) * (seg_size * 0.5)

                        y_position += self.font_size * self.line_height
                        current_line_segments = []
                        current_line_width = 0

                    # Add word to current line
                    current_line_segments.append((word_with_space, is_bold, is_italic, is_code))
                    current_line_width += word_width

            # Render remaining segments
            if current_line_segments:
                if y_position + self.font_size * self.line_height > page_height - self.margin:
                    page = doc.new_page(width=page_width, height=page_height)
                    y_position = self.margin

                x_pos = self.margin
                for seg_text, seg_bold, seg_italic, seg_code in current_line_segments:
                    seg_font = self._get_font_name(seg_bold, seg_italic, seg_code)
                    seg_size = self.font_size - 1 if seg_code else self.font_size

                    page.insert_text(
                        (x_pos, y_position),
                        seg_text,
                        fontsize=seg_size,
                        fontname=seg_font,
                        color=(0.2, 0.2, 0.2) if seg_code else (0, 0, 0),
                    )
                    x_pos += len(seg_text) * (seg_size * 0.5)

                y_position += self.font_size * self.line_height

            i += 1

    def _parse_inline_formatting(self, text: str) -> list:
        """Parse inline markdown formatting (bold, italic, code).

        Args:
            text: Text to parse

        Returns:
            List of tuples: (text, is_bold, is_italic, is_code)
        """
        segments = []
        current_pos = 0

        # Pattern to match markdown formatting
        pattern = r"(\*\*\*(.+?)\*\*\*|\*\*(.+?)\*\*|\*(.+?)\*|`(.+?)`)"

        for match in re.finditer(pattern, text):
            # Add text before match
            if match.start() > current_pos:
                plain_text = text[current_pos : match.start()]
                if plain_text:
                    segments.append((plain_text, False, False, False))

            # Determine formatting type
            if match.group(2):  # ***bold italic***
                segments.append((match.group(2), True, True, False))
            elif match.group(3):  # **bold**
                segments.append((match.group(3), True, False, False))
            elif match.group(4):  # *italic*
                segments.append((match.group(4), False, True, False))
            elif match.group(5):  # `code`
                segments.append((match.group(5), False, False, True))

            current_pos = match.end()

        # Add remaining text
        if current_pos < len(text):
            remaining = text[current_pos:]
            if remaining:
                segments.append((remaining, False, False, False))

        return segments if segments else [(text, False, False, False)]

    def _get_font_name(self, is_bold: bool, is_italic: bool, is_code: bool) -> str:
        """Get appropriate font name based on formatting.

        Args:
            is_bold: Whether text is bold
            is_italic: Whether text is italic
            is_code: Whether text is code

        Returns:
            Font name string
        """
        if is_code:
            return "cour"
        elif is_bold and is_italic:
            return "hebo"  # Helvetica Bold Oblique
        elif is_bold:
            return "helv"  # Use helv for bold (PyMuPDF limitation)
        elif is_italic:
            return "heit"  # Helvetica Oblique
        else:
            return self.font_name


def convert_markdown_to_pdf(
    markdown_path: Path,
    output_path: Path,
    title: Optional[str] = None,
    author: Optional[str] = None,
    font_size: int = 12,
) -> Path:
    """Convenience function to convert markdown to PDF.

    Args:
        markdown_path: Path to the markdown file
        output_path: Path where the PDF should be saved
        title: Optional title for PDF metadata
        author: Optional author for PDF metadata
        font_size: Font size for body text

    Returns:
        Path to the created PDF file
    """
    converter = MarkdownToPDFConverter(font_size=font_size)
    return converter.convert(markdown_path, output_path, title=title, author=author)
