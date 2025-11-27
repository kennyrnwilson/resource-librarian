"""Tests for Resource Librarian data models."""

from datetime import datetime
from pathlib import Path

import pytest

from resourcelibrarian.models import (
    Book,
    BookManifest,
    LibraryCatalog,
    SourceKind,
    Video,
    VideoManifest,
)


# ========================================
# SourceKind Enum Tests
# ========================================


def test_source_kind_enum_values():
    """Test that SourceKind enum has expected values."""
    assert SourceKind.BOOK == "book"
    assert SourceKind.VIDEO == "video"


def test_source_kind_enum_is_string():
    """Test that SourceKind values are strings."""
    assert isinstance(SourceKind.BOOK, str)
    assert isinstance(SourceKind.VIDEO, str)


def test_source_kind_enum_iteration():
    """Test that we can iterate over SourceKind values."""
    values = list(SourceKind)
    assert len(values) == 2
    assert SourceKind.BOOK in values
    assert SourceKind.VIDEO in values


# ========================================
# BookManifest Tests
# ========================================


def test_book_manifest_creation_minimal():
    """Test creating BookManifest with minimal required fields."""
    manifest = BookManifest(
        title="Test Book", author="Test Author", source_folder="test-book"
    )

    assert manifest.title == "Test Book"
    assert manifest.author == "Test Author"
    assert manifest.source_folder == "test-book"
    assert manifest.categories == []
    assert manifest.isbn is None
    assert manifest.formats == {}
    assert manifest.summaries == {}
    assert manifest.tags == []
    assert manifest.embedding_status == "pending"


def test_book_manifest_creation_full():
    """Test creating BookManifest with all fields."""
    manifest = BookManifest(
        title="Complete Book",
        author="Complete Author",
        source_folder="complete-book",
        categories=["ai", "machine-learning"],
        isbn="978-0123456789",
        formats={"pdf": "book.pdf", "epub": "book.epub"},
        summaries={"shortform": "summaries/shortform.md"},
        tags=["python", "ml"],
        embedding_status="ready",
    )

    assert manifest.title == "Complete Book"
    assert manifest.author == "Complete Author"
    assert manifest.categories == ["ai", "machine-learning"]
    assert manifest.isbn == "978-0123456789"
    assert manifest.formats == {"pdf": "book.pdf", "epub": "book.epub"}
    assert manifest.summaries == {"shortform": "summaries/shortform.md"}
    assert manifest.tags == ["python", "ml"]
    assert manifest.embedding_status == "ready"


def test_book_manifest_to_yaml_dict():
    """Test BookManifest YAML serialization."""
    manifest = BookManifest(
        title="YAML Book",
        author="YAML Author",
        source_folder="yaml-book",
        isbn="123456789",
        categories=["test"],
        tags=["yaml"],
    )

    yaml_dict = manifest.to_yaml_dict()

    assert yaml_dict["title"] == "YAML Book"
    assert yaml_dict["author"] == "YAML Author"
    assert yaml_dict["source_folder"] == "yaml-book"
    assert yaml_dict["isbn"] == "123456789"
    assert yaml_dict["categories"] == ["test"]
    assert yaml_dict["tags"] == ["yaml"]
    assert yaml_dict["formats"] == {}
    assert yaml_dict["summaries"] == {}
    assert yaml_dict["embedding_status"] == "pending"


# ========================================
# Book Tests
# ========================================


def test_book_creation():
    """Test creating Book with manifest and folder path."""
    manifest = BookManifest(
        title="My Book", author="Author Name", source_folder="my-book"
    )
    book = Book(folder_path=Path("/library/books/my-book"), manifest=manifest)

    assert book.folder_path == Path("/library/books/my-book")
    assert book.manifest == manifest


def test_book_title_property():
    """Test Book title property."""
    manifest = BookManifest(
        title="Property Test", author="Test Author", source_folder="prop-test"
    )
    book = Book(folder_path=Path("/test"), manifest=manifest)

    assert book.title == "Property Test"


def test_book_author_property():
    """Test Book author property."""
    manifest = BookManifest(
        title="Test", author="Famous Author", source_folder="test"
    )
    book = Book(folder_path=Path("/test"), manifest=manifest)

    assert book.author == "Famous Author"


def test_book_categories_property():
    """Test Book categories property."""
    manifest = BookManifest(
        title="Test", author="Test", source_folder="test", categories=["ai", "ml"]
    )
    book = Book(folder_path=Path("/test"), manifest=manifest)

    assert book.categories == ["ai", "ml"]


