"""Tests for I/O utility functions."""

import json
from pathlib import Path

import pytest
import yaml

from resourcelibrarian.models import BookManifest, VideoManifest
from resourcelibrarian.utils.io import (
    load_book_manifest,
    load_json,
    load_video_manifest,
    load_yaml,
    save_book_manifest,
    save_json,
    save_video_manifest,
    save_yaml,
)


# ========================================
# YAML I/O Tests
# ========================================


def test_save_and_load_yaml(tmp_path):
    """Test saving and loading YAML files."""
    test_data = {"title": "Test Book", "author": "Test Author", "tags": ["python", "testing"]}

    yaml_file = tmp_path / "test.yaml"
    save_yaml(test_data, yaml_file)

    assert yaml_file.exists()

    loaded_data = load_yaml(yaml_file)
    assert loaded_data == test_data


def test_save_yaml_creates_directories(tmp_path):
    """Test that save_yaml creates parent directories."""
    nested_path = tmp_path / "level1" / "level2" / "test.yaml"
    test_data = {"key": "value"}

    save_yaml(test_data, nested_path)

    assert nested_path.exists()
    assert nested_path.parent.exists()


def test_save_yaml_with_unicode(tmp_path):
    """Test saving YAML with Unicode characters."""
    test_data = {"title": "Тест", "author": "José García", "emoji": "📚"}

    yaml_file = tmp_path / "unicode.yaml"
    save_yaml(test_data, yaml_file)

    loaded_data = load_yaml(yaml_file)
    assert loaded_data == test_data


def test_load_yaml_file_not_found():
    """Test that load_yaml raises FileNotFoundError for missing files."""
    non_existent = Path("/nonexistent/file.yaml")

    with pytest.raises(FileNotFoundError, match="YAML file not found"):
        load_yaml(non_existent)


def test_load_yaml_invalid_yaml(tmp_path):
    """Test that load_yaml raises error for invalid YAML."""
    invalid_yaml = tmp_path / "invalid.yaml"
    invalid_yaml.write_text("{ invalid yaml content [")

    with pytest.raises(yaml.YAMLError):
        load_yaml(invalid_yaml)


# ========================================
# JSON I/O Tests
# ========================================


def test_save_and_load_json(tmp_path):
    """Test saving and loading JSON files."""
    test_data = {
        "total_books": 42,
        "authors": ["Alice", "Bob"],
        "stats": {"count": 100, "active": True},
    }

    json_file = tmp_path / "test.json"
    save_json(test_data, json_file)

    assert json_file.exists()

    loaded_data = load_json(json_file)
    assert loaded_data == test_data


def test_save_json_creates_directories(tmp_path):
    """Test that save_json creates parent directories."""
    nested_path = tmp_path / "deep" / "nested" / "path" / "test.json"
    test_data = {"nested": True}

    save_json(test_data, nested_path)

    assert nested_path.exists()


def test_save_json_with_custom_indent(tmp_path):
    """Test saving JSON with custom indentation."""
    test_data = {"key": "value", "list": [1, 2, 3]}
    json_file = tmp_path / "indented.json"

    save_json(test_data, json_file, indent=4)

    content = json_file.read_text()
    assert "    " in content  # Check for 4-space indentation


def test_save_json_with_unicode(tmp_path):
    """Test saving JSON with Unicode characters."""
    test_data = {"title": "日本語", "author": "François", "emoji": "🎉"}

    json_file = tmp_path / "unicode.json"
    save_json(test_data, json_file)

    loaded_data = load_json(json_file)
    assert loaded_data == test_data


def test_load_json_file_not_found():
    """Test that load_json raises FileNotFoundError for missing files."""
    non_existent = Path("/nonexistent/file.json")

    with pytest.raises(FileNotFoundError, match="JSON file not found"):
        load_json(non_existent)


def test_load_json_invalid_json(tmp_path):
    """Test that load_json raises error for invalid JSON."""
    invalid_json = tmp_path / "invalid.json"
    invalid_json.write_text("{ invalid json content [")

    with pytest.raises(json.JSONDecodeError):
        load_json(invalid_json)


# ========================================
# Book Manifest Tests
# ========================================


def test_save_and_load_book_manifest(tmp_path):
    """Test saving and loading book manifests."""
    manifest = BookManifest(
        title="Python Programming",
        author="Alice Johnson",
        source_folder="python-programming",
        categories=["programming", "python"],
        isbn="978-0123456789",
        tags=["beginner", "tutorial"],
    )

    book_folder = tmp_path / "books" / "python-programming"
    save_book_manifest(manifest, book_folder)

    manifest_file = book_folder / "manifest.yaml"
    assert manifest_file.exists()

    loaded_manifest = load_book_manifest(book_folder)
    assert loaded_manifest.title == manifest.title
    assert loaded_manifest.author == manifest.author
    assert loaded_manifest.isbn == manifest.isbn
    assert loaded_manifest.categories == manifest.categories
    assert loaded_manifest.tags == manifest.tags


