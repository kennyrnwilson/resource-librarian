"""Video ingestion - add YouTube videos to the resource library."""

import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from resourcelibrarian.models import Video, VideoManifest
from resourcelibrarian.utils.io import save_video_manifest
from resourcelibrarian.sources.youtube_api import YouTubeAPI
from resourcelibrarian.sources.youtube_transcript import (
    TranscriptNotAvailableError,
    YouTubeTranscript,
)


def slugify(text: str) -> str:
    """Convert text to a URL-safe slug.

    Args:
        text: Text to slugify

    Returns:
        Slugified text
    """
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-")


def extract_video_id(url_or_id: str) -> str | None:
    """Extract video ID from various YouTube URL formats.

    Args:
        url_or_id: YouTube URL or video ID

    Returns:
        Video ID or None if not found
    """
    # Handle different YouTube URL formats
    patterns = [
        r"(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})",
        r"youtube\.com\/.*[?&]v=([a-zA-Z0-9_-]{11})",
    ]

    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)

    # If it's already just a video ID
    if re.match(r"^[a-zA-Z0-9_-]{11}$", url_or_id):
        return url_or_id

    return None


def create_video_folder_name(video_id: str, title: str) -> str:
    """Create folder name for a video.

    Args:
        video_id: YouTube video ID
        title: Video title

    Returns:
        Folder name in format: videoId__title-slug
    """
    title_slug = slugify(title)
    # Limit title slug length
    if len(title_slug) > 50:
        title_slug = title_slug[:50]
    return f"{video_id}__{title_slug}"


def create_channel_folder_name(channel_id: str, channel_title: str) -> str:
    """Create folder name for a channel.

    Args:
        channel_id: YouTube channel ID
        channel_title: Channel title

    Returns:
        Folder name in format: channel-slug__channelId
    """
    channel_slug = slugify(channel_title)
    # Limit channel slug length
    if len(channel_slug) > 50:
        channel_slug = channel_slug[:50]
    return f"{channel_slug}__{channel_id}"