def test_book_tags_property():
    """Test Book tags property."""
    manifest = BookManifest(
        title="Test",
        author="Test",
        source_folder="test",
        tags=["python", "advanced"],
    )
    book = Book(folder_path=Path("/test"), manifest=manifest)

    assert book.tags == ["python", "advanced"]


def test_book_source_folder_property():
    """Test Book source_folder property."""
    manifest = BookManifest(
        title="Test", author="Test", source_folder="original-folder"
    )
    book = Book(folder_path=Path("/test"), manifest=manifest)

    assert book.source_folder == "original-folder"


def test_book_get_format_path():
    """Test Book.get_format_path method."""
    manifest = BookManifest(
        title="Test",
        author="Test",
        source_folder="test",
        formats={"pdf": "book.pdf", "epub": "book.epub"},
    )
    book = Book(folder_path=Path("/library/books/test"), manifest=manifest)

    pdf_path = book.get_format_path("pdf")
    assert pdf_path == Path("/library/books/test/book.pdf")

    epub_path = book.get_format_path("epub")
    assert epub_path == Path("/library/books/test/book.epub")

    missing_path = book.get_format_path("mobi")
    assert missing_path is None


def test_book_get_summary_path():
    """Test Book.get_summary_path method."""
    manifest = BookManifest(
        title="Test",
        author="Test",
        source_folder="test",
        summaries={"shortform": "summaries/short.md", "ai": "summaries/ai.md"},
    )
    book = Book(folder_path=Path("/library/books/test"), manifest=manifest)

    short_path = book.get_summary_path("shortform")
    assert short_path == Path("/library/books/test/summaries/short.md")

    ai_path = book.get_summary_path("ai")
    assert ai_path == Path("/library/books/test/summaries/ai.md")

    missing_path = book.get_summary_path("missing")
    assert missing_path is None


def test_book_list_formats():
    """Test Book.list_formats method."""
    manifest = BookManifest(
        title="Test",
        author="Test",
        source_folder="test",
        formats={"pdf": "book.pdf", "epub": "book.epub", "markdown": "book.md"},
    )
    book = Book(folder_path=Path("/test"), manifest=manifest)

    formats = book.list_formats()
    assert set(formats) == {"pdf", "epub", "markdown"}


def test_book_list_summaries():
    """Test Book.list_summaries method."""
    manifest = BookManifest(
        title="Test",
        author="Test",
        source_folder="test",
        summaries={"shortform": "short.md", "ai": "ai.md"},
    )
    book = Book(folder_path=Path("/test"), manifest=manifest)

    summaries = book.list_summaries()
    assert set(summaries) == {"shortform", "ai"}


# ========================================
# VideoManifest Tests
# ========================================


def test_video_manifest_creation_minimal():
    """Test creating VideoManifest with minimal required fields."""
    manifest = VideoManifest(
        videoId="abc123", title="Test Video", channelId="ch123", channelTitle="Test Ch"
    )

    assert manifest.videoId == "abc123"
    assert manifest.title == "Test Video"
    assert manifest.channelId == "ch123"
    assert manifest.channelTitle == "Test Ch"
    assert manifest.description == ""
    assert manifest.url is None
    assert manifest.thumbnails == {}
    assert manifest.tags == []
    assert manifest.categories == []
    assert manifest.categoryId is None
    assert manifest.publishedAt is None
    assert manifest.defaultLanguage == "en"
    assert manifest.defaultAudioLanguage == "en"
    assert manifest.source == {}
    assert manifest.summaries == {}
    assert manifest.pointers == {}


