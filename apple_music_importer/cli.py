from pathlib import Path
from typing import Optional
import typer
from typing_extensions import Annotated
from apple_music_importer.commands.local import local
from apple_music_importer.commands.spotify import spotify
from apple_music_importer.commands.sync import sync


app = typer.Typer(
    help="Track import tool for Apple Music",
)

app.command()(local)
app.command()(spotify)
app.command()(sync)


@app.callback()
def callback(
    ctx: typer.Context,
    request_headers_path: Annotated[
        Path,
        typer.Option(
            ...,
            "--request-headers",
            help="Path to JSON file containing request headers for Apple Music API",
            exists=True,
            file_okay=True,
            dir_okay=False,
        ),
    ],
    track_list_path: Annotated[
        Optional[Path],
        typer.Option(
            "--track-list",
            help="Path to the file containing track info (resume from this file if specified)",
        ),
    ] = None,
    country_code: Annotated[
        str,
        typer.Option(
            help="Country code for Apple Music search",
        ),
    ] = "US",
    search_limit: Annotated[
        int,
        typer.Option(
            help="Number of search results to retrieve",
            min=1,
            max=10,
        ),
    ] = 3,
    require_confirm: Annotated[
        bool,
        typer.Option(
            help="Require confirmation for artist name mismatch (skips automatically if not set)",
        ),
    ] = False,
) -> None:
    """
    Track import tool for Apple Music
    """
    ctx.ensure_object(dict)
    ctx.obj["request_headers"] = request_headers_path
    ctx.obj["country_code"] = country_code.lower()
    ctx.obj["limit"] = search_limit
    ctx.obj["track_list"] = track_list_path
    ctx.obj["require_confirm"] = require_confirm


if __name__ == "__main__":
    app()
