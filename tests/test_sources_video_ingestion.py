"""Tests for video ingestion functionality."""

import pytest

from resourcelibrarian.sources.video_ingestion import (
    VideoIngestion,
    create_channel_folder_name,
    create_video_folder_name,
    extract_video_id,
    slugify,
)


def test_slugify():
    """Test slugify function."""
    assert slugify("Hello World") == "hello-world"
    assert slugify("Test-Title!") == "test-title"
    assert slugify("Multiple   Spaces") == "multiple-spaces"
    assert slugify("Special@#$Characters") == "specialcharacters"
    assert slugify("  Leading and Trailing  ") == "leading-and-trailing"


def test_extract_video_id():
    """Test extracting video ID from various YouTube URL formats."""
    # Standard watch URL
    assert extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    # Short URL
    assert extract_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    # Embed URL
    assert extract_video_id("https://www.youtube.com/embed/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    # With additional parameters
    assert (
        extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ&feature=share")
        == "dQw4w9WgXcQ"
    )

    # Just the ID
    assert extract_video_id("dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    # Invalid inputs
    assert extract_video_id("not-a-valid-url") is None
    assert extract_video_id("https://example.com") is None
    assert extract_video_id("short-id") is None  # Not 11 characters


def test_create_video_folder_name():
    """Test video folder name creation."""
    assert create_video_folder_name("abc123def45", "Test Video") == "abc123def45__test-video"
    assert create_video_folder_name("xyz789", "Another Test!") == "xyz789__another-test"

    # Test long title truncation
    long_title = "A" * 100
    folder_name = create_video_folder_name("test12345", long_title)
    assert len(folder_name.split("__")[1]) <= 50


def test_create_channel_folder_name():
    """Test channel folder name creation."""
    assert create_channel_folder_name("UC123456", "Tech Channel") == "tech-channel__UC123456"
    assert create_channel_folder_name("UC789xyz", "Cool Videos!") == "cool-videos__UC789xyz"

    # Test long channel name truncation
    long_channel = "B" * 100
    folder_name = create_channel_folder_name("UC123", long_channel)
    assert len(folder_name.split("__")[0]) <= 50


def test_video_ingestion_add_video(tmp_path):
    """Test adding a video with VideoIngestion."""
    library_path = tmp_path / "library"
    library_path.mkdir()
    (library_path / "videos").mkdir()

    ingestion = VideoIngestion(library_path)

    # Sample video metadata
    video_metadata = {
        "videoId": "test123",
        "title": "Test Video",
        "description": "A test video description",
        "channelId": "UCtest456",
        "channelTitle": "Test Channel",
        "tags": ["test", "sample"],
        "publishedAt": "2024-01-01T00:00:00Z",
    }

    transcript_text = "This is a test transcript."

    # Add the video
    video = ingestion.add_video(
        video_metadata=video_metadata,
        transcript_text=transcript_text,
        categories=["Education"],
        tags=["tutorial"],
    )

    # Verify video object
    assert video.video_id == "test123"
    assert video.title == "Test Video"
    assert video.channel_title == "Test Channel"
    assert "Education" in video.manifest.categories
    assert "tutorial" in video.manifest.tags

    # Verify folder structure exists
    assert video.folder_path.exists()
    assert (video.folder_path / "source").exists()
    assert (video.folder_path / "summaries").exists()
    assert (video.folder_path / "pointers").exists()

    # Verify transcript file
    transcript_path = video.folder_path / "source" / "transcript.txt"
    assert transcript_path.exists()
    assert transcript_path.read_text() == transcript_text

    # Verify URL file
    url_path = video.folder_path / "source" / "video.url"
    assert url_path.exists()
    assert url_path.read_text() == "https://www.youtube.com/watch?v=test123"

    # Verify manifest exists
    manifest_path = video.folder_path / "manifest.yaml"
    assert manifest_path.exists()


def test_video_ingestion_missing_metadata_fields(tmp_path):
    """Test that VideoIngestion raises error when required fields are missing."""
    library_path = tmp_path / "library"
    library_path.mkdir()
    (library_path / "videos").mkdir()

    ingestion = VideoIngestion(library_path)

    # Missing video_id
    with pytest.raises(ValueError, match="Missing required video metadata fields"):
        ingestion.add_video(
            video_metadata={
                "title": "Test",
                "channelId": "UC123",
                "channelTitle": "Channel",
            },
            transcript_text="Transcript",
        )

    # Missing title
    with pytest.raises(ValueError, match="Missing required video metadata fields"):
        ingestion.add_video(
            video_metadata={
                "videoId": "test123",
                "channelId": "UC123",
                "channelTitle": "Channel",
            },
            transcript_text="Transcript",
        )


def test_video_ingestion_duplicate_video(tmp_path):
    """Test that adding duplicate video raises error."""
    library_path = tmp_path / "library"
    library_path.mkdir()
    (library_path / "videos").mkdir()

    ingestion = VideoIngestion(library_path)

    video_metadata = {
        "videoId": "test123",
        "title": "Test Video",
        "channelId": "UC123",
        "channelTitle": "Test Channel",
    }

    # Add video first time
    ingestion.add_video(
        video_metadata=video_metadata,
        transcript_text="First transcript",
    )

    # Try to add same video again
    with pytest.raises(ValueError, match="Video already exists"):
        ingestion.add_video(
            video_metadata=video_metadata,
            transcript_text="Second transcript",
        )


def test_video_ingestion_parses_published_date(tmp_path):
    """Test that VideoIngestion correctly parses publishedAt date."""
    library_path = tmp_path / "library"
    library_path.mkdir()
    (library_path / "videos").mkdir()

    ingestion = VideoIngestion(library_path)

    video_metadata = {
        "videoId": "test123",
        "title": "Test Video",
        "channelId": "UC123",
        "channelTitle": "Test Channel",
        "publishedAt": "2024-01-15T10:30:00Z",
    }

    video = ingestion.add_video(
        video_metadata=video_metadata,
        transcript_text="Transcript",
    )

    # Verify date was parsed
    assert video.manifest.publishedAt is not None
    assert video.manifest.publishedAt.year == 2024
    assert video.manifest.publishedAt.month == 1
    assert video.manifest.publishedAt.day == 15


def test_video_ingestion_handles_alternate_field_names(tmp_path):
    """Test that VideoIngestion handles alternate field names (snake_case vs camelCase)."""
    library_path = tmp_path / "library"
    library_path.mkdir()
    (library_path / "videos").mkdir()

    ingestion = VideoIngestion(library_path)

    # Use snake_case field names (some APIs return these)
    video_metadata = {
        "video_id": "test123",
        "title": "Test Video",
        "channel_id": "UC123",
        "channel_title": "Test Channel",
        "published_at": "2024-01-01T00:00:00Z",
    }

    video = ingestion.add_video(
        video_metadata=video_metadata,
        transcript_text="Transcript",
    )

    assert video.video_id == "test123"
    assert video.channel_id == "UC123"
    assert video.channel_title == "Test Channel"
