"""Core ResourceLibrary class for managing a digital library."""

from pathlib import Path
import json


class ResourceLibrary:
    """Main class for managing a Resource Library.

    A Resource Library is a filesystem-based digital library containing:
    - Books (PDF, EPUB, Markdown) organized by author/title
    - YouTube video transcripts organized by channel
    - YAML manifests for metadata
    - JSON catalog for searching
    - Master indices for navigation

    The library structure:
        library_root/
        ├── .metadata/
        │   ├── catalog.json
        │   └── video_processing_state.json
        ├── books/
        │   ├── _index/
        │   │   ├── authors.md
        │   │   └── titles.md
        │   └── [author]/[book-title]/
        │       ├── manifest.yaml
        │       ├── index.md
        │       ├── full-book-formats/
        │       └── summaries/
        └── videos/
            ├── _index/
            │   └── channels.md
            └── [channel__id]/[videoid__title]/
                ├── manifest.yaml
                └── source/transcript.txt
    """

    METADATA_DIR = ".metadata"
    CATALOG_FILE = "catalog.json"
    VIDEO_STATE_FILE = "video_processing_state.json"

    def __init__(self, root_path: Path | str):
        """Initialize a ResourceLibrary instance.

        Args:
            root_path: Path to the library root directory
        """
        self.root = Path(root_path).resolve()
        self.metadata_dir = self.root / self.METADATA_DIR
        self.catalog_path = self.metadata_dir / self.CATALOG_FILE
        self.video_state_path = self.metadata_dir / self.VIDEO_STATE_FILE
        self.books_dir = self.root / "books"
        self.videos_dir = self.root / "videos"

    @classmethod
    def initialize(cls, root_path: Path | str) -> "ResourceLibrary":
        """Initialize a new Resource Library at the specified path.

        Creates the complete directory structure and initial files.

        Args:
            root_path: Path where the library should be created

        Returns:
            ResourceLibrary instance for the newly created library

        Raises:
            FileExistsError: If the directory already exists
        """
        root = Path(root_path).resolve()

        # Check if directory exists
        if root.exists():
            raise FileExistsError(
                f"Directory already exists: {root}\n"
                f"Cannot initialize a library in an existing directory."
            )

        # Create root directory
        root.mkdir(parents=True, exist_ok=False)

        # Create metadata directory and files
        metadata_dir = root / cls.METADATA_DIR
        metadata_dir.mkdir()

        # Create empty catalog
        catalog_path = metadata_dir / cls.CATALOG_FILE
        empty_catalog = {
            "version": "1.0",
            "books": [],
            "videos": [],
            "last_updated": None
        }
        catalog_path.write_text(json.dumps(empty_catalog, indent=2))

        # Create empty video processing state
        video_state_path = metadata_dir / cls.VIDEO_STATE_FILE
        empty_state = {
            "processed": [],
            "failed": [],
            "pending": []
        }
        video_state_path.write_text(json.dumps(empty_state, indent=2))

        # Create books directory structure
        books_dir = root / "books"
        books_dir.mkdir()
        books_index_dir = books_dir / "_index"
        books_index_dir.mkdir()
        (books_index_dir / "authors.md").write_text("# Authors Index\n\n")
        (books_index_dir / "titles.md").write_text("# Titles Index\n\n")

        # Create videos directory structure
        videos_dir = root / "videos"
        videos_dir.mkdir()
        videos_index_dir = videos_dir / "_index"
        videos_index_dir.mkdir()
        (videos_index_dir / "channels.md").write_text("# Channels Index\n\n")

        return cls(root)

    def exists(self) -> bool:
        """Check if this appears to be a valid Resource Library.

        Returns:
            True if the library structure exists, False otherwise
        """
        return (
            self.root.exists()
            and self.metadata_dir.exists()
            and self.catalog_path.exists()
            and self.books_dir.exists()
            and self.videos_dir.exists()
        )

    def __str__(self) -> str:
        """String representation of the library."""
        return f"ResourceLibrary({self.root})"

    def __repr__(self) -> str:
        """Developer representation of the library."""
        return f"ResourceLibrary(root_path={self.root!r})"
