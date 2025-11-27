"""CLI integration tests for video commands.

Tests the 'rl video list' and 'rl video get' commands.
"""

import yaml
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from resourcelibrarian.cli.commands import app
from resourcelibrarian.library import ResourceLibrary
from resourcelibrarian.models.video import Video, VideoManifest
from resourcelibrarian.utils.io import save_video_manifest, save_yaml

runner = CliRunner()


def create_test_video(
    library_path: Path,
    video_id: str,
    title: str,
    channel_title: str,
    channel_id: str = "UCtest123",
    categories: list[str] = None,
    tags: list[str] = None,
    transcript_content: str = "Sample video transcript",
) -> Video:
    """Helper to create a test video in the library.

    Args:
        library_path: Path to the library root
        video_id: YouTube video ID
        title: Video title
        channel_title: Channel name
        channel_id: YouTube channel ID
        categories: List of categories
        tags: List of tags
        transcript_content: Content for the transcript file

    Returns:
        Video instance
    """
    # Create folder structure: videos/channel__id/videoid__title/
    channel_slug = f"{channel_title.lower().replace(' ', '-')}__{channel_id}"
    title_slug = title.lower().replace(" ", "-")
    video_folder = library_path / "videos" / channel_slug / f"{video_id}__{title_slug}"
    video_folder.mkdir(parents=True)

    # Create source directory
    source_dir = video_folder / "source"
    source_dir.mkdir()

    # Create transcript file
    transcript_path = source_dir / "transcript.txt"
    transcript_path.write_text(transcript_content, encoding="utf-8")

    # Create manifest
    manifest = VideoManifest(
        videoId=video_id,
        title=title,
        description=f"Description for {title}",
        url=f"https://www.youtube.com/watch?v={video_id}",
        channelId=channel_id,
        channelTitle=channel_title,
        tags=tags or [],
        categories=categories or [],
        publishedAt=datetime(2024, 1, 1),
        source={"transcript_path": "source/transcript.txt"},
    )

    save_video_manifest(manifest, video_folder)

    # Add to catalog
    catalog_path = library_path / "catalog.yaml"
    catalog_data = yaml.safe_load(catalog_path.read_text())
    catalog_data["videos"].append(
        {
            "video_id": video_id,
            "title": title,
            "channel_title": channel_title,
            "folder_path": str(video_folder),
        }
    )
    save_yaml(catalog_data, catalog_path)

    return Video(folder_path=video_folder, manifest=manifest)


# ============================================================================
# Tests for 'rl video list'
# ============================================================================


def test_video_list_shows_all_videos(tmp_path):
    """Test that 'rl video list' shows all videos in the library."""
    library_path = tmp_path / "library"
    ResourceLibrary.initialize(library_path)

    # Add test videos
    create_test_video(
        library_path,
        "abc123",
        "AI Introduction",
        "Tech Channel",
        categories=["AI"],
    )
    create_test_video(
        library_path,
        "def456",
        "Machine Learning Basics",
        "ML Academy",
        categories=["ML"],
    )

    result = runner.invoke(app, ["video", "list", "--library", str(library_path)])

    assert result.exit_code == 0
    assert "Videos in Library (2 found)" in result.stdout
    assert "AI Introduction" in result.stdout
    assert "Machine Learning Basics" in result.stdout
    assert "Tech Channel" in result.stdout
    assert "ML Academy" in result.stdout


def test_video_list_empty_library(tmp_path):
    """Test 'rl video list' with empty library."""
    library_path = tmp_path / "library"
    ResourceLibrary.initialize(library_path)

    result = runner.invoke(app, ["video", "list", "--library", str(library_path)])

    assert result.exit_code == 0
    assert "No videos in library yet" in result.stdout


def test_video_list_filter_by_channel(tmp_path):
    """Test 'rl video list --channel' filters correctly."""
    library_path = tmp_path / "library"
    ResourceLibrary.initialize(library_path)

    create_test_video(
        library_path, "abc123", "AI Introduction", "Tech Channel", categories=["AI"]
    )
    create_test_video(
        library_path, "def456", "Python Tutorial", "Code Academy", categories=["Programming"]
    )

    result = runner.invoke(
        app, ["video", "list", "--library", str(library_path), "--channel", "Tech"]
    )

    assert result.exit_code == 0
    assert "AI Introduction" in result.stdout
    assert "Python Tutorial" not in result.stdout


