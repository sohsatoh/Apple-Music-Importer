import os
import re
import eyed3
from datetime import datetime
from apple_music_importer.utils import normalize

eyed3.log.setLevel("ERROR")


class MetadataHandler:
    @staticmethod
    def _get_mp3_metadata(file_path, artist_name_position, album_name_position):
        """Extract metadata from an MP3 file."""
        parent_dirs = os.path.dirname(file_path).split(os.sep)
        file_basename = os.path.basename(os.path.splitext(file_path)[0])
        clean_file_name = re.sub(
            r"^\d+\.?\s*", "", file_basename
        )  # Remove track number

        try:
            file = eyed3.load(file_path)
            if not file or not file.tag:
                raise ValueError("No metadata found")
            track = file.tag.title or clean_file_name
            artist = file.tag.artist or parent_dirs[artist_name_position]
            album = file.tag.album or parent_dirs[album_name_position]

        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            track = clean_file_name
            artist = (
                parent_dirs[artist_name_position]
                if len(parent_dirs) > artist_name_position
                else "Unknown Artist"
            )
            album = (
                parent_dirs[album_name_position]
                if len(parent_dirs) > album_name_position
                else "Unknown Album"
            )

        return (
            normalize(track),
            normalize(artist),
            normalize(album),
        )

    @staticmethod
    def get_track_list_from_files(paths, artist_name_position, album_name_position):
        """Build track dictionary from MP3 files in the given paths."""
        tracks = []
        for i, file in enumerate(paths):
            try:
                print(f"Processing audio tags: {i+1}/{len(paths)}...")
                filename = os.path.basename(file)
                track, artist, album = MetadataHandler._get_mp3_metadata(
                    file, artist_name_position, album_name_position
                )
                date_added = datetime.fromtimestamp(os.path.getctime(file)).isoformat()

                track_info = {
                    "title": track,
                    "artist": artist,
                    "album": album,
                    "local": {
                        "path": file,
                        "filename": filename,
                        "date_added": date_added,
                    },
                }
                tracks.append(track_info)
            except Exception as e:
                print(f"Error reading {file}: {e}")
                continue
        return tracks

    @staticmethod
    def save_metadata_to_mp3(file_path, title, artist, album):
        """Save metadata to an MP3 file with UTF-8 encoding."""
        try:
            file = eyed3.load(file_path)
            file.tag.title = title
            file.tag.artist = artist
            file.tag.album = album
            file.tag.save(version=eyed3.id3.ID3_DEFAULT_VERSION, encoding="utf-8")
            print(f"Metadata saved to {file_path}")
        except Exception as e:
            print(f"Error saving metadata to {file_path}: {e}")
