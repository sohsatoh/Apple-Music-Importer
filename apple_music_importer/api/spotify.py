import spotipy
from spotipy.oauth2 import SpotifyOAuth
from apple_music_importer.utils import normalize

scope = "user-library-read"


class SpotifyAPI:
    def __init__(self):
        self.client = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    def _organize_playlist_tracks(self, tracks):
        return [
            {
                "id": track["track"]["id"],
                "title": normalize(track["track"]["name"]),
                "artist": normalize(track["track"]["artists"][0]["name"]),
                "album": normalize(track["track"]["album"]["name"]),
                "url": track["track"]["external_urls"]["spotify"],
                "date_added": track["added_at"],
                "isrc": track["track"]["external_ids"]["isrc"].upper(),
            }
            for track in tracks
        ]

    def get_playlist_tracks(self, playlist: str):
        tracks = []
        offset = 0
        while True:
            response = (
                self.client.playlist_tracks(playlist, offset=offset)
                if playlist != "liked"
                else self.client.current_user_saved_tracks(offset=offset)
            )
            tracks.extend(response["items"])
            if response["next"] is None:
                break
            offset += response["limit"]
        return self._organize_playlist_tracks(tracks)