def test_video_list_filter_by_category(tmp_path):
    """Test 'rl video list --category' filters correctly."""
    library_path = tmp_path / "library"
    ResourceLibrary.initialize(library_path)

    create_test_video(
        library_path, "abc123", "AI Introduction", "Tech Channel", categories=["AI", "Tutorials"]
    )
    create_test_video(
        library_path, "def456", "Python Tutorial", "Code Academy", categories=["Programming"]
    )

    result = runner.invoke(
        app, ["video", "list", "--library", str(library_path), "--category", "AI"]
    )

    assert result.exit_code == 0
    assert "AI Introduction" in result.stdout
    assert "Python Tutorial" not in result.stdout


def test_video_list_filter_by_tag(tmp_path):
    """Test 'rl video list --tag' filters correctly."""
    library_path = tmp_path / "library"
    ResourceLibrary.initialize(library_path)

    create_test_video(
        library_path, "abc123", "AI Introduction", "Tech Channel", tags=["beginner", "ai"]
    )
    create_test_video(
        library_path, "def456", "Advanced ML", "ML Academy", tags=["advanced", "ml"]
    )

    result = runner.invoke(
        app, ["video", "list", "--library", str(library_path), "--tag", "beginner"]
    )

    assert result.exit_code == 0
    assert "AI Introduction" in result.stdout
    assert "Advanced ML" not in result.stdout


def test_video_list_filter_by_title(tmp_path):
    """Test 'rl video list --title' filters correctly."""
    library_path = tmp_path / "library"
    ResourceLibrary.initialize(library_path)

    create_test_video(library_path, "abc123", "AI Introduction", "Tech Channel")
    create_test_video(library_path, "def456", "Machine Learning Basics", "ML Academy")

    result = runner.invoke(
        app, ["video", "list", "--library", str(library_path), "--title", "Introduction"]
    )

    assert result.exit_code == 0
    assert "AI Introduction" in result.stdout
    assert "Machine Learning Basics" not in result.stdout


def test_video_list_multiple_filters(tmp_path):
    """Test 'rl video list' with multiple filters."""
    library_path = tmp_path / "library"
    ResourceLibrary.initialize(library_path)

    create_test_video(
        library_path,
        "abc123",
        "AI Introduction",
        "Tech Channel",
        categories=["AI"],
        tags=["beginner"],
    )
    create_test_video(
        library_path,
        "def456",
        "Advanced AI",
        "Tech Channel",
        categories=["AI"],
        tags=["advanced"],
    )
    create_test_video(
        library_path,
        "ghi789",
        "Python Basics",
        "Code Academy",
        categories=["Programming"],
        tags=["beginner"],
    )

    result = runner.invoke(
        app,
        [
            "video",
            "list",
            "--library",
            str(library_path),
            "--channel",
            "Tech",
            "--tag",
            "beginner",
        ],
    )

    assert result.exit_code == 0
    assert "AI Introduction" in result.stdout
    assert "Advanced AI" not in result.stdout  # wrong tag
    assert "Python Basics" not in result.stdout  # wrong channel


def test_video_list_no_matches(tmp_path):
    """Test 'rl video list' with no matching results."""
    library_path = tmp_path / "library"
    ResourceLibrary.initialize(library_path)

    create_test_video(library_path, "abc123", "AI Introduction", "Tech Channel")

    result = runner.invoke(
        app, ["video", "list", "--library", str(library_path), "--channel", "Nonexistent"]
    )

    assert result.exit_code == 0
    assert "No videos found matching filters" in result.stdout


def test_video_list_library_not_found(tmp_path):
    """Test 'rl video list' with non-existent library."""
    result = runner.invoke(
        app, ["video", "list", "--library", str(tmp_path / "nonexistent")]
    )

    assert result.exit_code == 1
    assert "Not a valid Resource Library" in result.stdout


# ============================================================================
# Tests for 'rl video get'
# ============================================================================


