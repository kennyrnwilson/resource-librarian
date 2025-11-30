"""CLI commands for Resource Librarian.

Uses:
- Typer: https://typer.tiangolo.com/ - CLI framework with type hints
- Rich: https://rich.readthedocs.io/ - Beautiful terminal output
"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from resourcelibrarian.library import ResourceLibrary

# Version
__version__ = "0.1.0"


def version_callback(value: bool):
    """Print version and exit."""
    if value:
        typer.echo(f"Resource Librarian (rl) version {__version__}")
        raise typer.Exit()


app = typer.Typer(
    name="rl",
    help="Resource Librarian - Manage your digital library of books and YouTube video transcripts",
    add_completion=False,
)

# Book subcommand group
book_app = typer.Typer(help="Manage books in the library")
app.add_typer(book_app, name="book")

# Video subcommand group
video_app = typer.Typer(help="Manage videos in the library")
app.add_typer(video_app, name="video")

# Catalog subcommand group
catalog_app = typer.Typer(help="Manage library catalog and indices")
app.add_typer(catalog_app, name="catalog")

console = Console()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
):
    """Resource Librarian - Manage your digital library."""
    pass


@app.command()
def init(
    path: str = typer.Argument(
        ...,
        help="Path where the library should be initialized",
    ),
):
    """Initialize a new Resource Library.

    Creates the complete directory structure including:
    - catalog.yaml for library catalog
    - _index/ for library-wide navigation
    - books/ for book storage
    - videos/ for YouTube video transcripts
    - Index files for navigation
    """
    try:
        # Initialize the library
        library = ResourceLibrary.initialize(path)

        # Success message
        console.print()
        console.print(
            Panel.fit(
                f"[green]✓[/green] Resource Library initialized successfully!\n\n"
                f"[bold]Location:[/bold] {library.root}\n\n"
                f"[dim]Directory structure created:[/dim]\n"
                f"  • catalog.yaml (library catalog)\n"
                f"  • _index/ (library-wide navigation)\n"
                f"  • books/ (book storage and indices)\n"
                f"  • videos/ (YouTube transcripts and indices)\n\n"
                f"[bold]Next steps:[/bold]\n"
                f"  • Add books: [cyan]rl book add <file>[/cyan]\n"
                f"  • Fetch videos: [cyan]rl video fetch <url>[/cyan]\n"
                f"  • Rebuild catalog: [cyan]rl catalog rebuild[/cyan]",
                title="[bold green]Library Initialized[/bold green]",
                border_style="green",
            )
        )
        console.print()

    except FileExistsError as e:
        console.print()
        console.print(
            Panel.fit(
                f"[red]✗[/red] {str(e)}\n\n"
                f"[dim]The directory already exists. If you want to initialize a library:\n"
                f"  • Choose a different location, or\n"
                f"  • Remove the existing directory first[/dim]",
                title="[bold red]Initialization Failed[/bold red]",
                border_style="red",
            )
        )
        console.print()
        raise typer.Exit(1)
    except Exception as e:
        console.print()
        console.print(
            Panel.fit(
                f"[red]✗[/red] An unexpected error occurred:\n\n{str(e)}",
                title="[bold red]Error[/bold red]",
                border_style="red",
            )
        )
        console.print()
        raise typer.Exit(1)


@book_app.command("list")
def book_list(
    library_path: str = typer.Option(
        ".",
        "--library",
        "-l",
        help="Path to the library (default: current directory)",
    ),
    author: Optional[str] = typer.Option(
        None,
        "--author",
        "-a",
        help="Filter by author (case-insensitive substring match)",
    ),
    category: Optional[str] = typer.Option(
        None,
        "--category",
        "-c",
        help="Filter by category (case-insensitive substring match)",
    ),
    tag: Optional[str] = typer.Option(
        None,
        "--tag",
        "-t",
        help="Filter by tag (case-insensitive substring match)",
    ),
    title: Optional[str] = typer.Option(
        None,
        "--title",
        help="Filter by title (case-insensitive substring match)",
    ),
):
    """List all books in the library with optional filters.

    Examples:
        rl book list
        rl book list --author "Smith"
        rl book list --category "Programming"
        rl book list --tag "beginner" --author "Jones"
    """
    try:
        # Load library
        library = ResourceLibrary(library_path)
        if not library.exists():
            console.print()
            console.print(
                Panel.fit(
                    f"[red]✗[/red] Not a valid Resource Library: {library.root}\n\n"
                    f"[dim]Initialize a library first:[/dim]\n"
                    f"  [cyan]rl init /path/to/library[/cyan]",
                    title="[bold red]Library Not Found[/bold red]",
                    border_style="red",
                )
            )
            console.print()
            raise typer.Exit(1)

        # Load catalog
        catalog = library.load_catalog()

        # Apply filters
        books = catalog.search_books(author=author, category=category, tag=tag, title=title)

        if not books:
            console.print()
            filter_desc = []
            if author:
                filter_desc.append(f"author: {author}")
            if category:
                filter_desc.append(f"category: {category}")
            if tag:
                filter_desc.append(f"tag: {tag}")
            if title:
                filter_desc.append(f"title: {title}")

            if filter_desc:
                console.print(
                    f"[yellow]No books found matching filters: {', '.join(filter_desc)}[/yellow]"
                )
            else:
                console.print("[yellow]No books in library yet.[/yellow]")
            console.print()
            return

        # Create table
        table = Table(title=f"Books in Library ({len(books)} found)")
        table.add_column("Title", style="cyan", no_wrap=False)
        table.add_column("Author", style="green")
        table.add_column("Categories", style="yellow")
        table.add_column("Formats", style="magenta")

        for book in books:
            categories_str = ", ".join(book.categories) if book.categories else "-"
            formats_str = ", ".join(book.list_formats()) if book.list_formats() else "-"
            table.add_row(book.title, book.author, categories_str, formats_str)

        console.print()
        console.print(table)
        console.print()

    except FileNotFoundError as e:
        console.print()
        console.print(
            Panel.fit(
                f"[red]✗[/red] {str(e)}",
                title="[bold red]Error[/bold red]",
                border_style="red",
            )
        )
        console.print()
        raise typer.Exit(1)
    except Exception as e:
        console.print()
        console.print(
            Panel.fit(
                f"[red]✗[/red] An unexpected error occurred:\n\n{str(e)}",
                title="[bold red]Error[/bold red]",
                border_style="red",
            )
        )
        console.print()
        raise typer.Exit(1)


@book_app.command("add")
def book_add(
    file_path: str = typer.Argument(..., help="Path to book file (PDF, EPUB, or Markdown)"),
    library_path: str = typer.Option(
        ".",
        "--library",
        "-l",
        help="Path to the library (default: current directory)",
    ),
    title: Optional[str] = typer.Option(
        None,
        "--title",
        "-t",
        help="Book title (auto-detected if not provided)",
    ),
    author: Optional[str] = typer.Option(
        None,
        "--author",
        "-a",
        help="Book author (auto-detected if not provided)",
    ),
    categories: Optional[str] = typer.Option(
        None,
        "--categories",
        "-c",
        help="Comma-separated list of categories",
    ),
    tags: Optional[str] = typer.Option(
        None,
        "--tags",
        help="Comma-separated list of tags",
    ),
    isbn: Optional[str] = typer.Option(
        None,
        "--isbn",
        help="ISBN number",
    ),
):
    """Add a book to the library.

    Supports PDF, EPUB, and Markdown formats. Automatically extracts metadata
    from EPUB files and text content. You can override auto-detected values
    with command-line options.

    Examples:
        rl book add book.epub
        rl book add book.pdf --title "Python Programming" --author "John Smith"
        rl book add book.md --categories "Programming,AI" --tags "beginner,tutorial"
    """
    try:
        # Import here to avoid circular dependencies
        from resourcelibrarian.sources.book_ingestion import BookIngestion

        # Validate file exists
        source_file = Path(file_path)
        if not source_file.exists():
            console.print()
            console.print(
                Panel.fit(
                    f"[red]✗[/red] File not found: {file_path}\n\n"
                    f"[dim]Please check the file path and try again.[/dim]",
                    title="[bold red]File Not Found[/bold red]",
                    border_style="red",
                )
            )
            console.print()
            raise typer.Exit(1)

        # Load library
        library = ResourceLibrary(library_path)
        if not library.exists():
            console.print()
            console.print(
                Panel.fit(
                    f"[red]✗[/red] Not a valid Resource Library: {library.root}\n\n"
                    f"[dim]Initialize a library first:[/dim]\n"
                    f"  [cyan]rl init /path/to/library[/cyan]",
                    title="[bold red]Library Not Found[/bold red]",
                    border_style="red",
                )
            )
            console.print()
            raise typer.Exit(1)

        # Parse categories and tags
        category_list = [c.strip() for c in categories.split(",")] if categories else None
        tag_list = [t.strip() for t in tags.split(",")] if tags else None

        # Show processing message
        console.print()
        console.print(f"[cyan]Processing book:[/cyan] {source_file.name}")
        console.print()

        # Add book using ingestion system
        ingestion = BookIngestion(library.root)
        book = ingestion.add_book(
            file_path=source_file,
            title=title,
            author=author,
            categories=category_list,
            tags=tag_list,
            isbn=isbn,
        )

        # Update catalog and regenerate indices
        from resourcelibrarian.core.catalog_manager import CatalogManager
        from resourcelibrarian.core.index_generator import IndexGenerator

        catalog_mgr = CatalogManager(library.root)
        catalog_mgr.add_book(book)

        # Regenerate indices
        catalog = catalog_mgr.load_catalog()
        index_gen = IndexGenerator(library.root)
        index_gen.generate_all_indices(catalog)

        # Success message
        formats_str = ", ".join(book.list_formats())
        console.print(
            Panel.fit(
                f"[green]✓[/green] Book added successfully!\n\n"
                f"[bold]Title:[/bold] {book.title}\n"
                f"[bold]Author:[/bold] {book.author}\n"
                f"[bold]Formats:[/bold] {formats_str}\n"
                f"[bold]Location:[/bold] {book.folder_path.relative_to(library.root)}\n"
                + (
                    f"[bold]Categories:[/bold] {', '.join(book.categories)}\n"
                    if book.categories
                    else ""
                )
                + (f"[bold]Tags:[/bold] {', '.join(book.tags)}\n" if book.tags else "")
                + (f"[bold]ISBN:[/bold] {book.manifest.isbn}\n" if book.manifest.isbn else ""),
                title="[bold green]Book Added[/bold green]",
                border_style="green",
            )
        )
        console.print()

    except FileNotFoundError as e:
        console.print()
        console.print(
            Panel.fit(
                f"[red]✗[/red] {str(e)}",
                title="[bold red]Error[/bold red]",
                border_style="red",
            )
        )
        console.print()
        raise typer.Exit(1)
    except ValueError as e:
        console.print()
        console.print(
            Panel.fit(
                f"[red]✗[/red] {str(e)}\n\n"
                f"[dim]Tips:[/dim]\n"
                f"  • For EPUB files, metadata is auto-detected\n"
                f"  • For PDF/Markdown, use --title and --author options\n"
                f"  • Check that the file is a valid book format",
                title="[bold red]Invalid Book[/bold red]",
                border_style="red",
            )
        )
        console.print()
        raise typer.Exit(1)
    except Exception as e:
        console.print()
        console.print(
            Panel.fit(
                f"[red]✗[/red] An unexpected error occurred:\n\n{str(e)}",
                title="[bold red]Error[/bold red]",
                border_style="red",
            )
        )
        console.print()
        raise typer.Exit(1)


@book_app.command("import-folder")
def book_import_folder(
    folder_path: str = typer.Argument(..., help="Path to structured book folder"),
    library_path: str = typer.Option(
        ".",
        "--library",
        "-l",
        help="Path to the library (default: current directory)",
    ),
    title: Optional[str] = typer.Option(
        None,
        "--title",
        "-t",
        help="Book title (auto-detected if not provided)",
    ),
    author: Optional[str] = typer.Option(
        None,
        "--author",
        "-a",
        help="Book author (auto-detected if not provided)",
    ),
    categories: Optional[str] = typer.Option(
        None,
        "--categories",
        "-c",
        help="Comma-separated list of categories",
    ),
    tags: Optional[str] = typer.Option(
        None,
        "--tags",
        help="Comma-separated list of tags",
    ),
    isbn: Optional[str] = typer.Option(
        None,
        "--isbn",
        help="ISBN number",
    ),
):
    """Import a book from a structured folder.

    This command scans a folder containing book files and summaries organized in a
    specific structure:

    Folder structure:
        my-book/
        ├── my-book.epub           # Main book file (folder-name.ext)
        ├── my-book.pdf            # Alternative format
        ├── my-book-summary-shortform.pdf    # Summary files
        └── my-book-summary-claude.md

    The command will:
    - Auto-detect book formats (PDF, EPUB, Markdown)
    - Auto-detect summary files with naming pattern: folder-name-summary-type.ext
    - Convert summaries to Markdown if needed
    - Extract chapters from EPUB files
    - Auto-detect metadata from EPUB or text content

    Examples:
        rl book import-folder /path/to/my-book-folder
        rl book import-folder ./books/python-programming --categories "Programming,Python"
        rl book import-folder ./deep-learning --title "Deep Learning" --author "Ian Goodfellow"
    """
    try:
        # Import here to avoid circular dependencies
        from resourcelibrarian.sources.book_ingestion import BookIngestion

        # Validate folder exists
        source_folder = Path(folder_path)
        if not source_folder.exists():
            console.print()
            console.print(
                Panel.fit(
                    f"[red]✗[/red] Folder not found: {folder_path}\n\n"
                    f"[dim]Please check the folder path and try again.[/dim]",
                    title="[bold red]Folder Not Found[/bold red]",
                    border_style="red",
                )
            )
            console.print()
            raise typer.Exit(1)

        if not source_folder.is_dir():
            console.print()
            console.print(
                Panel.fit(
                    f"[red]✗[/red] Not a directory: {folder_path}\n\n"
                    f"[dim]Please provide a path to a folder containing book files.[/dim]",
                    title="[bold red]Not a Directory[/bold red]",
                    border_style="red",
                )
            )
            console.print()
            raise typer.Exit(1)

        # Load library
        library = ResourceLibrary(library_path)
        if not library.exists():
            console.print()
            console.print(
                Panel.fit(
                    f"[red]✗[/red] Not a valid Resource Library: {library.root}\n\n"
                    f"[dim]Initialize a library first:[/dim]\n"
                    f"  [cyan]rl init /path/to/library[/cyan]",
                    title="[bold red]Library Not Found[/bold red]",
                    border_style="red",
                )
            )
            console.print()
            raise typer.Exit(1)

        # Parse categories and tags
        category_list = [c.strip() for c in categories.split(",")] if categories else None
        tag_list = [t.strip() for t in tags.split(",")] if tags else None

        # Show processing message
        console.print()
        console.print(f"[cyan]Scanning folder:[/cyan] {source_folder.name}")
        console.print()

        # Import book from folder using ingestion system
        ingestion = BookIngestion(library.root)
        book = ingestion.add_book_from_folder(
            folder_path=source_folder,
            title=title,
            author=author,
            categories=category_list,
            tags=tag_list,
            isbn=isbn,
        )

        # Update catalog and regenerate indices
        from resourcelibrarian.core.catalog_manager import CatalogManager
        from resourcelibrarian.core.index_generator import IndexGenerator

        catalog_mgr = CatalogManager(library.root)
        catalog_mgr.add_book(book)

        # Regenerate indices
        catalog = catalog_mgr.load_catalog()
        index_gen = IndexGenerator(library.root)
        index_gen.generate_all_indices(catalog)

        # Success message
        formats_str = ", ".join(book.list_formats())
        summaries_str = ", ".join(book.list_summaries()) if book.list_summaries() else "None"

        console.print(
            Panel.fit(
                f"[green]✓[/green] Book imported successfully!\n\n"
                f"[bold]Title:[/bold] {book.title}\n"
                f"[bold]Author:[/bold] {book.author}\n"
                f"[bold]Formats:[/bold] {formats_str}\n"
                f"[bold]Summaries:[/bold] {summaries_str}\n"
                f"[bold]Location:[/bold] {book.folder_path.relative_to(library.root)}\n"
                + (
                    f"[bold]Categories:[/bold] {', '.join(book.categories)}\n"
                    if book.categories
                    else ""
                )
                + (f"[bold]Tags:[/bold] {', '.join(book.tags)}\n" if book.tags else "")
                + (f"[bold]ISBN:[/bold] {book.manifest.isbn}\n" if book.manifest.isbn else ""),
                title="[bold green]Book Imported[/bold green]",
                border_style="green",
            )
        )
        console.print()

    except FileNotFoundError as e:
        console.print()
        console.print(
            Panel.fit(
                f"[red]✗[/red] {str(e)}",
                title="[bold red]Error[/bold red]",
                border_style="red",
            )
        )
        console.print()
        raise typer.Exit(1)
    except ValueError as e:
        console.print()
        console.print(
            Panel.fit(
                f"[red]✗[/red] {str(e)}\n\n"
                f"[dim]Tips:[/dim]\n"
                f"  • Ensure the folder contains book files named: folder-name.epub, folder-name.pdf, etc.\n"
                f"  • Summary files should be named: folder-name-summary-type.ext\n"
                f"  • For folders without EPUB metadata, use --title and --author options",
                title="[bold red]Import Failed[/bold red]",
                border_style="red",
            )
        )
        console.print()
        raise typer.Exit(1)
    except Exception as e:
        console.print()
        console.print(
            Panel.fit(
                f"[red]✗[/red] An unexpected error occurred:\n\n{str(e)}",
                title="[bold red]Error[/bold red]",
                border_style="red",
            )
        )
        console.print()
        raise typer.Exit(1)


@book_app.command("get")
def book_get(
    title: str = typer.Argument(..., help="Title of the book to retrieve"),
    library_path: str = typer.Option(
        ".",
        "--library",
        "-l",
        help="Path to the library (default: current directory)",
    ),
    format_type: Optional[str] = typer.Option(
        None,
        "--format",
        "-f",
        help="Format to retrieve (pdf, epub, markdown). Default: markdown if available",
    ),
    output: Optional[str] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path. If not specified, prints to stdout",
    ),
):
    """Retrieve book content by title.

    Examples:
        rl book get "Python Programming"
        rl book get "Python Programming" --format pdf --output book.pdf
        rl book get "Data Science" --format markdown
    """
    try:
        # Load library
        library = ResourceLibrary(library_path)
        if not library.exists():
            console.print()
            console.print(
                Panel.fit(
                    f"[red]✗[/red] Not a valid Resource Library: {library.root}\n\n"
                    f"[dim]Initialize a library first:[/dim]\n"
                    f"  [cyan]rl init /path/to/library[/cyan]",
                    title="[bold red]Library Not Found[/bold red]",
                    border_style="red",
                )
            )
            console.print()
            raise typer.Exit(1)

        # Load catalog
        catalog = library.load_catalog()

        # Find book
        book = catalog.find_book(title)
        if not book:
            console.print()
            console.print(
                Panel.fit(
                    f"[red]✗[/red] Book not found: {title}\n\n"
                    f"[dim]Try:[/dim]\n"
                    f"  [cyan]rl book list[/cyan] - to see all books\n"
                    f'  [cyan]rl book list --title "{title.split()[0]}"[/cyan] - to search for similar titles',
                    title="[bold red]Book Not Found[/bold red]",
                    border_style="red",
                )
            )
            console.print()
            raise typer.Exit(1)

        # Determine format to use
        available_formats = book.list_formats()
        if not available_formats:
            console.print()
            console.print(
                Panel.fit(
                    f"[red]✗[/red] No formats available for: {book.title}",
                    title="[bold red]No Formats[/bold red]",
                    border_style="red",
                )
            )
            console.print()
            raise typer.Exit(1)

        # Select format
        if format_type:
            if format_type not in available_formats:
                console.print()
                console.print(
                    Panel.fit(
                        f"[red]✗[/red] Format '{format_type}' not available for: {book.title}\n\n"
                        f"[dim]Available formats:[/dim] {', '.join(available_formats)}",
                        title="[bold red]Format Not Available[/bold red]",
                        border_style="red",
                    )
                )
                console.print()
                raise typer.Exit(1)
            selected_format = format_type
        else:
            # Default: prefer markdown > epub > pdf
            if "markdown" in available_formats:
                selected_format = "markdown"
            elif "epub" in available_formats:
                selected_format = "epub"
            elif "pdf" in available_formats:
                selected_format = "pdf"
            else:
                selected_format = available_formats[0]

        # Get file path
        file_path = book.get_format_path(selected_format)
        if not file_path or not file_path.exists():
            console.print()
            console.print(
                Panel.fit(
                    f"[red]✗[/red] Format file not found: {file_path}",
                    title="[bold red]File Not Found[/bold red]",
                    border_style="red",
                )
            )
            console.print()
            raise typer.Exit(1)

        # Output to file or stdout
        if output:
            output_path = Path(output)
            output_path.write_bytes(file_path.read_bytes())
            console.print()
            console.print(
                Panel.fit(
                    f"[green]✓[/green] Book content written to: {output_path}\n\n"
                    f"[bold]Book:[/bold] {book.title}\n"
                    f"[bold]Author:[/bold] {book.author}\n"
                    f"[bold]Format:[/bold] {selected_format}\n"
                    f"[bold]Size:[/bold] {output_path.stat().st_size:,} bytes",
                    title="[bold green]Success[/bold green]",
                    border_style="green",
                )
            )
            console.print()
        else:
            # Print to stdout
            if selected_format in ("markdown", "md", "txt"):
                content = file_path.read_text(encoding="utf-8")
                console.print()
                console.print(Panel.fit(f"[bold]{book.title}[/bold]\nby {book.author}"))
                console.print()
                console.print(content)
                console.print()
            else:
                console.print()
                console.print(
                    Panel.fit(
                        f"[yellow]⚠[/yellow] Cannot display {selected_format} format in terminal.\n\n"
                        f"[dim]Use --output option to save to a file:[/dim]\n"
                        f'  [cyan]rl book get "{title}" --format {selected_format} --output book.{selected_format}[/cyan]',
                        title="[bold yellow]Binary Format[/bold yellow]",
                        border_style="yellow",
                    )
                )
                console.print()
                raise typer.Exit(1)

    except FileNotFoundError as e:
        console.print()
        console.print(
            Panel.fit(
                f"[red]✗[/red] {str(e)}",
                title="[bold red]Error[/bold red]",
                border_style="red",
            )
        )
        console.print()
        raise typer.Exit(1)
    except Exception as e:
        console.print()
        console.print(
            Panel.fit(
                f"[red]✗[/red] An unexpected error occurred:\n\n{str(e)}",
                title="[bold red]Error[/bold red]",
                border_style="red",
            )
        )
        console.print()
        raise typer.Exit(1)


@video_app.command("fetch")
def video_fetch(
    video_url: str = typer.Argument(..., help="YouTube video URL or ID"),
    library_path: str = typer.Option(
        ".",
        "--library",
        "-l",
        help="Path to the library (default: current directory)",
    ),
    categories: Optional[str] = typer.Option(
        None,
        "--categories",
        "-c",
        help="Comma-separated list of categories",
    ),
    tags: Optional[str] = typer.Option(
        None,
        "--tags",
        "-t",
        help="Comma-separated list of tags",
    ),
):
    """Fetch a YouTube video and its transcript to add to the library.

    Fetches video metadata and transcript from YouTube and saves them to the library.
    Creates a folder structure: videos/channel__id/videoid__title/

    Examples:
        rl video fetch "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        rl video fetch dQw4w9WgXcQ
        rl video fetch "https://youtu.be/dQw4w9WgXcQ" --categories "Music,Entertainment"
    """
    try:
        # Import here to avoid circular dependencies
        from resourcelibrarian.sources import (
            VideoIngestion,
            extract_video_id,
            YouTubeAPIError,
            TranscriptNotAvailableError,
        )

        # Extract video ID
        video_id = extract_video_id(video_url)
        if not video_id:
            console.print()
            console.print(
                Panel.fit(
                    f"[red]✗[/red] Invalid YouTube video URL or ID: {video_url}\n\n"
                    f"[dim]Valid formats:[/dim]\n"
                    f"  • https://www.youtube.com/watch?v=VIDEO_ID\n"
                    f"  • https://youtu.be/VIDEO_ID\n"
                    f"  • VIDEO_ID (11 characters)",
                    title="[bold red]Invalid URL[/bold red]",
                    border_style="red",
                )
            )
            console.print()
            raise typer.Exit(1)

        # Load library
        library = ResourceLibrary(library_path)
        if not library.exists():
            console.print()
            console.print(
                Panel.fit(
                    f"[red]✗[/red] Not a valid Resource Library: {library.root}\n\n"
                    f"[dim]Initialize a library first:[/dim]\n"
                    f"  [cyan]rl init /path/to/library[/cyan]",
                    title="[bold red]Library Not Found[/bold red]",
                    border_style="red",
                )
            )
            console.print()
            raise typer.Exit(1)

        # Parse categories and tags
        category_list = [c.strip() for c in categories.split(",")] if categories else None
        tag_list = [t.strip() for t in tags.split(",")] if tags else None

        # Show processing message
        console.print()
        console.print(f"[cyan]Fetching YouTube video:[/cyan] {video_id}")
        console.print()

        # Add video using ingestion system (it fetches metadata and transcript internally)
        console.print("[cyan]  → Fetching video metadata...[/cyan]")
        console.print("[cyan]  → Fetching transcript...[/cyan]")

        ingestion = VideoIngestion(library.root)
        video = ingestion.add_single_video(
            video_id_or_url=video_url,
            categories=category_list,
            tags=tag_list,
        )

        # Update catalog and regenerate indices
        from resourcelibrarian.core.catalog_manager import CatalogManager
        from resourcelibrarian.core.index_generator import IndexGenerator

        catalog_mgr = CatalogManager(library.root)
        catalog_mgr.add_video(video)

        # Regenerate indices
        catalog = catalog_mgr.load_catalog()
        index_gen = IndexGenerator(library.root)
        index_gen.generate_all_indices(catalog)

        # Success message
        console.print()
        console.print(
            Panel.fit(
                f"[green]✓[/green] Video added successfully!\n\n"
                f"[bold]Title:[/bold] {video.title}\n"
                f"[bold]Channel:[/bold] {video.channel_title}\n"
                f"[bold]Video ID:[/bold] {video.video_id}\n"
                f"[bold]Location:[/bold] {video.folder_path.relative_to(library.root)}\n"
                + (
                    f"[bold]Categories:[/bold] {', '.join(video.manifest.categories)}\n"
                    if video.manifest.categories
                    else ""
                )
                + (f"[bold]Tags:[/bold] {', '.join(video.tags)}\n" if video.tags else ""),
                title="[bold green]Video Added[/bold green]",
                border_style="green",
            )
        )
        console.print()

    except (YouTubeAPIError, TranscriptNotAvailableError, ValueError) as e:
        console.print()
        console.print(
            Panel.fit(
                f"[red]✗[/red] {str(e)}",
                title="[bold red]Error[/bold red]",
                border_style="red",
            )
        )
        console.print()
        raise typer.Exit(1)
    except Exception as e:
        console.print()
        console.print(
            Panel.fit(
                f"[red]✗[/red] An unexpected error occurred:\n\n{str(e)}",
                title="[bold red]Error[/bold red]",
                border_style="red",
            )
        )
        console.print()
        raise typer.Exit(1)


@video_app.command("list")
def video_list(
    library_path: str = typer.Option(
        ".",
        "--library",
        "-l",
        help="Path to the library (default: current directory)",
    ),
    channel: Optional[str] = typer.Option(
        None,
        "--channel",
        "-c",
        help="Filter by channel (case-insensitive substring match)",
    ),
    category: Optional[str] = typer.Option(
        None,
        "--category",
        help="Filter by category (case-insensitive substring match)",
    ),
    tag: Optional[str] = typer.Option(
        None,
        "--tag",
        "-t",
        help="Filter by tag (case-insensitive substring match)",
    ),
    title: Optional[str] = typer.Option(
        None,
        "--title",
        help="Filter by title (case-insensitive substring match)",
    ),
):
    """List all videos in the library with optional filters.

    Examples:
        rl video list
        rl video list --channel "Anthropic"
        rl video list --category "AI"
        rl video list --tag "tutorial" --channel "DeepMind"
    """
    try:
        # Load library
        library = ResourceLibrary(library_path)
        if not library.exists():
            console.print()
            console.print(
                Panel.fit(
                    f"[red]✗[/red] Not a valid Resource Library: {library.root}\n\n"
                    f"[dim]Initialize a library first:[/dim]\n"
                    f"  [cyan]rl init /path/to/library[/cyan]",
                    title="[bold red]Library Not Found[/bold red]",
                    border_style="red",
                )
            )
            console.print()
            raise typer.Exit(1)

        # Load catalog
        catalog = library.load_catalog()

        # Apply filters
        videos = catalog.search_videos(channel=channel, category=category, tag=tag, title=title)

        if not videos:
            console.print()
            filter_desc = []
            if channel:
                filter_desc.append(f"channel: {channel}")
            if category:
                filter_desc.append(f"category: {category}")
            if tag:
                filter_desc.append(f"tag: {tag}")
            if title:
                filter_desc.append(f"title: {title}")

            if filter_desc:
                console.print(
                    f"[yellow]No videos found matching filters: {', '.join(filter_desc)}[/yellow]"
                )
            else:
                console.print("[yellow]No videos in library yet.[/yellow]")
            console.print()
            return

        # Create table
        table = Table(title=f"Videos in Library ({len(videos)} found)")
        table.add_column("Title", style="cyan", no_wrap=False)
        table.add_column("Channel", style="green")
        table.add_column("Video ID", style="blue")
        table.add_column("Categories", style="yellow")

        for video in videos:
            categories_str = (
                ", ".join(video.manifest.categories) if video.manifest.categories else "-"
            )
            table.add_row(video.title, video.channel_title, video.video_id, categories_str)

        console.print()
        console.print(table)
        console.print()

    except FileNotFoundError as e:
        console.print()
        console.print(
            Panel.fit(
                f"[red]✗[/red] {str(e)}",
                title="[bold red]Error[/bold red]",
                border_style="red",
            )
        )
        console.print()
        raise typer.Exit(1)
    except Exception as e:
        console.print()
        console.print(
            Panel.fit(
                f"[red]✗[/red] An unexpected error occurred:\n\n{str(e)}",
                title="[bold red]Error[/bold red]",
                border_style="red",
            )
        )
        console.print()
        raise typer.Exit(1)


@video_app.command("get")
def video_get(
    identifier: str = typer.Argument(..., help="YouTube video ID or title to retrieve"),
    library_path: str = typer.Option(
        ".",
        "--library",
        "-l",
        help="Path to the library (default: current directory)",
    ),
    output: Optional[str] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path. If not specified, prints to stdout",
    ),
):
    """Retrieve video transcript by YouTube video ID or title.

    Examples:
        rl video get dQw4w9WgXcQ
        rl video get "My Video Title"
        rl video get dQw4w9WgXcQ --output transcript.txt
    """
    try:
        # Load library
        library = ResourceLibrary(library_path)
        if not library.exists():
            console.print()
            console.print(
                Panel.fit(
                    f"[red]✗[/red] Not a valid Resource Library: {library.root}\n\n"
                    f"[dim]Initialize a library first:[/dim]\n"
                    f"  [cyan]rl init /path/to/library[/cyan]",
                    title="[bold red]Library Not Found[/bold red]",
                    border_style="red",
                )
            )
            console.print()
            raise typer.Exit(1)

        # Load catalog
        catalog = library.load_catalog()

        # Find video by ID first, then by title
        video = catalog.find_video(identifier)
        if not video:
            # Try finding by title
            video = catalog.find_video_by_title(identifier)

        if not video:
            console.print()
            console.print(
                Panel.fit(
                    f"[red]✗[/red] Video not found: {identifier}\n\n"
                    f"[dim]Try:[/dim]\n"
                    f"  [cyan]rl video list[/cyan] - to see all videos\n"
                    f'  [cyan]rl video list --title "search term"[/cyan] - to search for videos',
                    title="[bold red]Video Not Found[/bold red]",
                    border_style="red",
                )
            )
            console.print()
            raise typer.Exit(1)

        # Get transcript path
        transcript_path = video.get_transcript_path()
        if not transcript_path or not transcript_path.exists():
            console.print()
            console.print(
                Panel.fit(
                    f"[red]✗[/red] Transcript not found for: {video.title}\n\n"
                    f"[dim]The video exists in the library but has no transcript.[/dim]",
                    title="[bold red]Transcript Not Found[/bold red]",
                    border_style="red",
                )
            )
            console.print()
            raise typer.Exit(1)

        # Output to file or stdout
        if output:
            output_path = Path(output)
            output_path.write_bytes(transcript_path.read_bytes())
            console.print()
            console.print(
                Panel.fit(
                    f"[green]✓[/green] Transcript written to: {output_path}\n\n"
                    f"[bold]Video:[/bold] {video.title}\n"
                    f"[bold]Channel:[/bold] {video.channel_title}\n"
                    f"[bold]Video ID:[/bold] {video.video_id}\n"
                    f"[bold]Size:[/bold] {output_path.stat().st_size:,} bytes",
                    title="[bold green]Success[/bold green]",
                    border_style="green",
                )
            )
            console.print()
        else:
            # Print to stdout
            content = transcript_path.read_text(encoding="utf-8")
            console.print()
            console.print(
                Panel.fit(
                    f"[bold]{video.title}[/bold]\n"
                    f"Channel: {video.channel_title}\n"
                    f"Video ID: {video.video_id}"
                )
            )
            console.print()
            console.print(content)
            console.print()

    except FileNotFoundError as e:
        console.print()
        console.print(
            Panel.fit(
                f"[red]✗[/red] {str(e)}",
                title="[bold red]Error[/bold red]",
                border_style="red",
            )
        )
        console.print()
        raise typer.Exit(1)
    except Exception as e:
        console.print()
        console.print(
            Panel.fit(
                f"[red]✗[/red] An unexpected error occurred:\n\n{str(e)}",
                title="[bold red]Error[/bold red]",
                border_style="red",
            )
        )
        console.print()
        raise typer.Exit(1)


# ================================================================================
# Catalog Commands
# ================================================================================


@catalog_app.command("rebuild")
def catalog_rebuild(
    library: str = typer.Option(
        ".",
        "--library",
        "-l",
        help="Path to the library (default: current directory)",
    ),
):
    """Rebuild the library catalog and indices from filesystem.

    Scans the entire library (books/ and videos/ directories) and rebuilds:
    - catalog.yaml with all books and videos
    - Master index files (authors.md, titles.md, channels.md)
    - Individual index.md files for each resource
    - Library-wide statistics and navigation

    Use this command if:
    - The catalog file is missing or corrupted
    - You've manually added/moved files in the library
    - Index files are out of date

    Example:
        rl catalog rebuild
        rl catalog rebuild --library /path/to/library
    """
    from datetime import datetime
    from resourcelibrarian.core.catalog_manager import CatalogManager
    from resourcelibrarian.core.index_generator import IndexGenerator

    console.print()
    console.print("[bold cyan]Rebuilding Library Catalog[/bold cyan]")
    console.print()

    try:
        # Verify library exists
        lib_path = Path(library).resolve()
        lib = ResourceLibrary(lib_path)

        if not lib.exists():
            raise FileNotFoundError(
                f"Not a valid Resource Library: {lib_path}\n"
                f"Initialize a library first with: rl init {lib_path}"
            )

        # Rebuild catalog
        console.print("[cyan]  → Scanning books directory...[/cyan]")
        catalog_mgr = CatalogManager(lib.root)
        catalog = catalog_mgr.rebuild_catalog()

        console.print(f"[cyan]  → Found {len(catalog.books)} books[/cyan]")
        console.print(f"[cyan]  → Found {len(catalog.videos)} videos[/cyan]")

        # Generate indices
        console.print("[cyan]  → Generating master indices...[/cyan]")
        index_gen = IndexGenerator(lib.root)
        index_gen.generate_all_indices(catalog)

        console.print("[cyan]  → Generating individual resource indices...[/cyan]")

        # Show stats
        stats = catalog.get_stats()

        console.print()
        console.print(
            Panel.fit(
                f"[green]✓[/green] Catalog rebuilt successfully!\n\n"
                f"[bold]Total Items:[/bold] {stats['total_items']}\n"
                f"[bold]Books:[/bold] {stats['total_books']}\n"
                f"[bold]Videos:[/bold] {stats['total_videos']}\n"
                f"[bold]Authors:[/bold] {stats['unique_authors']}\n"
                f"[bold]Categories:[/bold] {stats['unique_categories']}\n"
                f"[bold]Tags:[/bold] {stats['unique_tags']}\n\n"
                f"[bold]Indices Generated:[/bold]\n"
                f"  • Library index: _index/README.md\n"
                f"  • Books by author: books/_index/authors.md\n"
                f"  • Books by title: books/_index/titles.md\n"
                f"  • Videos by channel: videos/_index/channels.md\n"
                f"  • Individual resource indices: {stats['total_items']} files\n\n"
                f"[bold]Last Updated:[/bold] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                title="[bold green]Catalog Rebuilt[/bold green]",
                border_style="green",
            )
        )
        console.print()

    except FileNotFoundError as e:
        console.print()
        console.print(
            Panel.fit(
                f"[red]✗[/red] {str(e)}",
                title="[bold red]Error[/bold red]",
                border_style="red",
            )
        )
        console.print()
        raise typer.Exit(1)
    except Exception as e:
        console.print()
        console.print(
            Panel.fit(
                f"[red]✗[/red] An unexpected error occurred:\n\n{str(e)}",
                title="[bold red]Error[/bold red]",
                border_style="red",
            )
        )
        console.print()
        raise typer.Exit(1)


@catalog_app.command("stats")
def catalog_stats(
    library: str = typer.Option(
        ".",
        "--library",
        "-l",
        help="Path to the library (default: current directory)",
    ),
):
    """Show library statistics from the catalog.

    Displays comprehensive statistics about your library including:
    - Total books and videos
    - Number of unique authors, categories, and tags
    - Format and summary counts
    - Last update timestamp

    Example:
        rl catalog stats
        rl catalog stats --library /path/to/library
    """
    from resourcelibrarian.core.catalog_manager import CatalogManager

    console.print()

    try:
        # Verify library exists
        lib_path = Path(library).resolve()
        lib = ResourceLibrary(lib_path)

        if not lib.exists():
            raise FileNotFoundError(
                f"Not a valid Resource Library: {lib_path}\n"
                f"Initialize a library first with: rl init {lib_path}"
            )

        # Load catalog
        catalog_mgr = CatalogManager(lib.root)
        catalog = catalog_mgr.load_catalog()
        stats = catalog.get_stats()

        # Display stats
        console.print(
            Panel.fit(
                f"[bold]Library Statistics[/bold]\n\n"
                f"[cyan]Content:[/cyan]\n"
                f"  • Total Items: {stats['total_items']}\n"
                f"  • Books: {stats['total_books']}\n"
                f"  • Videos: {stats['total_videos']}\n\n"
                f"[cyan]Organization:[/cyan]\n"
                f"  • Unique Authors: {stats['unique_authors']}\n"
                f"  • Unique Categories: {stats['unique_categories']}\n"
                f"  • Unique Tags: {stats['unique_tags']}\n\n"
                f"[cyan]Formats & Summaries:[/cyan]\n"
                f"  • Book Formats: {stats['book_formats']}\n"
                f"  • Book Summaries: {stats['book_summaries']}\n"
                f"  • Video Summaries: {stats['video_summaries']}\n\n"
                f"[cyan]Last Updated:[/cyan] {stats.get('last_updated', 'Unknown')}",
                title=f"[bold]{lib.root}[/bold]",
                border_style="cyan",
            )
        )
        console.print()

    except FileNotFoundError as e:
        console.print()
        console.print(
            Panel.fit(
                f"[red]✗[/red] {str(e)}",
                title="[bold red]Error[/bold red]",
                border_style="red",
            )
        )
        console.print()
        raise typer.Exit(1)
    except Exception as e:
        console.print()
        console.print(
            Panel.fit(
                f"[red]✗[/red] An unexpected error occurred:\n\n{str(e)}",
                title="[bold red]Error[/bold red]",
                border_style="red",
            )
        )
        console.print()
        raise typer.Exit(1)


@catalog_app.command("migrate")
def catalog_migrate(
    library: str = typer.Option(
        ".", "--library", "-l", help="Path to the library (old format)"
    ),
):
    """Migrate an old library (.knowledgehub) to new format (catalog.yaml).

    This rebuilds the catalog from your existing books/ and videos/ directories.
    Your content is preserved - only the catalog format changes.
    """
    import shutil

    from resourcelibrarian.core.catalog_manager import CatalogManager

    console.print()
    console.print("[bold cyan]Migrating Library to New Format[/bold cyan]")
    console.print()

    try:
        lib_path = Path(library).resolve()

        # Check if it's an old-style library
        old_metadata_dir = lib_path / ".knowledgehub"

        if not old_metadata_dir.exists():
            console.print(
                Panel.fit(
                    f"[red]✗[/red] No old-style library found at: {lib_path}\n\n"
                    f"Looking for: {old_metadata_dir}\n\n"
                    f"This command is for migrating libraries with .knowledgehub/ directory.\n"
                    f"If you have a new-format library, use: rl catalog rebuild",
                    title="[bold red]Error[/bold red]",
                    border_style="red",
                )
            )
            console.print()
            raise typer.Exit(1)

        # Check if books and videos directories exist
        books_dir = lib_path / "books"
        videos_dir = lib_path / "videos"

        if not (books_dir.exists() or videos_dir.exists()):
            console.print(
                Panel.fit(
                    "[red]✗[/red] No books/ or videos/ directories found\n\n"
                    "Cannot find content to migrate.",
                    title="[bold red]Error[/bold red]",
                    border_style="red",
                )
            )
            console.print()
            raise typer.Exit(1)

        # Check if already migrated
        new_catalog_path = lib_path / "catalog.yaml"
        if new_catalog_path.exists():
            console.print(
                Panel.fit(
                    "[yellow]⚠[/yellow]  Library already has catalog.yaml\n\n"
                    "The library appears to already be migrated.\n"
                    "Use: rl catalog rebuild to regenerate the catalog.",
                    title="[bold yellow]Warning[/bold yellow]",
                    border_style="yellow",
                )
            )
            console.print()
            raise typer.Exit(0)

        # Backup old metadata directory
        backup_dir = lib_path / ".knowledgehub.backup"
        console.print(f"[cyan]→[/cyan] Backing up .knowledgehub/ to {backup_dir.name}/...")
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        shutil.copytree(old_metadata_dir, backup_dir)

        # Rebuild catalog from filesystem
        console.print("[cyan]→[/cyan] Scanning books and videos...")
        catalog_mgr = CatalogManager(lib_path)
        catalog = catalog_mgr.rebuild_catalog()

        # Create library index directory if it doesn't exist
        index_dir = lib_path / "_index"
        if not index_dir.exists():
            index_dir.mkdir()

        # Generate indices
        console.print("[cyan]→[/cyan] Generating indices...")
        from resourcelibrarian.core.index_generator import IndexGenerator
        index_gen = IndexGenerator(lib_path)
        index_gen.generate_all_indices(catalog)

        # Get stats
        stats = catalog.get_stats()

        # Success message
        console.print()
        console.print(
            Panel.fit(
                f"[green]✓[/green] Migration successful!\n\n"
                f"[cyan]What was found:[/cyan]\n"
                f"  • Books: {stats['total_books']}\n"
                f"  • Videos: {stats['total_videos']}\n"
                f"  • Categories: {stats['unique_categories']}\n\n"
                f"[cyan]What changed:[/cyan]\n"
                f"  • Created: catalog.yaml (at library root)\n"
                f"  • Created: _index/ (navigation indices)\n"
                f"  • Backed up: .knowledgehub/ → .knowledgehub.backup/\n"
                f"  • Format: JSON → YAML\n\n"
                f"[cyan]Next steps:[/cyan]\n"
                f"  • Your library is ready to use with the new version!\n"
                f"  • You can safely delete .knowledgehub.backup/ if everything works\n"
                f"  • All your books and videos are preserved!",
                title="[bold green]Migration Complete[/bold green]",
                border_style="green",
            )
        )
        console.print()

    except typer.Exit:
        raise
    except Exception as e:
        console.print()
        console.print(
            Panel.fit(
                f"[red]✗[/red] Migration failed:\n\n{str(e)}\n\n"
                f"Your original library is unchanged.",
                title="[bold red]Error[/bold red]",
                border_style="red",
            )
        )
        console.print()
        raise typer.Exit(1)