def test_save_book_manifest_creates_folder(tmp_path):
    """Test that save_book_manifest creates the folder."""
    manifest = BookManifest(title="Test Book", author="Test Author", source_folder="test-book")

    book_folder = tmp_path / "new" / "book"
    save_book_manifest(manifest, book_folder)

    assert book_folder.exists()
    assert (book_folder / "manifest.yaml").exists()


def test_load_book_manifest_missing_file(tmp_path):
    """Test that load_book_manifest raises error when manifest is missing."""
    empty_folder = tmp_path / "empty"
    empty_folder.mkdir()

    with pytest.raises(FileNotFoundError, match="No manifest.yaml found"):
        load_book_manifest(empty_folder)


def test_book_manifest_round_trip_with_formats(tmp_path):
    """Test book manifest with formats and summaries."""
    manifest = BookManifest(
        title="Complete Book",
        author="Complete Author",
        source_folder="complete-book",
        formats={"pdf": "book.pdf", "epub": "book.epub", "markdown": "book.md"},
        summaries={"shortform": "summaries/short.md", "ai": "summaries/ai.md"},
    )

    book_folder = tmp_path / "complete"
    save_book_manifest(manifest, book_folder)

    loaded = load_book_manifest(book_folder)
    assert loaded.formats == manifest.formats
    assert loaded.summaries == manifest.summaries


# ========================================
# Video Manifest Tests
# ========================================


def test_save_and_load_video_manifest(tmp_path):
    """Test saving and loading video manifests."""
    manifest = VideoManifest(
        videoId="abc123xyz",
        title="Python Tutorial",
        channelId="UC123",
        channelTitle="Tech Channel",
        description="Learn Python basics",
        tags=["python", "tutorial"],
        categories=["education"],
    )

    video_folder = tmp_path / "videos" / "tech-channel" / "python-tutorial"
    save_video_manifest(manifest, video_folder)

    manifest_file = video_folder / "manifest.yaml"
    assert manifest_file.exists()

    loaded_manifest = load_video_manifest(video_folder)
    assert loaded_manifest.videoId == manifest.videoId
    assert loaded_manifest.title == manifest.title
    assert loaded_manifest.channelId == manifest.channelId
    assert loaded_manifest.channelTitle == manifest.channelTitle
    assert loaded_manifest.tags == manifest.tags


def test_save_video_manifest_creates_folder(tmp_path):
    """Test that save_video_manifest creates the folder."""
    manifest = VideoManifest(
        videoId="vid123", title="Test Video", channelId="ch1", channelTitle="Test Channel"
    )

    video_folder = tmp_path / "new" / "video"
    save_video_manifest(manifest, video_folder)

    assert video_folder.exists()
    assert (video_folder / "manifest.yaml").exists()


def test_load_video_manifest_missing_file(tmp_path):
    """Test that load_video_manifest raises error when manifest is missing."""
    empty_folder = tmp_path / "empty"
    empty_folder.mkdir()

    with pytest.raises(FileNotFoundError, match="No manifest.yaml found"):
        load_video_manifest(empty_folder)


def test_video_manifest_round_trip_with_sources(tmp_path):
    """Test video manifest with source files and summaries."""
    manifest = VideoManifest(
        videoId="xyz789",
        title="Complete Video",
        channelId="ch456",
        channelTitle="Complete Channel",
        source={"transcript_path": "transcript.txt", "url_file": "url.txt"},
        summaries={"ai": "summaries/ai.md", "shortform": "summaries/short.md"},
    )

    video_folder = tmp_path / "complete"
    save_video_manifest(manifest, video_folder)

    loaded = load_video_manifest(video_folder)
    assert loaded.source == manifest.source
    assert loaded.summaries == manifest.summaries


def test_video_manifest_with_datetime(tmp_path):
    """Test video manifest with publishedAt datetime."""
    from datetime import datetime

    manifest = VideoManifest(
        videoId="dt123",
        title="DateTime Test",
        channelId="ch1",
        channelTitle="Test",
        publishedAt=datetime(2024, 1, 15, 10, 30, 0),
    )

    video_folder = tmp_path / "datetime-test"
    save_video_manifest(manifest, video_folder)

    # Read the YAML to check datetime serialization
    yaml_content = (video_folder / "manifest.yaml").read_text()
    assert "2024-01-15T10:30:00" in yaml_content

    loaded = load_video_manifest(video_folder)
    assert loaded.publishedAt is not None
    assert loaded.publishedAt.year == 2024
    assert loaded.publishedAt.month == 1
    assert loaded.publishedAt.day == 15
