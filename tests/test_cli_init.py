"""CLI integration tests for the init command.

Uses Typer's testing utilities to test CLI commands without subprocess calls.

IMPORTANT: Typer behavior with single vs multiple commands
- When there's only ONE command, Typer promotes it to the top level
  Example: `rl /path/to/library` (no "init" needed)
- When there are MULTIPLE commands, you must specify the subcommand
  Example: `rl init /path/to/library` (with "init")

These tests use BOTH forms to ensure compatibility:
- Current: Works with single command (Phase 0)
- Future: Will work when we add more commands (Phase 1+)

Documentation:
- Typer Testing: https://typer.tiangolo.com/tutorial/testing/
- CliRunner: https://typer.tiangolo.com/tutorial/testing/#the-clirunner
"""

import yaml
from typer.testing import CliRunner
from resourcelibrarian.cli.commands import app

runner = CliRunner()


# Helper function to test both command forms
def invoke_init(path: str) -> tuple:
    """Test init command in both forms (current single-command and future multi-command).

    Returns: (result_without_subcommand, result_with_subcommand)
    """
    # Current form (init is the only command, promoted to top level)
    result_direct = runner.invoke(app, [path])

    # Future form (when we have multiple commands, need explicit "init")
    # This will fail now but will work later
    result_explicit = runner.invoke(app, ["init", path])

    return result_direct, result_explicit


def test_init_command_creates_library(tmp_path):
    """Test that 'rl init' creates a complete library structure."""
    library_path = tmp_path / "test-library"

    # Use explicit 'init' subcommand (now that we have multiple commands)
    result = runner.invoke(app, ["init", str(library_path)])

    # Command should succeed
    assert result.exit_code == 0

    # Should show success message
    assert "Resource Library initialized successfully" in result.stdout
    assert str(library_path) in result.stdout

    # Verify directory structure exists
    assert (library_path / "_index").exists()  # Library-wide index
    assert (library_path / "books").exists()
    assert (library_path / "books" / "_index").exists()
    assert (library_path / "videos").exists()
    assert (library_path / "videos" / "_index").exists()


def test_init_command_creates_catalog_file(tmp_path):
    """Test that 'rl init' creates catalog.yaml."""
    library_path = tmp_path / "test-library"

    result = runner.invoke(app, ["init", str(library_path)])

    assert result.exit_code == 0

    catalog_file = library_path / "catalog.yaml"
    assert catalog_file.exists()

    # Verify catalog structure
    catalog_data = yaml.safe_load(catalog_file.read_text())
    assert catalog_data["version"] == "1.0"
    assert catalog_data["books"] == []
    assert catalog_data["videos"] == []


def test_init_command_creates_index_files(tmp_path):
    """Test that 'rl init' creates index markdown files."""
    library_path = tmp_path / "test-library"

    result = runner.invoke(app, ["init", str(library_path)])

    assert result.exit_code == 0

    # Library-wide index
    assert (library_path / "_index" / "README.md").exists()

    # Books indices
    assert (library_path / "books" / "_index" / "authors.md").exists()
    assert (library_path / "books" / "_index" / "titles.md").exists()

    # Videos indices
    assert (library_path / "videos" / "_index" / "channels.md").exists()


def test_init_command_fails_if_directory_exists(tmp_path):
    """Test that 'rl init' fails gracefully if directory exists."""
    library_path = tmp_path / "test-library"
    library_path.mkdir()  # Create directory first

    result = runner.invoke(app, ["init", str(library_path)])

    # Command should fail with exit code 1
    assert result.exit_code == 1

    # Should show error message
    assert "Initialization Failed" in result.stdout
    assert "already exists" in result.stdout


def test_init_command_shows_next_steps(tmp_path):
    """Test that 'rl init' shows helpful next steps."""
    library_path = tmp_path / "test-library"

    result = runner.invoke(app, ["init", str(library_path)])

    assert result.exit_code == 0

    # Should show next steps
    assert "Next steps:" in result.stdout
    assert "rl book add" in result.stdout
    assert "rl video fetch" in result.stdout
    assert "rl catalog rebuild" in result.stdout


def test_init_command_output_formatting(tmp_path):
    """Test that 'rl init' uses Rich formatting."""
    library_path = tmp_path / "test-library"

    result = runner.invoke(app, ["init", str(library_path)])

    assert result.exit_code == 0

    # Should mention directory structure
    assert "_index/" in result.stdout
    assert "books/" in result.stdout
    assert "videos/" in result.stdout


def test_init_command_with_nested_path(tmp_path):
    """Test that 'rl init' can create nested directory paths."""
    library_path = tmp_path / "parent" / "child" / "library"

    result = runner.invoke(app, ["init", str(library_path)])

    assert result.exit_code == 0

    # Should create parent directories
    assert library_path.exists()
    assert (library_path / "_index").exists()


def test_init_command_with_relative_path(tmp_path):
    """Test that 'rl init' handles relative paths."""
    # Note: This test runs from the project root, so we use tmp_path
    # to ensure we're testing in a clean environment
    library_name = "relative-library"
    library_path = tmp_path / library_name

    # Change to tmp_path to test relative paths
    import os

    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        result = runner.invoke(app, ["init", library_name])

        assert result.exit_code == 0
        assert library_path.exists()
        assert (library_path / "_index").exists()
    finally:
        os.chdir(original_cwd)
