import json
from pathlib import Path
from typing import List, Dict, Any
import unicodedata


def normalize(value):
    """Convert full-width characters to half-width (except for kana) and handle lists."""
    if isinstance(value, list):
        value = ", ".join(value)
    return unicodedata.normalize("NFKC", value.replace("’", "'").strip())


def load_track_list(track_list_path: Path) -> List[Dict[str, Any]]:
    """
    Load track information from a JSON file.

    Args:
        track_list_path: Path to existing track JSON file

    Returns:
        List of track information dictionaries
    """
    if track_list_path.exists():
        print(f"Loading tracks from {track_list_path}...")
        return json.loads(track_list_path.read_text())

    return []


def save_track_list(track_list: List[Dict[str, Any]], track_list_path: Path) -> None:
    """
    Save track information to a JSON file.

    Args:
        track_dict: Track information to save
        track_list_path: Path to file for saving
    """
    track_list_path.write_text(json.dumps(track_list, indent=2, ensure_ascii=False))
    print(f"Progress saved to {track_list_path}")


def merge_tracks(service, new_tracks, track_list):
    # Helper function to safely extract a nested value
    def safe_get(d, keys, default=None):
        for key in keys:
            if not isinstance(d, dict):
                return default
            d = d.get(key)
        return d if d is not None else default

    # 1. Create a dictionary using ISRC as the key (O(N))
    isrc_dict = {
        safe_get(track, ["apple_music", "response", "attributes", "isrc"]): track
        for track in track_list
        if safe_get(track, ["apple_music", "response", "attributes", "isrc"])
    }

    # 2. Create dictionaries using title + artist and title only as keys (O(N))
    title_artist_dict = {
        f"{track.get('title', '')}|{track.get('artist', '')}": track
        for track in track_list
        if track.get("title") and track.get("artist")
    }
    title_dict = {
        track.get("title", ""): track for track in track_list if track.get("title")
    }

    # 3. Search for each track in the playlist and update or add it (O(M))
    for i, track in enumerate(new_tracks):
        print(f"Processing track {i+1}/{len(new_tracks)}...")

        isrc = track.get("isrc", "")
        title = track.get("title", "")
        artist = track.get("artist", "")

        if isrc and isrc in isrc_dict:
            # Match found by ISRC (highest priority)
            isrc_dict[isrc][service] = track
            isrc_dict[isrc][service]["match_type"] = "isrc"
        elif title and artist and f"{title}|{artist}" in title_artist_dict:
            # Match found by title + artist
            title_artist_dict[f"{title}|{artist}"][service] = track
            title_artist_dict[f"{title}|{artist}"][service][
                "match_type"
            ] = "title_artist"
        elif title and title in title_dict:
            # Match found by title only
            title_dict[title][service] = track
            title_dict[title][service][service] = "title"
        else:
            track_to_be_added = {
                "title": title,
                "artist": artist,
                "album": track.get("album", ""),
                service: {**track, "match_type": "new"},
            }

            # Skip if the track is already in the list. Determine it by "service": {**track}
            if any(
                existing_track.get(service) == track_to_be_added.get(service)
                for existing_track in track_list
                if existing_track.get(service)
            ):
                continue

            # No match found, add as a new track
            print(f"No match found for {title} by {artist}")
            track_list.append(
                {
                    "title": title,
                    "artist": artist,
                    "album": track.get("album", ""),
                    service: {**track, "match_type": "new"},
                }
            )

    return track_list  # Return the updated track list