def test_video_manifest_creation_full():
    """Test creating VideoManifest with all fields."""
    published = datetime(2024, 1, 1, 12, 0, 0)

    manifest = VideoManifest(
        videoId="xyz789",
        title="Complete Video",
        description="Full description",
        url="https://youtube.com/watch?v=xyz789",
        thumbnails={"default": "thumb.jpg"},
        channelId="ch456",
        channelTitle="Complete Channel",
        tags=["python", "tutorial"],
        categories=["programming"],
        categoryId="28",
        publishedAt=published,
        defaultLanguage="en",
        defaultAudioLanguage="en",
        source={"transcript_path": "transcript.txt"},
        summaries={"ai": "summary.md"},
        pointers={"intro": "0:00"},
    )

    assert manifest.videoId == "xyz789"
    assert manifest.title == "Complete Video"
    assert manifest.description == "Full description"
    assert manifest.url == "https://youtube.com/watch?v=xyz789"
    assert manifest.thumbnails == {"default": "thumb.jpg"}
    assert manifest.channelId == "ch456"
    assert manifest.channelTitle == "Complete Channel"
    assert manifest.tags == ["python", "tutorial"]
    assert manifest.categories == ["programming"]
    assert manifest.categoryId == "28"
    assert manifest.publishedAt == published
    assert manifest.source == {"transcript_path": "transcript.txt"}
    assert manifest.summaries == {"ai": "summary.md"}
    assert manifest.pointers == {"intro": "0:00"}


def test_video_manifest_to_yaml_dict():
    """Test VideoManifest YAML serialization."""
    published = datetime(2024, 6, 15, 10, 30, 0)

    manifest = VideoManifest(
        videoId="test123",
        title="YAML Video",
        channelId="ch789",
        channelTitle="YAML Channel",
        publishedAt=published,
        tags=["test"],
        categories=["demo"],
    )

    yaml_dict = manifest.to_yaml_dict()

    assert yaml_dict["videoId"] == "test123"
    assert yaml_dict["title"] == "YAML Video"
    assert yaml_dict["channelId"] == "ch789"
    assert yaml_dict["channelTitle"] == "YAML Channel"
    assert yaml_dict["publishedAt"] == "2024-06-15T10:30:00"
    assert yaml_dict["tags"] == ["test"]
    assert yaml_dict["categories"] == ["demo"]


def test_video_manifest_to_yaml_dict_none_published():
    """Test VideoManifest YAML serialization with None publishedAt."""
    manifest = VideoManifest(
        videoId="test456",
        title="No Date",
        channelId="ch111",
        channelTitle="Channel",
        publishedAt=None,
    )

    yaml_dict = manifest.to_yaml_dict()
    assert yaml_dict["publishedAt"] is None


# ========================================
# Video Tests
# ========================================


def test_video_creation():
    """Test creating Video with manifest and folder path."""
    manifest = VideoManifest(
        videoId="vid123", title="My Video", channelId="ch1", channelTitle="My Channel"
    )
    video = Video(
        folder_path=Path("/library/videos/my-channel/my-video"), manifest=manifest
    )

    assert video.folder_path == Path("/library/videos/my-channel/my-video")
    assert video.manifest == manifest


def test_video_id_property():
    """Test Video.video_id property."""
    manifest = VideoManifest(
        videoId="xyz999", title="Test", channelId="ch1", channelTitle="Test Ch"
    )
    video = Video(folder_path=Path("/test"), manifest=manifest)

    assert video.video_id == "xyz999"


def test_video_title_property():
    """Test Video.title property."""
    manifest = VideoManifest(
        videoId="vid1",
        title="Amazing Video",
        channelId="ch1",
        channelTitle="Test Ch",
    )
    video = Video(folder_path=Path("/test"), manifest=manifest)

    assert video.title == "Amazing Video"


def test_video_channel_id_property():
    """Test Video.channel_id property."""
    manifest = VideoManifest(
        videoId="vid1", title="Test", channelId="UCxyz123", channelTitle="Test Ch"
    )
    video = Video(folder_path=Path("/test"), manifest=manifest)

    assert video.channel_id == "UCxyz123"


def test_video_channel_title_property():
    """Test Video.channel_title property."""
    manifest = VideoManifest(
        videoId="vid1", title="Test", channelId="ch1", channelTitle="Great Channel"
    )
    video = Video(folder_path=Path("/test"), manifest=manifest)

    assert video.channel_title == "Great Channel"


def test_video_tags_property():
    """Test Video.tags property."""
    manifest = VideoManifest(
        videoId="vid1",
        title="Test",
        channelId="ch1",
        channelTitle="Test Ch",
        tags=["python", "coding"],
    )
    video = Video(folder_path=Path("/test"), manifest=manifest)

    assert video.tags == ["python", "coding"]


def test_video_published_at_property():
    """Test Video.published_at property."""
    published = datetime(2023, 12, 25, 15, 30, 0)
    manifest = VideoManifest(
        videoId="vid1",
        title="Test",
        channelId="ch1",
        channelTitle="Test Ch",
        publishedAt=published,
    )
    video = Video(folder_path=Path("/test"), manifest=manifest)

    assert video.published_at == published


