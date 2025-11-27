# Development Guide

> **[← Back to Main README](../README.md)** | **[Implementation Plan](IMPLEMENTATION_PLAN.md)** | **[CLI Commands](CLI_COMMANDS_ANALYSIS.md)**

This guide covers everything you need to know to contribute to Resource Librarian.

## Table of Contents

- [Project Setup](#project-setup)
- [Running Tests](#running-tests)
- [Code Quality](#code-quality)
- [Project Structure](#project-structure)
- [Writing Tests](#writing-tests)
- [Contributing](#contributing)

## Project Setup

### Prerequisites

- Python 3.11 or higher
- Git
- Virtual environment (venv)

### Development Installation

1. **Clone the repository:**

```bash
git clone git@github.com:kennyrnwilson/resource-librarian.git
cd resource-librarian
```

2. **Create and activate virtual environment:**

```bash
# Create venv
python -m venv venv

# Activate on Linux/macOS
source venv/bin/activate

# Activate on Windows PowerShell
.\venv\Scripts\Activate.ps1

# Activate on Windows CMD
.\venv\Scripts\activate.bat
```

3. **Install in editable mode with dev dependencies:**

```bash
pip install -e ".[dev]"
```

This installs:
- The `resourcelibrarian` package in editable mode
- All runtime dependencies
- Development tools (pytest, ruff, coverage)

## Running Tests

### Run All Tests

```bash
pytest tests/ -v
```

Output example:
```
tests/test_library.py::test_initialize_library PASSED
tests/test_models.py::test_book_manifest_creation PASSED
tests/test_cli_init.py::test_cli_init_command PASSED
================================ 143 passed in 2.34s ================================
```

### Run Tests with Coverage

```bash
pytest tests/ --cov=src/resourcelibrarian --cov-report=term-missing
```

This shows:
- Overall coverage percentage
- Coverage per module
- Line-by-line coverage
- Missing lines that aren't covered

Example output:
```
Name                                              Stmts   Miss  Cover   Missing
-------------------------------------------------------------------------------
src/resourcelibrarian/__init__.py                     4      0   100%
src/resourcelibrarian/library.py                     89     12    87%   45-48, 102-105
src/resourcelibrarian/models.py                      67      5    93%   123-127
src/resourcelibrarian/sources/book_parser.py        156     53    66%   25-33, 45-57
-------------------------------------------------------------------------------
TOTAL                                               543    245    55%
```

### Run Specific Test Files

```bash
# Test a specific file
pytest tests/test_library.py -v

# Test a specific test function
pytest tests/test_library.py::test_initialize_library -v

# Test with pattern matching
pytest tests/ -k "test_book" -v
```

### Generate HTML Coverage Report

```bash
pytest tests/ --cov=src/resourcelibrarian --cov-report=html
```

Then open `htmlcov/index.html` in your browser for an interactive coverage report.

## Code Quality

This project uses [Ruff](https://github.com/astral-sh/ruff) for both linting and formatting.

### Linting

Check for code issues:

```bash
# Check all files
ruff check .

# Check specific directory
ruff check src/

# Auto-fix issues where possible
ruff check . --fix
```

### Formatting

Format code to project standards:

```bash
# Check formatting (don't modify files)
ruff format . --check

# Format all files
ruff format .

# Format specific file
ruff format src/resourcelibrarian/library.py
```

### Configuration

Ruff is configured in `pyproject.toml`:

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "W"]
ignore = ["E501"]

[tool.ruff.format]
line-length = 100
```

### Pre-commit Checks

Before committing, run:

```bash
# Format code
ruff format .

# Check linting
ruff check . --fix

# Run tests
pytest tests/ -v
```

## Project Structure

```
resource-librarian/
├── src/
│   └── resourcelibrarian/
│       ├── __init__.py           # Package exports
│       ├── cli.py                # CLI entry points (Typer)
│       ├── library.py            # ResourceLibrary class
│       ├── models.py             # Pydantic data models
│       ├── utils.py              # Shared utilities
│       └── sources/              # Resource ingestion
│           ├── __init__.py
│           ├── book_parser.py    # PDF/EPUB/Markdown parsing
│           ├── book_ingestion.py # Book addition pipeline
│           ├── book_folder_scanner.py
│           └── epub_chapter_extractor.py
│
├── tests/
│   ├── test_library.py           # Library initialization tests
│   ├── test_models.py            # Data model tests
│   ├── test_utils.py             # Utility function tests
│   ├── test_cli_init.py          # CLI command tests
│   └── test_sources_book_parser.py
│
├── docs/
│   ├── DEVELOPMENT.md            # This file
│   ├── IMPLEMENTATION_PLAN.md    # Project roadmap
│   └── CLI_COMMANDS_ANALYSIS.md  # Command specifications
│
├── pyproject.toml                # Project metadata & dependencies
├── README.md                     # User-facing documentation
└── .gitignore
```

### Key Modules

#### `library.py`
- `ResourceLibrary` class - Main library management
- Methods: `initialize()`, `add_book()`, `list_books()`

#### `models.py`
- Pydantic models for data validation
- `BookManifest`, `VideoManifest`, `Book`, `Video`
- `LibraryMetadata`, `Catalog`

#### `cli.py`
- Typer-based CLI commands
- Command groups: `book`, `video`, `init`

#### `sources/book_parser.py`
- Multi-format book parsing
- PDF extraction (PyMuPDF)
- EPUB extraction (ebooklib)
- HTML-to-Markdown conversion
- Metadata extraction

#### `utils.py`
- File I/O helpers
- YAML/JSON reading and writing
- Hash computation

## Writing Tests

### Test Structure

Resource Librarian uses pytest with the following patterns:

#### Unit Tests

Test individual functions and classes in isolation:

```python
# tests/test_library.py
from pathlib import Path
import pytest
from resourcelibrarian.library import ResourceLibrary

def test_initialize_library(tmp_path):
    """Test library initialization creates correct structure."""
    library = ResourceLibrary(tmp_path)
    library.initialize()

    assert (tmp_path / ".metadata" / "catalog.json").exists()
    assert (tmp_path / "books").exists()
    assert (tmp_path / "videos").exists()
```

#### CLI Integration Tests

Test CLI commands using Typer's testing utilities:

```python
# tests/test_cli_init.py
from typer.testing import CliRunner
from resourcelibrarian.cli import app

runner = CliRunner()

def test_cli_init_command(tmp_path):
    """Test the 'rl init' command."""
    library_path = tmp_path / "my-library"

    result = runner.invoke(app, ["init", str(library_path)])

    assert result.exit_code == 0
    assert "Library initialized" in result.stdout
    assert (library_path / ".metadata").exists()
```

**Why use CliRunner:**
- No subprocess overhead
- Direct command invocation
- Easy to test output and exit codes
- Documentation: https://typer.tiangolo.com/tutorial/testing/

#### Test Fixtures

Use pytest fixtures for shared test setup:

```python
import pytest
from pathlib import Path

@pytest.fixture
def library_dir(tmp_path):
    """Create and initialize a test library."""
    library = ResourceLibrary(tmp_path)
    library.initialize()
    return tmp_path

def test_add_book(library_dir):
    """Test adding a book to initialized library."""
    # library_dir is already initialized
    book_path = library_dir / "books" / "test.epub"
    # ... test implementation
```

### Test Coverage Goals

- **Overall:** Aim for 80%+ coverage
- **Core modules:** 90%+ coverage
  - `library.py`
  - `models.py`
  - `utils.py`
- **CLI commands:** 100% coverage of happy paths
- **Parsers:** 70%+ (some features require real files)

### Running Coverage Analysis

```bash
# Check current coverage
pytest tests/ --cov=src/resourcelibrarian --cov-report=term-missing

# Find untested code
pytest tests/ --cov=src/resourcelibrarian --cov-report=term-missing | grep "0%"

# Generate detailed HTML report
pytest tests/ --cov=src/resourcelibrarian --cov-report=html
open htmlcov/index.html
```

## Contributing

### Workflow

1. **Fork the repository**
2. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Write/update tests**
5. **Run quality checks:**
   ```bash
   ruff format .
   ruff check . --fix
   pytest tests/ -v
   ```
6. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```
7. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```
8. **Create a Pull Request**

### Commit Message Convention

Use conventional commit format:

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `test:` Test additions/changes
- `refactor:` Code refactoring
- `chore:` Build/tooling changes

Examples:
```
feat: add EPUB chapter extraction
fix: handle missing ISBN in metadata
docs: update installation instructions
test: add coverage for book parsing
```

### Code Style Guidelines

- **Line length:** 100 characters (enforced by Ruff)
- **Type hints:** Use type hints for function signatures
- **Docstrings:** Use Google-style docstrings
- **Imports:** Organize with Ruff (automatic)

Example function:

```python
def parse_author_name(author: str) -> tuple[str, str]:
    """Parse author name into first and last name.

    Handles various formats:
    - "Camille Fournier" -> ("Camille", "Fournier")
    - "Fournier, Camille" -> ("Camille", "Fournier")
    - "John Smith Jr." -> ("John", "Smith Jr.")

    Args:
        author: Author name in any common format

    Returns:
        Tuple of (firstname, lastname)
    """
    # Implementation...
```

### Testing Your Changes

Before submitting a PR:

1. **All tests pass:**
   ```bash
   pytest tests/ -v
   ```

2. **Coverage doesn't decrease:**
   ```bash
   pytest tests/ --cov=src/resourcelibrarian --cov-report=term
   ```

3. **Code quality passes:**
   ```bash
   ruff check .
   ruff format . --check
   ```

4. **Manual testing:**
   - Install in dev mode: `pip install -e .`
   - Test affected commands: `rl <command>`

## Development Roadmap

See [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for:
- Current phase status
- Upcoming features
- Long-term goals

## Getting Help

- **Issues:** Use GitHub Issues for bugs and feature requests
- **Discussions:** Use GitHub Discussions for questions
- **Email:** Contact Kenny Wilson (see README)

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Typer Documentation](https://typer.tiangolo.com/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
