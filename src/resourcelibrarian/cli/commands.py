"""CLI commands for Resource Librarian.

Uses:
- Typer: https://typer.tiangolo.com/ - CLI framework with type hints
- Rich: https://rich.readthedocs.io/ - Beautiful terminal output
"""

import typer
from rich.console import Console
from rich.panel import Panel

from resourcelibrarian.library import ResourceLibrary

app = typer.Typer(
    name="rl",
    help="Resource Librarian - Manage your digital library of books and YouTube video transcripts",
    add_completion=False,
)

console = Console()


@app.command()
def init(
    path: str = typer.Argument(
        ...,
        help="Path where the library should be initialized",
    ),
):
    """Initialize a new Resource Library.

    Creates the complete directory structure including:
    - .metadata/ for catalog and state files
    - books/ for book storage
    - videos/ for YouTube video transcripts
    - Index files for navigation
    """
    try:
        # Initialize the library
        library = ResourceLibrary.initialize(path)

        # Success message
        console.print()
        console.print(Panel.fit(
            f"[green]✓[/green] Resource Library initialized successfully!\n\n"
            f"[bold]Location:[/bold] {library.root}\n\n"
            f"[dim]Directory structure created:[/dim]\n"
            f"  • .metadata/ (catalog and state files)\n"
            f"  • books/ (book storage and indices)\n"
            f"  • videos/ (YouTube transcripts and indices)\n\n"
            f"[bold]Next steps:[/bold]\n"
            f"  • Add books: [cyan]rl add book <file>[/cyan]\n"
            f"  • Fetch video transcripts: [cyan]rl fetch video <url>[/cyan]\n"
            f"  • Build catalog: [cyan]rl catalog build[/cyan]",
            title="[bold green]Library Initialized[/bold green]",
            border_style="green",
        ))
        console.print()

    except FileExistsError as e:
        console.print()
        console.print(Panel.fit(
            f"[red]✗[/red] {str(e)}\n\n"
            f"[dim]The directory already exists. If you want to initialize a library:\n"
            f"  • Choose a different location, or\n"
            f"  • Remove the existing directory first[/dim]",
            title="[bold red]Initialization Failed[/bold red]",
            border_style="red",
        ))
        console.print()
        raise typer.Exit(1)
    except Exception as e:
        console.print()
        console.print(Panel.fit(
            f"[red]✗[/red] An unexpected error occurred:\n\n"
            f"{str(e)}",
            title="[bold red]Error[/bold red]",
            border_style="red",
        ))
        console.print()
        raise typer.Exit(1)