def test_video_get_transcript_path():
    """Test Video.get_transcript_path method."""
    manifest = VideoManifest(
        videoId="vid1",
        title="Test",
        channelId="ch1",
        channelTitle="Test Ch",
        source={"transcript_path": "transcript.txt"},
    )
    video = Video(folder_path=Path("/library/videos/test"), manifest=manifest)

    transcript_path = video.get_transcript_path()
    assert transcript_path == Path("/library/videos/test/transcript.txt")


def test_video_get_transcript_path_missing():
    """Test Video.get_transcript_path returns None when not available."""
    manifest = VideoManifest(
        videoId="vid1", title="Test", channelId="ch1", channelTitle="Test Ch"
    )
    video = Video(folder_path=Path("/test"), manifest=manifest)

    transcript_path = video.get_transcript_path()
    assert transcript_path is None


def test_video_get_url_path():
    """Test Video.get_url_path method."""
    manifest = VideoManifest(
        videoId="vid1",
        title="Test",
        channelId="ch1",
        channelTitle="Test Ch",
        source={"url_file": "video_url.txt"},
    )
    video = Video(folder_path=Path("/library/videos/test"), manifest=manifest)

    url_path = video.get_url_path()
    assert url_path == Path("/library/videos/test/video_url.txt")


def test_video_get_url_path_missing():
    """Test Video.get_url_path returns None when not available."""
    manifest = VideoManifest(
        videoId="vid1", title="Test", channelId="ch1", channelTitle="Test Ch"
    )
    video = Video(folder_path=Path("/test"), manifest=manifest)

    url_path = video.get_url_path()
    assert url_path is None


def test_video_get_summary_path():
    """Test Video.get_summary_path method."""
    manifest = VideoManifest(
        videoId="vid1",
        title="Test",
        channelId="ch1",
        channelTitle="Test Ch",
        summaries={"ai": "summaries/ai.md", "shortform": "summaries/short.md"},
    )
    video = Video(folder_path=Path("/library/videos/test"), manifest=manifest)

    ai_path = video.get_summary_path("ai")
    assert ai_path == Path("/library/videos/test/summaries/ai.md")

    short_path = video.get_summary_path("shortform")
    assert short_path == Path("/library/videos/test/summaries/short.md")

    missing_path = video.get_summary_path("missing")
    assert missing_path is None


def test_video_list_summaries():
    """Test Video.list_summaries method."""
    manifest = VideoManifest(
        videoId="vid1",
        title="Test",
        channelId="ch1",
        channelTitle="Test Ch",
        summaries={"ai": "ai.md", "shortform": "short.md", "detailed": "detail.md"},
    )
    video = Video(folder_path=Path("/test"), manifest=manifest)

    summaries = video.list_summaries()
    assert set(summaries) == {"ai", "shortform", "detailed"}


# ========================================
# LibraryCatalog Tests
# ========================================


def test_library_catalog_creation_empty():
    """Test creating empty LibraryCatalog."""
    catalog = LibraryCatalog()

    assert catalog.books == []
    assert catalog.videos == []
    assert catalog.library_path is None
    assert catalog.last_updated is None


def test_library_catalog_creation_with_data():
    """Test creating LibraryCatalog with books and videos."""
    book_manifest = BookManifest(
        title="Test Book", author="Author", source_folder="test-book"
    )
    book = Book(folder_path=Path("/library/books/test"), manifest=book_manifest)

    video_manifest = VideoManifest(
        videoId="vid1", title="Test Video", channelId="ch1", channelTitle="Channel"
    )
    video = Video(folder_path=Path("/library/videos/test"), manifest=video_manifest)

    catalog = LibraryCatalog(
        books=[book],
        videos=[video],
        library_path=Path("/library"),
        last_updated="2024-01-01T00:00:00",
    )

    assert len(catalog.books) == 1
    assert len(catalog.videos) == 1
    assert catalog.library_path == Path("/library")
    assert catalog.last_updated == "2024-01-01T00:00:00"


