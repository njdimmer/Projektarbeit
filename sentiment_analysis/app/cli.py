from typing import Optional
import typer

from . import __app_name__, __version__

app =  typer.Typer()

def _version_callback(value: bool):
    if value:
        typer.echo(f"{__app_name__} version: {__version__}")
        raise typer.Exit()
    
@app.callback()
def version(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    return

@app.command()
def scrape(
    analyze: Optional[bool] = typer.Option(
        None,
        "--scrape",
        "-s",
        help="Scrape reviews from Letterboxd.",
    )
) -> None:
    return