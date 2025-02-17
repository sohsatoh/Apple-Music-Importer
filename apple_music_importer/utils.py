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
    def safe_get(d, keys, default=None):
        for key in keys:
            if not isinstance(d, dict):
                return default
            d = d.get(key)
        return d if d is not None else default

    isrc_dict = {
        safe_get(track, ["apple_music", "response", "attributes", "isrc"]): track
        for track in track_list
        if safe_get(track, ["apple_music", "response", "attributes", "isrc"])
    }

    title_artist_dict = {
        f"{track.get('title', '')}|{track.get('artist', '')}": track
        for track in track_list
        if track.get("title") and track.get("artist")
    }
    title_dict = {
        track.get("title", ""): track for track in track_list if track.get("title")
    }

    def get_service_data(track):
        if service in track and isinstance(track[service], dict):
            return track[service].copy()
        return {
            k: v
            for k, v in track.items()
            if k not in ("title", "artist", "album", service)
        }

    for i, track in enumerate(new_tracks):
        print(f"Processing track {i+1}/{len(new_tracks)}...")
        isrc = track.get("isrc", "")
        title = track.get("title", "")
        artist = track.get("artist", "")

        if isrc and isrc in isrc_dict:
            service_data = get_service_data(track)
            service_data["match_type"] = "isrc"
            isrc_dict[isrc][service] = service_data
        elif title and artist and f"{title}|{artist}" in title_artist_dict:
            service_data = get_service_data(track)
            service_data["match_type"] = "title_artist"
            title_artist_dict[f"{title}|{artist}"][service] = service_data
        elif title and title in title_dict:
            service_data = get_service_data(track)
            service_data["match_type"] = "title"
            title_dict[title][service] = service_data
        else:
            print(f"No match found for {title} by {artist}")
            service_data = get_service_data(track)
            service_data["match_type"] = "new"
            track_to_be_added = {
                "title": title,
                "artist": artist,
                "album": track.get("album", ""),
                service: service_data,
            }
            track_list.append(track_to_be_added)

    return track_list
