# Apple Music Importer

Apple Music Importer is a tool to import local music files into Apple Music. This tool reads the metadata of music files and searches for corresponding tracks using the Apple Music API.

## Disclaimer

This tool was created for personal use and is not officially supported. There are no guarantees regarding its functionality, and the author assumes no responsibility for any issues or damages that may arise from its use. Use it at your own risk.

Additionally, the code was written out of necessity, so it may not be the most readable. If time permits, I might refactor it on a whim, but for now, expect it to be somewhat messy.

## Installation

To use this tool, you need Python 3.7 or higher. Follow the steps below to install it.

```sh
git clone https://github.com/sohsatoh/Apple-Music-Importer.git
cd apple-music-importer
pip install -r requirements.txt
python ./setup.py install
```

## Usage

### Command Line Interface (CLI)

```sh
apple-music-importer [OPTIONS] COMMAND [ARGS]...
```

### Mode-independent Options

- `-rh, --request-headers`: Path to the JSON file containing the request headers for the Apple Music API (required)
- `-tl, --track-list`: Path to the file containing track info (resume from this file if specified)
- `-c, --country-code`: Country code for Apple Music search (default: US)
- `-l, --limit`: Number of search results to retrieve (default: 3)
- `--require-confirm`: Require confirmation for artist name mismatch (skips automatically if not set)

### Requirements

### Request headers for Apple Music API

To use the Apple Music API, you need to obtain the API key and other necessary information from the response headers.
This is used with the `-rh, --request-headers` option.

### Steps

1. Open [https://music.apple.com/new](https://music.apple.com/new) in Chrome or another browser.
2. Open the Developer Tools and go to the **Network** tab.
3. Perform a search or any action that triggers a request to the Apple Music API.
4. Right-click on the request and select **Copy as cURL**.
5. Use a tool like [https://curlconverter.com/](https://curlconverter.com/) to convert the cURL command into Python code or extract the request headers as JSON.

### Spotify OAuth Client

To access the Spotify API, you need to register an application as a Spotify Developer. (This is not a particularly complicated process.)

These values will be used as environment variables.

Follow the instructions on the following page:

<https://spotipy.readthedocs.io/en/2.11.1/#authorization-code-flow>

## Modes

This tool saves track information to a file using the local and spotify modes.
Finally, you can use the sync mode to merge this information and synchronize it with Apple Music.

### Local Mode

The `local` mode allows you to search for local music files in Apple Music. It reads the metadata of the music files and searches for corresponding tracks using the Apple Music API. If the track is not found, you can optionally edit the metadata interactively.

#### Mode-dependent Options

- `FOLDER_PATH`: Path to the folder containing music files
- `-ap, --artist-name-position`: Position of the artist name in the file path (default: -2)
- `-al, --album-name-position`: Position of the album name in the file path (default: -1)
- `--allow-edit`: Edit MP3 tag metadata interactively (only if the song is not found in Apple Music) (default: False)

### Spotify Mode

The `spotify` mode allows you to import tracks from a Spotify playlist into Apple Music. It reads the metadata of the tracks in the Spotify playlist and searches for corresponding tracks using the Apple Music API.

#### Mode-dependent Options

- `PLAYLIST_ID`: Spotify playlist ID to import tracks from

### Sync Mode

The `sync` mode allows you to sync tracks from Spotify and local files with Apple Music. You can choose to add the synced tracks to the Apple Music Library and/or create playlists with the synced tracks.

#### Mode-dependent Options

- `--delete-all`: Delete all tracks in the Apple Music Cloud Library (except for Apple Music tracks)
- `--spotify`: Sync tracks from Spotify
- `--local`: Sync tracks from local files
- `--create-playlist`: Create a playlist with the synced tracks (Each source will create a separate playlist)
- `--add-to-library`: Add the synced tracks to the Apple Music Library

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
