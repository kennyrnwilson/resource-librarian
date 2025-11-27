"""CLI integration tests for book commands.

Tests for:
- rl book list (with various filters)
- rl book get (retrieve book content)
"""

import yaml
from pathlib import Path

from typer.testing import CliRunner

from resourcelibrarian.cli.commands import app
from resourcelibrarian.library import ResourceLibrary
from resourcelibrarian.models.book import Book, BookManifest
from resourcelibrarian.utils.io import save_book_manifest, save_yaml

runner = CliRunner()


def create_test_book(
    library_path: Path,
    title: str,
    author: str,
    categories: list[str] = None,
    tags: list[str] = None,
    content: str = "Sample book content",
) -> Book:
    """Helper to create a test book in the library.

    Args:
        library_path: Path to library root
        title: Book title
        author: Book author
        categories: List of categories
        tags: List of tags
        content: Markdown content for the book

    Returns:
        Book instance
    """
    if categories is None:
        categories = []
    if tags is None:
        tags = []

    # Create folder structure
    author_slug = author.lower().replace(" ", "-")
    title_slug = title.lower().replace(" ", "-")
    book_folder = library_path / "books" / author_slug / title_slug
    book_folder.mkdir(parents=True)

    # Create manifest
    manifest = BookManifest(
        title=title,
        author=author,
        categories=categories,
        tags=tags,
        source_folder=f"{author_slug}/{title_slug}",
        formats={"markdown": f"{title_slug}.md"},
        summaries={},
    )
    save_book_manifest(manifest, book_folder)

    # Create markdown file
    markdown_file = book_folder / f"{title_slug}.md"
    markdown_file.write_text(content, encoding="utf-8")

    # Add to catalog (matching CatalogManager format)
    catalog_path = library_path / "catalog.yaml"
    catalog_data = yaml.safe_load(catalog_path.read_text())
    catalog_data["books"].append(
        {
            "title": title,
            "author": author,
            "folder_path": str(book_folder),
            "categories": categories,
            "tags": tags,
        }
    )
    save_yaml(catalog_data, catalog_path)

    return Book(folder_path=book_folder, manifest=manifest)


# ==================== Book List Tests ====================


def test_book_list_shows_all_books(tmp_path):
    """Test 'rl book list' shows all books in library."""
    library_path = tmp_path / "library"
    ResourceLibrary.initialize(library_path)

    # Create test books
    create_test_book(library_path, "Python Guide", "John Smith", ["Programming"])
    create_test_book(library_path, "Data Science", "Jane Doe", ["Data", "Programming"])

    result = runner.invoke(app, ["book", "list", "--library", str(library_path)])

    assert result.exit_code == 0
    assert "Python Guide" in result.stdout
    assert "Data Science" in result.stdout
    assert "John Smith" in result.stdout
    assert "Jane Doe" in result.stdout
    assert "2 found" in result.stdout


def test_book_list_empty_library(tmp_path):
    """Test 'rl book list' with empty library."""
    library_path = tmp_path / "library"
    ResourceLibrary.initialize(library_path)

    result = runner.invoke(app, ["book", "list", "--library", str(library_path)])

    assert result.exit_code == 0
    assert "No books in library yet" in result.stdout


def test_book_list_filter_by_author(tmp_path):
    """Test 'rl book list --author' filters correctly."""
    library_path = tmp_path / "library"
    ResourceLibrary.initialize(library_path)

    create_test_book(library_path, "Python Guide", "John Smith", ["Programming"])
    create_test_book(library_path, "Data Science", "Jane Doe", ["Data"])
    create_test_book(library_path, "Web Dev", "John Doe", ["Web"])

    result = runner.invoke(
        app, ["book", "list", "--library", str(library_path), "--author", "John"]
    )

    assert result.exit_code == 0
    assert "Python Guide" in result.stdout
    assert "Web Dev" in result.stdout
    assert "Data Science" not in result.stdout
    assert "2 found" in result.stdout


