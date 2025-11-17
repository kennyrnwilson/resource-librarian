# Resource Librarian

A library to help create, maintain and index a library of digital resources such as electronic books and youtube video transcripts. By organising resources in these forms and in this manner we make the information amenable to processing by modern generative AI systems.

## Features

### Resource Ingestion - Multiple Content Types

**Books:**
- Supports PDF, EPUB, and Markdown formats
- Auto-extracts metadata (title, author, ISBN)
- Automatically splits into chapters (from EPUB structure)
- Preserves all original formats
- Organizes by author and title with normalized naming

**Videos:**
- YouTube videos and channels
- Downloads transcripts automatically
- Captures video metadata (title, channel, publish date, tags)
- Organizes by channel
- Resumable batch processing for large collections

### Library Organization

- **Filesystem-first architecture** - No database required
- **YAML manifests** - Each resource has structured metadata
- **Searchable catalog** - JSON-based catalog for quick lookups
- **Generated indices** - Markdown index pages by author, title, channel

### Library Catalog & Metadata Queries

Browse your library like a traditional catalog:

- **List all books** - Filter by author, category, or tags
- **View available formats** - PDF, EPUB, Markdown, chapters
- **Retrieve content** - Full books or specific chapters
- **Access summaries** - View existing summaries for any resource
- **Master indices** - Library-wide navigation via `books/_index/authors.md` and `books/_index/titles.md`
- **Individual book indices** - Each book gets a beautiful `index.md` file for easy navigation 

## Installation

```bash
# Clone the repository
git clone git@github.com:kennyrnwilson/resource-librarian.git
cd resource-librarian

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install package with dev dependencies
pip install -e ".[dev]"
```

## Development

### Running Tests

Run all tests:

```bash
pytest tests/ -v
```

Run tests with coverage report:

```bash
pytest tests/ --cov=src/resourcelibrarian --cov-report=term-missing
```

This will show:
- Overall coverage percentage
- Line-by-line coverage for each module
- Missing lines that aren't covered by tests

### Writing Tests

**Unit Tests:** Test individual classes and functions in isolation
- Example: `tests/test_library.py` tests the `ResourceLibrary` class

**CLI Integration Tests:** Test CLI commands using Typer's testing utilities
- Example: `tests/test_cli_init.py` tests the `rl init` command
- Uses `typer.testing.CliRunner` to invoke commands without subprocess calls
- Documentation: https://typer.tiangolo.com/tutorial/testing/

### Code Quality

This project uses [Ruff](https://github.com/astral-sh/ruff) for linting and formatting:

```bash
# Lint code
ruff check .

# Format code
ruff format .
```

## Usage

### Initialize a New Library

Create a new resource library in a directory:

```bash
# Initialize a new library
rl init /path/to/my-library
```

This creates the following directory structure:

```
my-library/
├── .metadata/
│   ├── catalog.json                # Searchable catalog
│   └── video_processing_state.json # Video processing state tracker
├── books/
│   └── _index/
│       ├── authors.md              # Index of all books by author
│       └── titles.md               # Index of all books by title
└── videos/
    └── _index/
        └── channels.md             # Index of all videos by channel
```

### Command-Line Reference

See available commands:

```bash
rl --help
```

**Note:** More commands will be available as development continues. See [docs/CLI_COMMANDS_ANALYSIS.md](docs/CLI_COMMANDS_ANALYSIS.md) for the full command roadmap.

## License

TBD

## Author

Kenny Wilson