class VideoIngestion:
    """Handle YouTube video ingestion into the resource library."""

    def __init__(self, library_path: Path):
        """Initialize video ingestion.

        Args:
            library_path: Path to library root
        """
        self.library_path = Path(library_path)
        self.videos_dir = self.library_path / "videos"

    def add_single_video(
        self,
        video_id_or_url: str,
        api_key: Optional[str] = None,
        tags: Optional[list[str]] = None,
        categories: Optional[list[str]] = None,
    ) -> Video:
        """Add a single video to the library.

        Args:
            video_id_or_url: YouTube video ID or URL
            api_key: YouTube API key (optional, uses env var if not provided)
            tags: Additional tags for the video
            categories: User-defined categories for the video

        Returns:
            Video instance

        Raises:
            ValueError: If video ID invalid or transcript not available
        """
        # Extract video ID
        video_id = extract_video_id(video_id_or_url)
        if not video_id:
            raise ValueError(f"Invalid YouTube video ID or URL: {video_id_or_url}")

        # Check if already exists
        # (simplified check - in production we'd check all channel folders)

        # Fetch metadata
        api = YouTubeAPI(api_key)
        video_metadata = api.fetch_single_video(video_id)

        # Fetch transcript
        try:
            transcript_text, language = YouTubeTranscript.fetch_transcript(video_id)
        except TranscriptNotAvailableError as e:
            raise ValueError(f"No transcript available: {e}")

        # Create folder structure
        channel_folder_name = create_channel_folder_name(
            video_metadata["channelId"], video_metadata["channelTitle"]
        )
        video_folder_name = create_video_folder_name(video_id, video_metadata["title"])

        channel_folder = self.videos_dir / channel_folder_name
        video_folder = channel_folder / video_folder_name

        if video_folder.exists():
            raise ValueError(
                f"Video folder already exists: {channel_folder_name}/{video_folder_name}"
            )

        # Create directories
        video_folder.mkdir(parents=True, exist_ok=True)
        (video_folder / "source").mkdir(exist_ok=True)
        (video_folder / "summaries").mkdir(exist_ok=True)
        (video_folder / "pointers").mkdir(exist_ok=True)

        # Save transcript
        transcript_path = video_folder / "source" / "transcript.txt"
        transcript_path.write_text(transcript_text, encoding="utf-8")

        # Save video URL
        url = f"https://www.youtube.com/watch?v={video_id}"
        url_path = video_folder / "source" / "video.url"
        url_path.write_text(url, encoding="utf-8")

        # Parse publishedAt if present
        published_at = None
        if "publishedAt" in video_metadata:
            published_str = video_metadata.get("publishedAt")
            if published_str:
                try:
                    published_at = datetime.fromisoformat(published_str.replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    pass

        # Create manifest
        manifest = VideoManifest(
            videoId=video_id,
            title=video_metadata["title"],
            description=video_metadata.get("description", ""),
            url=url,
            thumbnails=video_metadata.get("thumbnails", {}),
            channelId=video_metadata["channelId"],
            channelTitle=video_metadata["channelTitle"],
            tags=video_metadata.get("tags", []) + (tags or []),
            categories=categories or [],
            categoryId=video_metadata.get("categoryId"),
            publishedAt=published_at,
            defaultLanguage=video_metadata.get("defaultLanguage"),
            defaultAudioLanguage=video_metadata.get("defaultAudioLanguage"),
            source={
                "transcript_path": "source/transcript.txt",
                "url_file": "source/video.url",
            },
            summaries={},
            pointers={},
        )

        # Save manifest
        save_video_manifest(manifest, video_folder)

        # Create Video instance
        video = Video(folder_path=video_folder, manifest=manifest)

        return video

    def add_video(
        self,
        video_metadata: dict,
        transcript_text: str,
        categories: list[str] | None = None,
        tags: list[str] | None = None,
    ) -> Video:
        """Add a video to the library.

        Args:
            video_metadata: Video metadata from MCP YouTube tool
            transcript_text: Video transcript text
            categories: User-defined categories
            tags: Additional tags

        Returns:
            Video instance

        Raises:
            ValueError: If video already exists or required fields missing
        """
        # Extract required fields from metadata
        video_id = video_metadata.get("videoId") or video_metadata.get("video_id")
        title = video_metadata.get("title")
        channel_id = video_metadata.get("channelId") or video_metadata.get("channel_id")
        channel_title = video_metadata.get("channelTitle") or video_metadata.get("channel_title")

        if not all([video_id, title, channel_id, channel_title]):
            raise ValueError("Missing required video metadata fields")

        # Create folder structure
        channel_folder_name = create_channel_folder_name(channel_id, channel_title)
        video_folder_name = create_video_folder_name(video_id, title)

        channel_folder = self.videos_dir / channel_folder_name
        video_folder = channel_folder / video_folder_name

        if video_folder.exists():
            raise ValueError(f"Video already exists: {channel_folder_name}/{video_folder_name}")

        # Create directories
        video_folder.mkdir(parents=True, exist_ok=True)
        (video_folder / "source").mkdir(exist_ok=True)
        (video_folder / "summaries").mkdir(exist_ok=True)
        (video_folder / "pointers").mkdir(exist_ok=True)

        # Save transcript
        transcript_path = video_folder / "source" / "transcript.txt"
        transcript_path.write_text(transcript_text, encoding="utf-8")

        # Save video URL
        url = f"https://www.youtube.com/watch?v={video_id}"
        url_path = video_folder / "source" / "video.url"
        url_path.write_text(url, encoding="utf-8")

        # Parse publishedAt if present
        published_at = None
        if "publishedAt" in video_metadata or "published_at" in video_metadata:
            published_str = video_metadata.get("publishedAt") or video_metadata.get("published_at")
            if published_str:
                try:
                    published_at = datetime.fromisoformat(published_str.replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    pass

        # Create manifest
        manifest = VideoManifest(
            videoId=video_id,
            title=title,
            description=video_metadata.get("description", ""),
            url=url,
            thumbnails=video_metadata.get("thumbnails", {}),
            channelId=channel_id,
            channelTitle=channel_title,
            tags=video_metadata.get("tags", []) + (tags or []),
            categories=categories or [],
            categoryId=video_metadata.get("categoryId"),
            publishedAt=published_at,
            defaultLanguage=video_metadata.get("defaultLanguage"),
            defaultAudioLanguage=video_metadata.get("defaultAudioLanguage"),
            source={
                "transcript_path": "source/transcript.txt",
                "url_file": "source/video.url",
            },
            summaries={},
            pointers={},
        )

        # Save manifest
        save_video_manifest(manifest, video_folder)

        # Create Video instance
        video = Video(folder_path=video_folder, manifest=manifest)

        return video