def test_catalog_to_dict():
    """Test LibraryCatalog.to_dict method."""
    book_manifest = BookManifest(
        title="Dict Book", author="Author", source_folder="dict-book"
    )
    book = Book(folder_path=Path("/library/books/dict"), manifest=book_manifest)

    catalog = LibraryCatalog(
        books=[book], library_path=Path("/library"), last_updated="2024-01-01"
    )

    data = catalog.to_dict()

    assert "books" in data
    assert "videos" in data
    assert "library_path" in data
    assert "last_updated" in data
    assert "stats" in data

    assert len(data["books"]) == 1
    assert len(data["videos"]) == 0
    assert data["library_path"] == "/library"
    assert data["last_updated"] == "2024-01-01"
    assert data["stats"]["total_books"] == 1
    assert data["stats"]["total_videos"] == 0
    assert data["stats"]["total_items"] == 1


def test_catalog_find_book():
    """Test LibraryCatalog.find_book method."""
    book1 = Book(
        folder_path=Path("/test"),
        manifest=BookManifest(
            title="First Book", author="Author 1", source_folder="first"
        ),
    )
    book2 = Book(
        folder_path=Path("/test"),
        manifest=BookManifest(
            title="Second Book", author="Author 2", source_folder="second"
        ),
    )

    catalog = LibraryCatalog(books=[book1, book2])

    found = catalog.find_book("First Book")
    assert found is not None
    assert found.title == "First Book"

    found_case = catalog.find_book("second book")
    assert found_case is not None
    assert found_case.title == "Second Book"

    not_found = catalog.find_book("Missing Book")
    assert not_found is None


def test_catalog_find_video():
    """Test LibraryCatalog.find_video method."""
    video1 = Video(
        folder_path=Path("/test"),
        manifest=VideoManifest(
            videoId="vid1", title="Video 1", channelId="ch1", channelTitle="Channel"
        ),
    )
    video2 = Video(
        folder_path=Path("/test"),
        manifest=VideoManifest(
            videoId="vid2", title="Video 2", channelId="ch2", channelTitle="Channel"
        ),
    )

    catalog = LibraryCatalog(videos=[video1, video2])

    found = catalog.find_video("vid1")
    assert found is not None
    assert found.video_id == "vid1"

    found2 = catalog.find_video("vid2")
    assert found2 is not None
    assert found2.video_id == "vid2"

    not_found = catalog.find_video("vid999")
    assert not_found is None


def test_catalog_search_books_no_filters():
    """Test LibraryCatalog.search_books with no filters returns all books."""
    book1 = Book(
        folder_path=Path("/test"),
        manifest=BookManifest(title="Book 1", author="A1", source_folder="b1"),
    )
    book2 = Book(
        folder_path=Path("/test"),
        manifest=BookManifest(title="Book 2", author="A2", source_folder="b2"),
    )

    catalog = LibraryCatalog(books=[book1, book2])

    results = catalog.search_books()
    assert len(results) == 2


def test_catalog_search_books_by_author():
    """Test LibraryCatalog.search_books by author."""
    book1 = Book(
        folder_path=Path("/test"),
        manifest=BookManifest(title="Book 1", author="Alice", source_folder="b1"),
    )
    book2 = Book(
        folder_path=Path("/test"),
        manifest=BookManifest(title="Book 2", author="Bob", source_folder="b2"),
    )

    catalog = LibraryCatalog(books=[book1, book2])

    results = catalog.search_books(author="Alice")
    assert len(results) == 1
    assert results[0].author == "Alice"

    results_partial = catalog.search_books(author="lic")
    assert len(results_partial) == 1
    assert results_partial[0].author == "Alice"


def test_catalog_search_books_by_category():
    """Test LibraryCatalog.search_books by category."""
    book1 = Book(
        folder_path=Path("/test"),
        manifest=BookManifest(
            title="Book 1", author="A", source_folder="b1", categories=["ai", "ml"]
        ),
    )
    book2 = Book(
        folder_path=Path("/test"),
        manifest=BookManifest(
            title="Book 2", author="A", source_folder="b2", categories=["web"]
        ),
    )

    catalog = LibraryCatalog(books=[book1, book2])

    results = catalog.search_books(category="ai")
    assert len(results) == 1
    assert "ai" in results[0].categories


def test_catalog_search_books_by_tag():
    """Test LibraryCatalog.search_books by tag."""
    book1 = Book(
        folder_path=Path("/test"),
        manifest=BookManifest(
            title="Book 1", author="A", source_folder="b1", tags=["python", "advanced"]
        ),
    )
    book2 = Book(
        folder_path=Path("/test"),
        manifest=BookManifest(
            title="Book 2", author="A", source_folder="b2", tags=["javascript"]
        ),
    )

    catalog = LibraryCatalog(books=[book1, book2])

    results = catalog.search_books(tag="python")
    assert len(results) == 1
    assert "python" in results[0].tags


