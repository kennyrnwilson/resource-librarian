"""YouTube API wrapper for fetching video metadata."""

import os
from typing import Optional

from googleapiclient.discovery import build


class YouTubeAPIError(Exception):
    """YouTube API related errors."""

    pass


class YouTubeAPI:
    """YouTube API wrapper for fetching video metadata."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize YouTube API client.

        Args:
            api_key: YouTube API key (defaults to YOUTUBE_API_KEY env variable)

        Raises:
            YouTubeAPIError: If API key is not provided
        """
        self.api_key = api_key or os.getenv("YOUTUBE_API_KEY")
        if not self.api_key:
            raise YouTubeAPIError(
                "YouTube API key required. Set YOUTUBE_API_KEY environment variable "
                "or provide api_key parameter."
            )

        self.youtube = build("youtube", "v3", developerKey=self.api_key)

    def fetch_single_video(self, video_id: str) -> dict:
        """Fetch metadata for a single video.

        Args:
            video_id: YouTube video ID

        Returns:
            Video metadata dictionary

        Raises:
            YouTubeAPIError: If video not found or API error
        """
        try:
            response = self.youtube.videos().list(
                part="snippet,contentDetails", id=video_id
            ).execute()

            if not response.get("items"):
                raise YouTubeAPIError(f"Video not found: {video_id}")

            item = response["items"][0]
            snippet = item["snippet"]

            return {
                "videoId": item["id"],
                "title": snippet["title"],
                "description": snippet.get("description", ""),
                "thumbnails": snippet.get("thumbnails", {}),
                "channelId": snippet["channelId"],
                "channelTitle": snippet["channelTitle"],
                "tags": snippet.get("tags", []),
                "categoryId": snippet.get("categoryId", ""),
                "publishedAt": snippet["publishedAt"],
                "defaultLanguage": snippet.get("defaultLanguage", ""),
                "defaultAudioLanguage": snippet.get("defaultAudioLanguage", ""),
            }

        except Exception as e:
            raise YouTubeAPIError(f"Failed to fetch video {video_id}: {e}")