def test_book_list_filter_by_category(tmp_path):
    """Test 'rl book list --category' filters correctly."""
    library_path = tmp_path / "library"
    ResourceLibrary.initialize(library_path)

    create_test_book(library_path, "Python Guide", "John Smith", ["Programming", "Python"])
    create_test_book(library_path, "Data Science", "Jane Doe", ["Data", "Programming"])
    create_test_book(library_path, "History Book", "Bob Jones", ["History"])

    result = runner.invoke(
        app, ["book", "list", "--library", str(library_path), "--category", "Programming"]
    )

    assert result.exit_code == 0
    assert "Python Guide" in result.stdout
    assert "Data Science" in result.stdout
    assert "History Book" not in result.stdout
    assert "2 found" in result.stdout


def test_book_list_filter_by_tag(tmp_path):
    """Test 'rl book list --tag' filters correctly."""
    library_path = tmp_path / "library"
    ResourceLibrary.initialize(library_path)

    create_test_book(library_path, "Python Guide", "John Smith", tags=["beginner", "tutorial"])
    create_test_book(library_path, "Advanced Python", "Jane Doe", tags=["advanced"])

    result = runner.invoke(
        app, ["book", "list", "--library", str(library_path), "--tag", "beginner"]
    )

    assert result.exit_code == 0
    assert "Python Guide" in result.stdout
    assert "Advanced Python" not in result.stdout
    assert "1 found" in result.stdout


def test_book_list_filter_by_title(tmp_path):
    """Test 'rl book list --title' filters correctly."""
    library_path = tmp_path / "library"
    ResourceLibrary.initialize(library_path)

    create_test_book(library_path, "Python Programming", "John Smith")
    create_test_book(library_path, "Python Guide", "Jane Doe")
    create_test_book(library_path, "Data Science", "Bob Jones")

    result = runner.invoke(
        app, ["book", "list", "--library", str(library_path), "--title", "Python"]
    )

    assert result.exit_code == 0
    assert "Python Programming" in result.stdout
    assert "Python Guide" in result.stdout
    assert "Data Science" not in result.stdout
    assert "2 found" in result.stdout


def test_book_list_multiple_filters(tmp_path):
    """Test 'rl book list' with multiple filters."""
    library_path = tmp_path / "library"
    ResourceLibrary.initialize(library_path)

    create_test_book(
        library_path, "Python Guide", "John Smith", ["Programming"], ["beginner"]
    )
    create_test_book(
        library_path, "Python Advanced", "John Smith", ["Programming"], ["advanced"]
    )
    create_test_book(library_path, "Data Science", "Jane Doe", ["Programming"], ["beginner"])

    result = runner.invoke(
        app,
        [
            "book",
            "list",
            "--library",
            str(library_path),
            "--author",
            "John",
            "--tag",
            "beginner",
        ],
    )

    assert result.exit_code == 0
    assert "Python Guide" in result.stdout
    assert "Python Advanced" not in result.stdout
    assert "Data Science" not in result.stdout
    assert "1 found" in result.stdout


def test_book_list_no_matches(tmp_path):
    """Test 'rl book list' with filters that match nothing."""
    library_path = tmp_path / "library"
    ResourceLibrary.initialize(library_path)

    create_test_book(library_path, "Python Guide", "John Smith")

    result = runner.invoke(
        app, ["book", "list", "--library", str(library_path), "--author", "NonExistent"]
    )

    assert result.exit_code == 0
    assert "No books found matching filters" in result.stdout


def test_book_list_library_not_found(tmp_path):
    """Test 'rl book list' with non-existent library."""
    result = runner.invoke(
        app, ["book", "list", "--library", str(tmp_path / "nonexistent")]
    )

    assert result.exit_code == 1
    assert "Library Not Found" in result.stdout


# ==================== Book Get Tests ====================