def test_catalog_search_books_by_title():
    """Test LibraryCatalog.search_books by title."""
    book1 = Book(
        folder_path=Path("/test"),
        manifest=BookManifest(
            title="Python Programming", author="A", source_folder="b1"
        ),
    )
    book2 = Book(
        folder_path=Path("/test"),
        manifest=BookManifest(
            title="JavaScript Guide", author="A", source_folder="b2"
        ),
    )

    catalog = LibraryCatalog(books=[book1, book2])

    results = catalog.search_books(title="Python")
    assert len(results) == 1
    assert "Python" in results[0].title


def test_catalog_search_books_multiple_filters():
    """Test LibraryCatalog.search_books with multiple filters."""
    book1 = Book(
        folder_path=Path("/test"),
        manifest=BookManifest(
            title="AI with Python",
            author="Alice",
            source_folder="b1",
            categories=["ai"],
            tags=["python"],
        ),
    )
    book2 = Book(
        folder_path=Path("/test"),
        manifest=BookManifest(
            title="Web Development",
            author="Bob",
            source_folder="b2",
            categories=["web"],
            tags=["javascript"],
        ),
    )

    catalog = LibraryCatalog(books=[book1, book2])

    results = catalog.search_books(author="Alice", category="ai", tag="python")
    assert len(results) == 1
    assert results[0].title == "AI with Python"

    results_no_match = catalog.search_books(author="Alice", category="web")
    assert len(results_no_match) == 0


def test_catalog_search_videos_no_filters():
    """Test LibraryCatalog.search_videos with no filters returns all videos."""
    video1 = Video(
        folder_path=Path("/test"),
        manifest=VideoManifest(
            videoId="v1", title="Vid 1", channelId="ch1", channelTitle="Channel 1"
        ),
    )
    video2 = Video(
        folder_path=Path("/test"),
        manifest=VideoManifest(
            videoId="v2", title="Vid 2", channelId="ch2", channelTitle="Channel 2"
        ),
    )

    catalog = LibraryCatalog(videos=[video1, video2])

    results = catalog.search_videos()
    assert len(results) == 2


def test_catalog_search_videos_by_channel():
    """Test LibraryCatalog.search_videos by channel."""
    video1 = Video(
        folder_path=Path("/test"),
        manifest=VideoManifest(
            videoId="v1", title="Vid 1", channelId="ch1", channelTitle="Tech Channel"
        ),
    )
    video2 = Video(
        folder_path=Path("/test"),
        manifest=VideoManifest(
            videoId="v2", title="Vid 2", channelId="ch2", channelTitle="Cooking Show"
        ),
    )

    catalog = LibraryCatalog(videos=[video1, video2])

    results = catalog.search_videos(channel="Tech")
    assert len(results) == 1
    assert results[0].channel_title == "Tech Channel"


def test_catalog_search_videos_by_category():
    """Test LibraryCatalog.search_videos by category."""
    video1 = Video(
        folder_path=Path("/test"),
        manifest=VideoManifest(
            videoId="v1",
            title="Vid 1",
            channelId="ch1",
            channelTitle="Ch1",
            categories=["ai", "tutorial"],
        ),
    )
    video2 = Video(
        folder_path=Path("/test"),
        manifest=VideoManifest(
            videoId="v2",
            title="Vid 2",
            channelId="ch2",
            channelTitle="Ch2",
            categories=["gaming"],
        ),
    )

    catalog = LibraryCatalog(videos=[video1, video2])

    results = catalog.search_videos(category="tutorial")
    assert len(results) == 1
    assert "tutorial" in results[0].manifest.categories


def test_catalog_search_videos_by_tag():
    """Test LibraryCatalog.search_videos by tag."""
    video1 = Video(
        folder_path=Path("/test"),
        manifest=VideoManifest(
            videoId="v1",
            title="Vid 1",
            channelId="ch1",
            channelTitle="Ch1",
            tags=["python", "coding"],
        ),
    )
    video2 = Video(
        folder_path=Path("/test"),
        manifest=VideoManifest(
            videoId="v2",
            title="Vid 2",
            channelId="ch2",
            channelTitle="Ch2",
            tags=["gaming"],
        ),
    )

    catalog = LibraryCatalog(videos=[video1, video2])

    results = catalog.search_videos(tag="coding")
    assert len(results) == 1
    assert "coding" in results[0].tags


