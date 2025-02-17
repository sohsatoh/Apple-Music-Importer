import urllib.parse
import re
from apple_music_importer.session import UnauthorizedRequestException


class AppleMusicAPI:
    def __init__(self, session_handler, country_code, limit=1):
        self.session_handler = session_handler
        self.country_code = country_code
        self.limit = limit
        self.base_url = f"https://amp-api.music.apple.com"
        self.catalog_base_url = f"{self.base_url}/v1/catalog/{country_code}"

    def add_tracks_to_library(self, music_id_list):
        queries = {
            "format[resources]": "map",
            "ids[songs]": ",".join(music_id_list),
            "representation": "ids",
        }
        query = urllib.parse.urlencode(queries, quote_via=urllib.parse.quote)
        url = f"{self.base_url}/v1/me/library?{query}"
        response_json = self.session_handler.post(url)
        return response_json

    def create_playlist(self, name, music_id_list=[]):
        url = f"{self.base_url}/v1/me/library/playlists"
        data = {
            "attributes": {
                "name": name,
                "description": "",
                "isPublic": False,
            },
            "relationships": {
                "tracks": {
                    "data": [
                        {"id": music_id, "type": "songs"} for music_id in music_id_list
                    ]
                }
            },
        }
        response_json = self.session_handler.post(url, data)
        return response_json

    def get_my_library(self):
        url = f"{self.base_url}/me/library/songs"
        all_songs = []
        while True:
            queries = {
                "format[resources]": "map",
                "include[library-songs]": "catalog",
                "limit": "100",
                "meta": "sorts",
                "platform": "web",
                "sort": "name",
            }
            if "?" in url:
                url = f"{url}&{urllib.parse.urlencode(queries, quote_via=urllib.parse.quote)}"
            else:
                url = f"{url}?{urllib.parse.urlencode(queries, quote_via=urllib.parse.quote)}"
            response_json = self.session_handler.get(url)
            all_songs.extend(response_json.get("data", []))
            next_url = response_json.get("next")
            if not next_url:
                break
            url = next_url
        return all_songs

    def search_track_by_isrc(self, isrc):
        queries = {"filter[isrc]": isrc}
        query = urllib.parse.urlencode(queries, quote_via=urllib.parse.quote)
        url = f"{self.catalog_base_url}/songs?{query}"
        response_json = self.session_handler.get(url)
        try:
            return response_json.get("data", [])[0].get("attributes", {}).values()
        except IndexError:
            print(f"Track with ISRC {isrc} not found.")
            return None

    def _search_by_term(self, term):
        """Execute a search request to the Apple Music API."""
        queries = {
            "art[music-videos:url]": "c",
            "art[url]": "f",
            "extend": "artistUrl",
            "fields[albums]": "artistName,artistUrl,name,playParams,releaseDate,url",
            "fields[artists]": "url,name",
            "format[resources]": "map",
            "include[albums]": "artists",
            "include[music-videos]": "artists",
            "include[songs]": "artists",
            "include[stations]": "radio-show",
            "limit": self.limit,
            "omit[resource]": "autos",
            "platform": "web",
            "relate[albums]": "artists",
            "relate[songs]": "albums",
            "term": term,
            "types": "activities,albums,apple-curators,artists,curators,editorial-items,music-movies,music-videos,playlists,record-labels,songs,stations,tv-episodes,uploaded-videos",
            "with": "lyricHighlights,lyrics,naturalLanguage,serverBubbles,subtitles",
        }
        query = urllib.parse.urlencode(queries, quote_via=urllib.parse.quote)
        url = f"{self.catalog_base_url}/search?{query}"
        response_json = self.session_handler.get(url)
        return response_json.get("resources", {}).get("songs", {}).values()

    def search_track_from_text(self, title, artist, album, require_confirm):
        """Search for a track on Apple Music."""
        title_without_supplement = re.sub(
            r"\s(feat.*|((（|\()(?!.*\b(?:instrumental)\b.*$).*?(instrumental)?.*?(）|\))))",
            r" \4",
            title,
        ).strip()
        title_without_supplement_and_symbols = re.sub(
            r"\s+", " ", re.sub(r"[^\w\s]", " ", title_without_supplement)
        ).strip()

        query_patterns = [
            (
                f"{title} {artist} {album}",
                "title_artist_album",
            ),
            (f"{title} {artist}", "title_artist"),
            (
                f"{title_without_supplement} {artist}",
                "title-without-supp_artist",
            ),
            (
                f"{title_without_supplement_and_symbols} {artist}",
                "title-without-supp-and-symbols_artist",
            ),
            (title_without_supplement_and_symbols, "title"),
        ]

        try:
            for query, match_type in query_patterns:
                results = self._search_by_term(query)
                for result in results:
                    if match_type == "title" and not self._check_artist_name(
                        title, album, artist, result, require_confirm
                    ):
                        continue
                    result["match_type"] = match_type
                    return result
            return None
        except UnauthorizedRequestException:
            raise
        except Exception as e:
            print(f"Error searching for {title} by {artist}: {e}")
            return None

    def _check_artist_name(self, title, artist, album, result, require_confirm=False):
        """Check if the artist name matches in the result."""
        if (
            artist.lower() not in result["attributes"]["artistName"].lower()
            and require_confirm
        ):
            user_input = input(
                f"Artist name mismatch: {artist} vs {result['attributes']['artistName']}.\n"
                f"Title: {title} / {result['attributes']['name']}\n"
                f"Album: {album} / {result['attributes']['albumName']}\nDo you want to add it? (Y/n): "
            ).lower()
            return user_input == "y"
        return False
