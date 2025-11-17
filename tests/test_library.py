"""Tests for ResourceLibrary class."""

import pytest
import json
from resourcelibrarian.library import ResourceLibrary


def test_initialize_creates_structure(tmp_path):
    """Test that initialize creates the complete directory structure."""
    library_path = tmp_path / "test-library"

    library = ResourceLibrary.initialize(library_path)

    # Check that library instance was created
    assert library is not None
    assert library.root == library_path

    # Check directory structure
    assert (library_path / ".metadata").exists()
    assert (library_path / "books").exists()
    assert (library_path / "books" / "_index").exists()
    assert (library_path / "videos").exists()
    assert (library_path / "videos" / "_index").exists()


def test_initialize_creates_catalog_file(tmp_path):
    """Test that initialize creates catalog.json with correct structure."""
    library_path = tmp_path / "test-library"

    ResourceLibrary.initialize(library_path)

    catalog_file = library_path / ".metadata" / "catalog.json"
    assert catalog_file.exists()

    catalog_data = json.loads(catalog_file.read_text())
    assert catalog_data["version"] == "1.0"
    assert catalog_data["books"] == []
    assert catalog_data["videos"] == []
    assert catalog_data["last_updated"] is None


def test_initialize_creates_video_state_file(tmp_path):
    """Test that initialize creates video_processing_state.json."""
    library_path = tmp_path / "test-library"

    ResourceLibrary.initialize(library_path)

    state_file = library_path / ".metadata" / "video_processing_state.json"
    assert state_file.exists()

    state_data = json.loads(state_file.read_text())
    assert state_data["processed"] == []
    assert state_data["failed"] == []
    assert state_data["pending"] == []


def test_initialize_creates_index_files(tmp_path):
    """Test that initialize creates index markdown files."""
    library_path = tmp_path / "test-library"

    ResourceLibrary.initialize(library_path)

    # Books indices
    assert (library_path / "books" / "_index" / "authors.md").exists()
    assert (library_path / "books" / "_index" / "titles.md").exists()

    # Videos indices
    assert (library_path / "videos" / "_index" / "channels.md").exists()


def test_initialize_raises_error_if_directory_exists(tmp_path):
    """Test that initialize raises FileExistsError if directory exists."""
    library_path = tmp_path / "test-library"
    library_path.mkdir()  # Create the directory first

    with pytest.raises(FileExistsError) as exc_info:
        ResourceLibrary.initialize(library_path)

    assert "already exists" in str(exc_info.value)


def test_exists_returns_true_for_valid_library(tmp_path):
    """Test that exists() returns True for a valid library."""
    library_path = tmp_path / "test-library"
    library = ResourceLibrary.initialize(library_path)

    assert library.exists() is True


def test_exists_returns_false_for_invalid_library(tmp_path):
    """Test that exists() returns False for an invalid library."""
    library_path = tmp_path / "nonexistent-library"
    library = ResourceLibrary(library_path)

    assert library.exists() is False


def test_library_init_sets_paths(tmp_path):
    """Test that __init__ correctly sets all paths."""
    library_path = tmp_path / "test-library"
    library = ResourceLibrary(library_path)

    assert library.root == library_path.resolve()
    assert library.metadata_dir == library_path.resolve() / ".metadata"
    assert library.catalog_path == library_path.resolve() / ".metadata" / "catalog.json"
    assert (
        library.video_state_path
        == library_path.resolve() / ".metadata" / "video_processing_state.json"
    )
    assert library.books_dir == library_path.resolve() / "books"
    assert library.videos_dir == library_path.resolve() / "videos"


def test_library_str_representation(tmp_path):
    """Test that __str__ returns a readable representation."""
    library_path = tmp_path / "test-library"
    library = ResourceLibrary(library_path)

    assert str(library) == f"ResourceLibrary({library_path.resolve()})"


def test_library_repr_representation(tmp_path):
    """Test that __repr__ returns a developer representation."""
    library_path = tmp_path / "test-library"
    library = ResourceLibrary(library_path)

    assert repr(library) == f"ResourceLibrary(root_path={library_path.resolve()!r})"
