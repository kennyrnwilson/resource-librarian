"""YouTube transcript fetching utilities."""

from typing import Optional, Tuple

from youtube_transcript_api import YouTubeTranscriptApi


class TranscriptNotAvailableError(Exception):
    """Transcript is not available for this video."""

    pass


class YouTubeTranscript:
    """YouTube transcript fetcher (no API key needed)."""

    @staticmethod
    def fetch_transcript(video_id: str, language: str = "en") -> Tuple[str, Optional[str]]:
        """Fetch transcript for a YouTube video.

        Args:
            video_id: YouTube video ID
            language: Preferred language code (default: 'en')

        Returns:
            Tuple of (transcript_text, actual_language_used)

        Raises:
            TranscriptNotAvailableError: If no transcript available
        """
        try:
            # Initialize the API
            api = YouTubeTranscriptApi()

            # Try requested language first
            transcript_list = api.list(video_id)

            # Try to find requested language
            try:
                transcript = transcript_list.find_transcript([language])
                transcript_data = transcript.fetch()
                text = YouTubeTranscript._format_transcript(transcript_data)
                return text, language
            except:
                pass

            # Try English as fallback
            if language != "en":
                try:
                    transcript = transcript_list.find_transcript(["en"])
                    transcript_data = transcript.fetch()
                    text = YouTubeTranscript._format_transcript(transcript_data)
                    return text, "en"
                except:
                    pass

            # Try any available transcript (including generated)
            try:
                transcript = transcript_list.find_generated_transcript(["en"])
                transcript_data = transcript.fetch()
                text = YouTubeTranscript._format_transcript(transcript_data)
                return text, "en (generated)"
            except:
                pass

            # Last resort: get first available
            for transcript in transcript_list:
                try:
                    transcript_data = transcript.fetch()
                    text = YouTubeTranscript._format_transcript(transcript_data)
                    return text, transcript.language_code
                except:
                    continue

            raise TranscriptNotAvailableError(f"No transcript available for video {video_id}")

        except Exception as e:
            if isinstance(e, TranscriptNotAvailableError):
                raise
            raise TranscriptNotAvailableError(f"Failed to fetch transcript: {e}")

    @staticmethod
    def _format_transcript(transcript_data: list) -> str:
        """Format transcript data into plain text.

        Args:
            transcript_data: List of transcript entries (FetchedTranscriptSnippet objects)

        Returns:
            Formatted transcript text
        """
        text_parts = []
        for entry in transcript_data:
            # Handle both dict and object formats
            if hasattr(entry, 'text'):
                text_parts.append(entry.text.strip())
            elif isinstance(entry, dict) and 'text' in entry:
                text_parts.append(entry['text'].strip())
        return " ".join(text_parts)
