"""Entry point for Resource Librarian CLI.

This module is invoked when running:
    - rl (after installation)
    - python -m resourcelibrarian
"""

from resourcelibrarian.cli.commands import app


def main():
    """Main entry point for the rl command."""
    app()


if __name__ == "__main__":
    main()
