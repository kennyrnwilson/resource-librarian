"""Core ResourceLibrary class for managing a digital library."""

from pathlib import Path

from resourcelibrarian.models.catalog import LibraryCatalog


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

    def __init__(self, root_path: Path | str):
        """Initialize a ResourceLibrary instance.

        Args:
            root_path: Path to the library root directory
        """
        self.root = Path(root_path).resolve()
        self.catalog_path = self.root / "catalog.yaml"
        self.books_dir = self.root / "books"
        self.videos_dir = self.root / "videos"
        self.index_dir = self.root / "_index"

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

        # Create empty catalog as YAML (using catalog manager)
        from resourcelibrarian.core.catalog_manager import CatalogManager
        from resourcelibrarian.models.catalog import LibraryCatalog

        empty_catalog = LibraryCatalog(books=[], videos=[], library_path=root, last_updated=None)
        catalog_mgr = CatalogManager(root)
        catalog_mgr.save_catalog(empty_catalog)

        # Create library-wide index directory
        library_index_dir = root / "_index"
        library_index_dir.mkdir()
        (library_index_dir / "README.md").write_text("# Library Index\n\n")

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

    def load_catalog(self) -> LibraryCatalog:
        """Load the library catalog from disk.

        Returns:
            LibraryCatalog instance with all books and videos

        Raises:
            FileNotFoundError: If catalog file doesn't exist
        """
        from resourcelibrarian.core.catalog_manager import CatalogManager

        catalog_mgr = CatalogManager(self.root)
        return catalog_mgr.load_catalog()
