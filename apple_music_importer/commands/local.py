import os
import json
from pathlib import Path
import typer
from apple_music_importer.metadata import MetadataHandler
from apple_music_importer.api.apple_music import AppleMusicAPI
from apple_music_importer.session import SessionHandler, UnauthorizedRequestException
from apple_music_importer.utils import load_track_list, save_track_list, merge_tracks


def _get_file_list_recursive(folder_path: str) -> list:
    """Recursively get all MP3 files in the given folder."""
    files = []
    for root, _, filenames in os.walk(folder_path):
        for file in filenames:
            if file.lower().endswith(".mp3"):
                files.append(os.path.join(root, file))
    print(f"Found {len(files)} mp3 files")
    return files


def _edit_metadata_interactively(track: dict) -> bool:
    """Edit mp3 tag metadata interactively."""
    print("Edit mp3 tag metadata interactively...")
    track["title"] = input(f"Title ({track['title']}): ") or track["title"]
    track["artist"] = input(f"Artist ({track['artist']}): ") or track["artist"]
    track["album"] = input(f"Album ({track['album']}): ") or track["album"]

    confirm_message = (
        f"Track will be saved with the new metadata\n"
        f"Title: {track['title']}\n"
        f"Artist: {track['artist']}\n"
        f"Album: {track['album']}\n(Y/n): "
    )
    if input(confirm_message).lower() == "y":
        # Save the edited track information into mp3 file
        MetadataHandler.save_metadata_to_mp3(
            track["local"]["path"],
            track["title"],
            track["artist"],
            track["album"],
        )
        return True
    else:
        return False


def _search_and_update_track(
    apple_music_api: AppleMusicAPI, track: dict, require_confirm: bool, allow_edit: bool
) -> dict:
    """Search for a track on Apple Music and update the track information."""
    search_result = apple_music_api.search_track_from_text(
        track["title"],
        track["artist"],
        track["album"],
        require_confirm,
    )

    if search_result is None:
        print(f"No results found for {track['title']} by {track['artist']}")
        if allow_edit:
            success = _edit_metadata_interactively(track)
            if success:
                return _search_and_update_track(
                    apple_music_api, track, require_confirm, allow_edit
                )

    track["apple_music"] = search_result
    return track


def local(
    ctx: typer.Context,
    folder_path: Path,
    artist_name_position: int = typer.Option(
        -2,
        help="Position of artist name in file path (e.g., -2 for '.../Artist/Album/Title.mp3')",
    ),
    album_name_position: int = typer.Option(
        -1,
        help="Position of album name in file path (e.g., -1 for '.../Artist/Album/Title.mp3')",
    ),
    allow_edit: bool = typer.Option(
        False,
        help="Edit mp3 tag metadata interactively (only if the song is not found in Apple Music)",
    ),
):
    """
    Search local music files in Apple Music.
    """
    track_list_path = ctx.obj["track_list"] or Path("tracks.list")
    track_list = load_track_list(track_list_path)

    # Load track information from local music files if no progress file is found
    print("Loading local music files...")
    files = _get_file_list_recursive(str(folder_path))
    track_list = merge_tracks(
        "local",
        MetadataHandler.get_track_list_from_files(
            files, artist_name_position, album_name_position
        ),
        track_list,
    )
    save_track_list(track_list, track_list_path)

    request_headers = json.loads(ctx.obj["request_headers"].read_text())
    session_handler = SessionHandler(request_headers)

    apple_music_api = AppleMusicAPI(
        session_handler,
        ctx.obj["country_code"],
        ctx.obj["limit"],
    )

    try:
        # Search tracks using Apple Music API
        track_list_with_apple_music_info = []

        for i, track in enumerate(track_list, 1):
            if "apple_music" in track:
                track_list_with_apple_music_info.append(track)
                continue

            print(
                f"Searching track {i}/{len(track_list)}: {track['title']} by {track['artist']}"
            )
            updated_track = _search_and_update_track(
                apple_music_api, track, ctx.obj["require_confirm"], allow_edit
            )
            track_list_with_apple_music_info.append(updated_track)

        save_track_list(track_list_with_apple_music_info, track_list_path)
        print("Search complete!")

    except (KeyboardInterrupt, UnauthorizedRequestException):
        if typer.confirm("\nProcess interrupted. Do you want to save progress?"):
            save_track_list(track_list, track_list_path)
    except Exception as e:
        print(f"Error: {e}")
        raise typer.Exit(code=1)
    finally:
        session_handler.session.close()
