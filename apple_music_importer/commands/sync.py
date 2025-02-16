import json
import typer
from pathlib import Path
from apple_music_importer.api.apple_music import AppleMusicAPI
from apple_music_importer.utils import load_track_list
from apple_music_importer.session import SessionHandler


def _add_tracks(
    source: str,
    track_list: list,
    apple_music_api: AppleMusicAPI,
    add_to_library: bool,
    create_playlist: bool,
):
    """Add tracks from a specified source to Apple Music."""
    song_list = list(filter(lambda track: source in track, track_list))
    song_list.sort(key=lambda track: track[source]["date_added"])
    music_id_list = [
        track["apple_music"]["response"]["id"]
        for track in song_list
        if "apple_music" in track
        and "response" in track["apple_music"]
        and "id" in track["apple_music"]["response"]
    ]
    if add_to_library:
        response = apple_music_api.add_tracks_to_library(music_id_list)
        print(f"Successfully added {len(music_id_list)} tracks to the library")
    if create_playlist:
        apple_music_api.create_playlist(
            f"Imported from {source.capitalize()}", music_id_list
        )
        print(f'Successfully created playlist "Imported from {source.capitalize()}"')


def sync(
    ctx: typer.Context,
    delete_all_tracks: bool = typer.Option(
        False,
        "--delete-all-tracks",
        help="Delete all tracks in the Apple Music Cloud Library (except for Apple Music tracks)",
    ),
    sync_spotify: bool = typer.Option(
        False,
        "--sync-spotify",
        help="Sync tracks from Spotify",
    ),
    sync_local: bool = typer.Option(
        False,
        "--sync-local",
        help="Sync tracks from local files",
    ),
    create_playlist: bool = typer.Option(
        False,
        "--create-playlist",
        help="Create a playlist with the synced tracks (Each source will create a separate playlist)",
    ),
    add_to_library: bool = typer.Option(
        False,
        "--add-to-library",
        help="Add the synced tracks to the Apple Music Library",
    ),
):
    """
    Sync tracks from Spotify and local files with Apple Music.
    """

    # Load track information from the track list file
    track_list_path = ctx.obj["track_list"] or Path("tracks.list")
    track_list = load_track_list(track_list_path)

    request_headers = json.loads(ctx.obj["request_headers"].read_text())
    session_handler = SessionHandler(request_headers)

    apple_music_api = AppleMusicAPI(
        session_handler,
        ctx.obj["country_code"],
        ctx.obj["limit"],
    )

    # First, get the contents of the library from Apple Music
    # TODO: Implement this

    # Second, add tracks from Spotify
    if sync_spotify:
        _add_tracks(
            "spotify", track_list, apple_music_api, add_to_library, create_playlist
        )

    # Third, add tracks from local files
    if sync_local:
        _add_tracks(
            "local", track_list, apple_music_api, add_to_library, create_playlist
        )