def test_book_get_retrieves_markdown(tmp_path):
    """Test 'rl book get' retrieves markdown content."""
    library_path = tmp_path / "library"
    ResourceLibrary.initialize(library_path)

    content = "# Python Guide\n\nThis is the content."
    create_test_book(library_path, "Python Guide", "John Smith", content=content)

    result = runner.invoke(app, ["book", "get", "Python Guide", "--library", str(library_path)])

    assert result.exit_code == 0
    assert "Python Guide" in result.stdout
    assert "John Smith" in result.stdout
    assert "This is the content" in result.stdout


def test_book_get_saves_to_file(tmp_path):
    """Test 'rl book get --output' saves to file."""
    library_path = tmp_path / "library"
    ResourceLibrary.initialize(library_path)

    content = "# Python Guide\n\nThis is the content."
    create_test_book(library_path, "Python Guide", "John Smith", content=content)

    output_file = tmp_path / "output.md"
    result = runner.invoke(
        app,
        [
            "book",
            "get",
            "Python Guide",
            "--library",
            str(library_path),
            "--output",
            str(output_file),
        ],
    )

    assert result.exit_code == 0
    assert output_file.exists()
    assert output_file.read_text() == content
    assert "Success" in result.stdout


def test_book_get_book_not_found(tmp_path):
    """Test 'rl book get' with non-existent book."""
    library_path = tmp_path / "library"
    ResourceLibrary.initialize(library_path)

    result = runner.invoke(
        app, ["book", "get", "NonExistent Book", "--library", str(library_path)]
    )

    assert result.exit_code == 1
    assert "Book Not Found" in result.stdout


def test_book_get_case_insensitive_title(tmp_path):
    """Test 'rl book get' is case-insensitive for title matching."""
    library_path = tmp_path / "library"
    ResourceLibrary.initialize(library_path)

    content = "# Python Guide\n\nContent here."
    create_test_book(library_path, "Python Guide", "John Smith", content=content)

    # Try with different case
    result = runner.invoke(
        app, ["book", "get", "python guide", "--library", str(library_path)]
    )

    assert result.exit_code == 0
    assert "Python Guide" in result.stdout


def test_book_get_library_not_found(tmp_path):
    """Test 'rl book get' with non-existent library."""
    result = runner.invoke(
        app, ["book", "get", "Some Book", "--library", str(tmp_path / "nonexistent")]
    )

    assert result.exit_code == 1
    assert "Library Not Found" in result.stdout


# ==================== Book Add Tests ====================


def test_book_add_markdown_with_metadata(tmp_path):
    """Test 'rl book add' with markdown file and explicit metadata."""
    library_path = tmp_path / "library"
    ResourceLibrary.initialize(library_path)

    # Create a markdown file
    md_file = tmp_path / "test-book.md"
    md_file.write_text("# Test Book\n\nThis is a test book content.", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "book",
            "add",
            str(md_file),
            "--library",
            str(library_path),
            "--title",
            "Test Book",
            "--author",
            "Test Author",
            "--categories",
            "Fiction,Adventure",
            "--tags",
            "test,sample",
        ],
    )

    assert result.exit_code == 0
    assert "Book added successfully" in result.stdout
    assert "Test Book" in result.stdout
    assert "Test Author" in result.stdout

    # Verify book was added to catalog
    catalog_path = library_path / "catalog.yaml"
    catalog_data = yaml.safe_load(catalog_path.read_text())
    assert len(catalog_data["books"]) == 1

    # Get book data from catalog
    book_data = catalog_data["books"][0]
    assert book_data["title"] == "Test Book"
    assert book_data["author"] == "Test Author"

    # Verify book folder structure exists
    book_folder = Path(book_data["folder_path"])
    assert book_folder.exists()
    assert (book_folder / "manifest.yaml").exists()


def test_book_add_markdown_minimal(tmp_path):
    """Test 'rl book add' with only required metadata."""
    library_path = tmp_path / "library"
    ResourceLibrary.initialize(library_path)

    # Create a markdown file
    md_file = tmp_path / "simple.md"
    md_file.write_text("# Simple Book\n\nContent.", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "book",
            "add",
            str(md_file),
            "--library",
            str(library_path),
            "--title",
            "Simple Book",
            "--author",
            "Simple Author",
        ],
    )

    assert result.exit_code == 0
    assert "Book added successfully" in result.stdout


