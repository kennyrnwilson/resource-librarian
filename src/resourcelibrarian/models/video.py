"""Video models for Resource Librarian."""

from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Union

from pydantic import BaseModel, Field


class VideoManifest(BaseModel):
    """Manifest file for a YouTube video source.

    Stores metadata and file paths for a video in the library.
    Serialized to/from YAML in the video's manifest.yaml file.
    """

    videoId: str
    title: str
    description: str = ""
    url: Optional[str] = None  # YouTube video URL

    # Thumbnails - YouTube returns dict with 'url', 'width', 'height' for each size
    # We accept both formats: dict[str, dict] from API or dict[str, str] (just URLs)
    thumbnails: dict[str, Union[str, dict]] = Field(default_factory=dict)

    # Channel info
    channelId: str
    channelTitle: str

    # Metadata
    tags: list[str] = Field(default_factory=list)
    categories: list[str] = Field(default_factory=list)  # User-defined categories
    categoryId: Optional[str] = None
    publishedAt: Optional[datetime] = None
    defaultLanguage: Optional[str] = "en"
    defaultAudioLanguage: Optional[str] = "en"

    # Source paths (relative to video folder)
    source: dict[str, str] = Field(default_factory=dict)
    summaries: dict[str, str] = Field(default_factory=dict)
    pointers: dict[str, str] = Field(default_factory=dict)

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat() if v else None}}

    def to_yaml_dict(self) -> dict[str, Any]:
        """Convert to YAML-serializable dictionary.

        Returns:
            Dictionary suitable for YAML serialization
        """
        return {
            "videoId": self.videoId,
            "title": self.title,
            "description": self.description,
            "url": self.url,
            "thumbnails": self.thumbnails,
            "channelId": self.channelId,
            "channelTitle": self.channelTitle,
            "tags": self.tags,
            "categories": self.categories,
            "categoryId": self.categoryId,
            "publishedAt": self.publishedAt.isoformat() if self.publishedAt else None,
            "defaultLanguage": self.defaultLanguage,
            "defaultAudioLanguage": self.defaultAudioLanguage,
            "source": self.source,
            "summaries": self.summaries,
            "pointers": self.pointers,
        }


class Video(BaseModel):
    """Represents a YouTube video in the resource library.

    Combines the video's folder path with its manifest data,
    providing convenience methods for accessing video files.
    """

    folder_path: Path
    manifest: VideoManifest

    model_config = {"arbitrary_types_allowed": True}

    @property
    def video_id(self) -> str:
        """YouTube video ID from manifest."""
        return self.manifest.videoId

    @property
    def title(self) -> str:
        """Video title from manifest."""
        return self.manifest.title

    @property
    def channel_id(self) -> str:
        """YouTube channel ID from manifest."""
        return self.manifest.channelId

    @property
    def channel_title(self) -> str:
        """Channel title from manifest."""
        return self.manifest.channelTitle

    @property
    def tags(self) -> list[str]:
        """Video tags from manifest."""
        return self.manifest.tags

    @property
    def published_at(self) -> Optional[datetime]:
        """Publication date from manifest."""
        return self.manifest.publishedAt

    def get_transcript_path(self) -> Optional[Path]:
        """Get absolute path to the transcript file.

        Returns:
            Absolute path to transcript, or None if not found
        """
        if "transcript_path" in self.manifest.source:
            rel_path = self.manifest.source["transcript_path"]
            return self.folder_path / rel_path
        return None

    def get_url_path(self) -> Optional[Path]:
        """Get absolute path to the video URL file.

        Returns:
            Absolute path to URL file, or None if not found
        """
        if "url_file" in self.manifest.source:
            rel_path = self.manifest.source["url_file"]
            return self.folder_path / rel_path
        return None

    def get_summary_path(self, summary_type: str) -> Optional[Path]:
        """Get absolute path to a specific summary file.

        Args:
            summary_type: Summary type (e.g., 'shortform', 'ai_claude_sonnet_4_5')

        Returns:
            Absolute path to the summary file, or None if not found
        """
        if summary_type in self.manifest.summaries:
            rel_path = self.manifest.summaries[summary_type]
            return self.folder_path / rel_path
        return None

    def list_summaries(self) -> list[str]:
        """List available summary types.

        Returns:
            List of summary type names
        """
        return list(self.manifest.summaries.keys())

    @classmethod
    def from_folder(cls, folder_path: Path) -> "Video":
        """Load a video from its folder.

        Args:
            folder_path: Path to video folder containing manifest.yaml

        Returns:
            Video instance

        Raises:
            FileNotFoundError: If folder or manifest doesn't exist
        """
        # Import here to avoid circular dependency
        from resourcelibrarian.utils.io import load_video_manifest

        if not folder_path.exists():
            raise FileNotFoundError(f"Video folder not found: {folder_path}")

        manifest = load_video_manifest(folder_path)
        return cls(folder_path=folder_path, manifest=manifest)