def test_video_get_retrieves_transcript(tmp_path):
    """Test that 'rl video get' retrieves video transcript."""
    library_path = tmp_path / "library"
    ResourceLibrary.initialize(library_path)

    create_test_video(
        library_path,
        "abc123",
        "AI Introduction",
        "Tech Channel",
        transcript_content="This is the AI introduction transcript.",
    )

    result = runner.invoke(app, ["video", "get", "abc123", "--library", str(library_path)])

    assert result.exit_code == 0
    assert "AI Introduction" in result.stdout
    assert "Tech Channel" in result.stdout
    assert "abc123" in result.stdout
    assert "This is the AI introduction transcript." in result.stdout


def test_video_get_saves_to_file(tmp_path):
    """Test that 'rl video get --output' saves transcript to file."""
    library_path = tmp_path / "library"
    ResourceLibrary.initialize(library_path)

    create_test_video(
        library_path,
        "abc123",
        "AI Introduction",
        "Tech Channel",
        transcript_content="This is the AI introduction transcript.",
    )

    output_file = tmp_path / "transcript.txt"
    result = runner.invoke(
        app,
        [
            "video",
            "get",
            "abc123",
            "--library",
            str(library_path),
            "--output",
            str(output_file),
        ],
    )

    assert result.exit_code == 0
    assert "Transcript written to" in result.stdout
    assert output_file.exists()
    assert output_file.read_text() == "This is the AI introduction transcript."


def test_video_get_video_not_found(tmp_path):
    """Test 'rl video get' with non-existent video."""
    library_path = tmp_path / "library"
    ResourceLibrary.initialize(library_path)

    result = runner.invoke(app, ["video", "get", "nonexistent", "--library", str(library_path)])

    assert result.exit_code == 1
    assert "Video not found" in result.stdout


def test_video_get_library_not_found(tmp_path):
    """Test 'rl video get' with non-existent library."""
    result = runner.invoke(
        app, ["video", "get", "abc123", "--library", str(tmp_path / "nonexistent")]
    )

    assert result.exit_code == 1
    assert "Not a valid Resource Library" in result.stdout


# ============================================================================
# Tests for 'rl video fetch'
# ============================================================================


def test_video_fetch_shows_not_implemented(tmp_path):
    """Test that 'rl video fetch' fails when YouTube API key is missing."""
    library_path = tmp_path / "library"
    ResourceLibrary.initialize(library_path)

    # Make sure YOUTUBE_API_KEY is not set
    import os
    old_key = os.environ.get("YOUTUBE_API_KEY")
    if old_key:
        del os.environ["YOUTUBE_API_KEY"]

    try:
        result = runner.invoke(
            app,
            [
                "video",
                "fetch",
                "dQw4w9WgXcQ",
                "--library",
                str(library_path),
            ],
        )

        assert result.exit_code == 1
        assert "YouTube API key required" in result.stdout
    finally:
        # Restore old key if it existed
        if old_key:
            os.environ["YOUTUBE_API_KEY"] = old_key


def test_video_fetch_invalid_url(tmp_path):
    """Test 'rl video fetch' with invalid YouTube URL."""
    library_path = tmp_path / "library"
    ResourceLibrary.initialize(library_path)

    result = runner.invoke(
        app,
        [
            "video",
            "fetch",
            "not-a-valid-url",
            "--library",
            str(library_path),
        ],
    )

    assert result.exit_code == 1
    assert "Invalid YouTube video URL or ID" in result.stdout


def test_video_fetch_library_not_found(tmp_path):
    """Test 'rl video fetch' with non-existent library."""
    result = runner.invoke(
        app,
        [
            "video",
            "fetch",
            "dQw4w9WgXcQ",
            "--library",
            str(tmp_path / "nonexistent"),
        ],
    )

    assert result.exit_code == 1
    assert "Not a valid Resource Library" in result.stdout


