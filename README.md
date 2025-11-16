# Resource Librarian

A library to help create, maintain and index a digital library of electronic book, youtube transcripts and summaries of them.

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

```bash
pytest tests/ -v
```

### Code Quality

This project uses [Ruff](https://github.com/astral-sh/ruff) for linting and formatting:

```bash
# Lint code
ruff check .

# Format code
ruff format .
```

## Usage

```python
import resourcelibrarian

# Your code here
```

## License

TBD

## Author

Kenny Wilson
