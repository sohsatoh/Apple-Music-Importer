import json
import typer
from pathlib import Path
from typing import Annotated
from apple_music_importer.api.spotify import SpotifyAPI
from apple_music_importer.api.apple_music import AppleMusicAPI
from apple_music_importer.utils import load_track_list, save_track_list, merge_tracks
from apple_music_importer.session import SessionHandler, UnauthorizedRequestException


def spotify(
    ctx: typer.Context,
    playlist: Annotated[
        str, typer.Argument(help="Spotify playlist ID, URL, or 'liked' for liked songs")
    ] = "liked",
):
    """
    Search Spotify playlist in Apple Music.
    """

    # Load track information from the track list file
    track_list_path = ctx.obj["track_list"] or Path("tracks.list")
    track_list = load_track_list(track_list_path)

    # Load tracks from the Spotify playlist
    spotify_api = SpotifyAPI()
    print(f"Loading tracks from Spotify playlist {playlist}...")
    playlist_tracks = spotify_api.get_playlist_tracks(playlist)

    # Search for each track in track list and append the value as "spotify" key
    ## The priority is:
    ## 1. Search by ISRC
    ## 2. Search by title and artist
    ## 3. Search by title
    # If no match is found, the track should be newly added to the track list
    print("Merging tracks...")
    merged_track_list = merge_tracks("spotify", playlist_tracks, track_list)

    # Save the updated track list
    save_track_list(merged_track_list, track_list_path)

    # Update the track list if it does not have the "apple_music" key
    request_headers = json.loads(ctx.obj["request_headers"].read_text())
    session_handler = SessionHandler(request_headers)
    apple_music_api = AppleMusicAPI(
        session_handler,
        ctx.obj["country_code"],
        ctx.obj["limit"],
    )
    print("Updating track list...")
    for i, track in enumerate(merged_track_list):
        if "apple_music" not in track and "spotify" in track:
            print(
                f"Searching track {i+1}/{len(merged_track_list)}: {track['title']} by {track['artist']}..."
            )
            isrc = track["spotify"]["isrc"]
            try:
                search_result = apple_music_api.search_track_by_isrc(isrc)
                if search_result is None:
                    print("Searching by title and artist instead...")
                    search_result = apple_music_api.search_track_from_text(
                        track["title"], track["artist"], track["album"], False
                    )
                    (
                        print("Could not be found")
                        if search_result is None
                        else print("Found")
                    )
                track["apple_music"] = search_result
            except UnauthorizedRequestException as e:
                print(f"Error: {e}")
                break