def test_catalog_search_videos_by_title():
    """Test LibraryCatalog.search_videos by title."""
    video1 = Video(
        folder_path=Path("/test"),
        manifest=VideoManifest(
            videoId="v1",
            title="Python Tutorial",
            channelId="ch1",
            channelTitle="Ch1",
        ),
    )
    video2 = Video(
        folder_path=Path("/test"),
        manifest=VideoManifest(
            videoId="v2", title="JavaScript Basics", channelId="ch2", channelTitle="Ch2"
        ),
    )

    catalog = LibraryCatalog(videos=[video1, video2])

    results = catalog.search_videos(title="Python")
    assert len(results) == 1
    assert "Python" in results[0].title


def test_catalog_get_all_authors():
    """Test LibraryCatalog.get_all_authors method."""
    book1 = Book(
        folder_path=Path("/test"),
        manifest=BookManifest(title="B1", author="Alice", source_folder="b1"),
    )
    book2 = Book(
        folder_path=Path("/test"),
        manifest=BookManifest(title="B2", author="Bob", source_folder="b2"),
    )
    book3 = Book(
        folder_path=Path("/test"),
        manifest=BookManifest(title="B3", author="Alice", source_folder="b3"),
    )

    catalog = LibraryCatalog(books=[book1, book2, book3])

    authors = catalog.get_all_authors()
    assert authors == ["Alice", "Bob"]


def test_catalog_get_all_categories():
    """Test LibraryCatalog.get_all_categories method."""
    book1 = Book(
        folder_path=Path("/test"),
        manifest=BookManifest(
            title="B1", author="A", source_folder="b1", categories=["ai", "ml"]
        ),
    )
    video1 = Video(
        folder_path=Path("/test"),
        manifest=VideoManifest(
            videoId="v1",
            title="V1",
            channelId="ch1",
            channelTitle="Ch1",
            categories=["tutorial", "ai"],
        ),
    )

    catalog = LibraryCatalog(books=[book1], videos=[video1])

    categories = catalog.get_all_categories()
    assert set(categories) == {"ai", "ml", "tutorial"}


def test_catalog_get_all_tags():
    """Test LibraryCatalog.get_all_tags method."""
    book1 = Book(
        folder_path=Path("/test"),
        manifest=BookManifest(
            title="B1", author="A", source_folder="b1", tags=["python", "advanced"]
        ),
    )
    video1 = Video(
        folder_path=Path("/test"),
        manifest=VideoManifest(
            videoId="v1",
            title="V1",
            channelId="ch1",
            channelTitle="Ch1",
            tags=["coding", "python"],
        ),
    )

    catalog = LibraryCatalog(books=[book1], videos=[video1])

    tags = catalog.get_all_tags()
    assert set(tags) == {"python", "advanced", "coding"}


def test_catalog_get_stats():
    """Test LibraryCatalog.get_stats method."""
    book1 = Book(
        folder_path=Path("/test"),
        manifest=BookManifest(
            title="B1",
            author="Alice",
            source_folder="b1",
            formats={"pdf": "b.pdf", "epub": "b.epub"},
            summaries={"short": "s.md"},
            categories=["ai"],
            tags=["python"],
        ),
    )
    book2 = Book(
        folder_path=Path("/test"),
        manifest=BookManifest(
            title="B2",
            author="Bob",
            source_folder="b2",
            formats={"pdf": "b.pdf"},
            categories=["web"],
        ),
    )
    video1 = Video(
        folder_path=Path("/test"),
        manifest=VideoManifest(
            videoId="v1",
            title="V1",
            channelId="ch1",
            channelTitle="Ch1",
            summaries={"ai": "ai.md"},
            categories=["tutorial"],
        ),
    )

    catalog = LibraryCatalog(
        books=[book1, book2], videos=[video1], last_updated="2024-01-01"
    )

    stats = catalog.get_stats()

    assert stats["total_books"] == 2
    assert stats["total_videos"] == 1
    assert stats["total_items"] == 3
    assert stats["unique_authors"] == 2
    assert stats["unique_categories"] == 3
    assert stats["unique_tags"] == 1
    assert stats["book_formats"] == 3  # 2 + 1
    assert stats["book_summaries"] == 1
    assert stats["video_summaries"] == 1
    assert stats["last_updated"] == "2024-01-01"