def test_video_fetch_extracts_video_id_from_urls(tmp_path):
    """Test that video fetch correctly extracts video IDs from various URL formats."""
    library_path = tmp_path / "library"
    ResourceLibrary.initialize(library_path)

    # Test various URL formats - all should extract the same video ID
    test_urls = [
        "dQw4w9WgXcQ",  # Just the ID
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Standard URL
        "https://youtu.be/dQw4w9WgXcQ",  # Short URL
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ&feature=share",  # With params
    ]

    for url in test_urls:
        result = runner.invoke(
            app,
            [
                "video",
                "fetch",
                url,
                "--library",
                str(library_path),
            ],
        )

        # All should show the processing message with the video ID
        assert "dQw4w9WgXcQ" in result.stdout or "Fetching YouTube video" in result.stdout


def test_video_fetch_with_categories_and_tags(tmp_path):
    """Test 'rl video fetch' with categories and tags options."""
    library_path = tmp_path / "library"
    ResourceLibrary.initialize(library_path)

    # Make sure API key is not set (will fail, but we can test arg parsing)
    import os
    old_key = os.environ.get("YOUTUBE_API_KEY")
    if old_key:
        del os.environ["YOUTUBE_API_KEY"]

    try:
        result = runner.invoke(
            app,
            [
                "video",
                "fetch",
                "dQw4w9WgXcQ",
                "--library",
                str(library_path),
                "--categories",
                "Music,Entertainment",
                "--tags",
                "test,sample",
            ],
        )

        # Should fail due to missing API key
        assert result.exit_code == 1
        assert "YouTube API key required" in result.stdout
    finally:
        if old_key:
            os.environ["YOUTUBE_API_KEY"] = old_key


def test_video_fetch_successfully_adds_video_with_mocks(tmp_path):
    """Test successful video fetch with mocked YouTube API and transcript."""
    library_path = tmp_path / "library"
    ResourceLibrary.initialize(library_path)

    # Use a valid 11-character video ID
    video_id = "dQw4w9WgXcQ"

    # Mock video metadata
    mock_metadata = {
        "videoId": video_id,
        "title": "Test Video",
        "description": "A test video",
        "thumbnails": {},
        "channelId": "UCtest456789",
        "channelTitle": "Test Channel",
        "tags": ["test"],
        "categoryId": "22",
        "publishedAt": "2024-01-01T00:00:00Z",
        "defaultLanguage": "en",
        "defaultAudioLanguage": "en",
    }

    mock_transcript = "This is a test transcript."

    # Mock the YouTube API and Transcript classes
    with patch("resourcelibrarian.sources.video_ingestion.YouTubeAPI") as MockAPI, \
         patch("resourcelibrarian.sources.video_ingestion.YouTubeTranscript") as MockTranscript:

        # Configure mocks
        mock_api_instance = MagicMock()
        mock_api_instance.fetch_single_video.return_value = mock_metadata
        MockAPI.return_value = mock_api_instance

        MockTranscript.fetch_transcript.return_value = (mock_transcript, "en")

        result = runner.invoke(
            app,
            [
                "video",
                "fetch",
                video_id,
                "--library",
                str(library_path),
                "--categories",
                "Education",
                "--tags",
                "tutorial",
            ],
        )

        # Should succeed
        assert result.exit_code == 0
        assert "Video added successfully" in result.stdout
        assert "Test Video" in result.stdout
        assert "Test Channel" in result.stdout

        # Verify folder structure was created
        videos_dir = library_path / "videos"
        assert videos_dir.exists()

        # Check that a channel folder was created (exclude _index folder)
        channel_folders = [d for d in videos_dir.iterdir() if d.name != "_index"]
        assert len(channel_folders) == 1

        # Check that video folder was created
        video_folders = list(channel_folders[0].iterdir())
        assert len(video_folders) == 1

        video_folder = video_folders[0]
        assert (video_folder / "source" / "transcript.txt").exists()
        assert (video_folder / "source" / "video.url").exists()
        assert (video_folder / "manifest.yaml").exists()

        # Verify transcript content
        transcript_content = (video_folder / "source" / "transcript.txt").read_text()
        assert transcript_content == mock_transcript

        # Verify API calls were made
        MockAPI.assert_called_once()
        mock_api_instance.fetch_single_video.assert_called_once_with(video_id)
        MockTranscript.fetch_transcript.assert_called_once_with(video_id)