def test_book_add_file_not_found(tmp_path):
    """Test 'rl book add' with non-existent file."""
    library_path = tmp_path / "library"
    ResourceLibrary.initialize(library_path)

    result = runner.invoke(
        app,
        [
            "book",
            "add",
            str(tmp_path / "nonexistent.md"),
            "--library",
            str(library_path),
        ],
    )

    assert result.exit_code == 1
    assert "File Not Found" in result.stdout


def test_book_add_library_not_found(tmp_path):
    """Test 'rl book add' with non-existent library."""
    md_file = tmp_path / "book.md"
    md_file.write_text("# Book\n\nContent.", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "book",
            "add",
            str(md_file),
            "--library",
            str(tmp_path / "nonexistent"),
        ],
    )

    assert result.exit_code == 1
    assert "Library Not Found" in result.stdout


def test_book_add_missing_metadata(tmp_path):
    """Test 'rl book add' without required metadata fails gracefully."""
    library_path = tmp_path / "library"
    ResourceLibrary.initialize(library_path)

    # Create markdown file without clear metadata
    md_file = tmp_path / "book.md"
    md_file.write_text("Some content without title or author.", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "book",
            "add",
            str(md_file),
            "--library",
            str(library_path),
        ],
    )

    assert result.exit_code == 1
    assert "Invalid Book" in result.stdout or "Could not determine" in result.stdout


def test_book_add_updates_catalog(tmp_path):
    """Test that 'rl book add' properly updates the catalog."""
    library_path = tmp_path / "library"
    ResourceLibrary.initialize(library_path)

    # Add first book manually
    create_test_book(library_path, "Existing Book", "Existing Author")

    # Add second book via CLI
    md_file = tmp_path / "new-book.md"
    md_file.write_text("# New Book\n\nContent.", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "book",
            "add",
            str(md_file),
            "--library",
            str(library_path),
            "--title",
            "New Book",
            "--author",
            "New Author",
        ],
    )

    assert result.exit_code == 0

    # Verify catalog has both books
    catalog_path = library_path / "catalog.yaml"
    catalog_data = yaml.safe_load(catalog_path.read_text())
    assert len(catalog_data["books"]) == 2

    titles = [book["title"] for book in catalog_data["books"]]
    assert "Existing Book" in titles
    assert "New Book" in titles


def test_book_add_with_isbn(tmp_path):
    """Test 'rl book add' with ISBN number."""
    library_path = tmp_path / "library"
    ResourceLibrary.initialize(library_path)

    md_file = tmp_path / "book.md"
    md_file.write_text("# Programming Book\n\nContent.", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "book",
            "add",
            str(md_file),
            "--library",
            str(library_path),
            "--title",
            "Programming Book",
            "--author",
            "Prog Author",
            "--isbn",
            "978-0-123456-78-9",
        ],
    )

    assert result.exit_code == 0
    assert "ISBN: 978-0-123456-78-9" in result.stdout


def test_book_add_author_name_parsing(tmp_path):
    """Test that 'rl book add' correctly parses author names."""
    library_path = tmp_path / "library"
    ResourceLibrary.initialize(library_path)

    md_file = tmp_path / "book.md"
    md_file.write_text("# Book\n\nContent.", encoding="utf-8")

    # Test with "Firstname Lastname" format
    result = runner.invoke(
        app,
        [
            "book",
            "add",
            str(md_file),
            "--library",
            str(library_path),
            "--title",
            "Test Book",
            "--author",
            "John Smith",
        ],
    )

    assert result.exit_code == 0

    # Verify folder structure follows lastname-firstname pattern
    catalog_path = library_path / "catalog.yaml"
    catalog_data = yaml.safe_load(catalog_path.read_text())
    folder_path = catalog_data["books"][0]["folder_path"]

    # Should be in format: books/smith-john/test-book
    assert "smith-john" in folder_path.lower()
