# Apple Music Importer

Apple Music Importer is a tool designed to import music from multiple sources, including local files and Spotify playlists, into Apple Music. By analyzing metadata from various sources, it searches for matching tracks via the Apple Music API, providing an efficient way to integrate your music collection.

## Disclaimer

This tool was developed for personal use and is not officially supported. Functionality is not guaranteed, and the author assumes no responsibility for any issues or damages resulting from its use. Use it at your own discretion.

The code was written primarily out of necessity and may not be the most polished. Future refactoring may occur, but for now, expect a somewhat unrefined implementation.

## Installation

To use Apple Music Importer, you need Python 3.7 or higher. Follow the steps below to install:

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

### Global Options

- `--request-headers` (required): Path to the JSON file containing request headers for the Apple Music API
- `--track-list`: Path to a file containing track information (useful for resuming imports)
- `--country-code`: Country code for Apple Music search (default: US)
- `--limit`: Number of search results to retrieve (default: 3)
- `--require-confirm`: Requires confirmation for artist name mismatches (skips automatically if not set)

## Requirements

### Apple Music API Request Headers

To interact with the Apple Music API, you must obtain an API key and required headers. These are used with the `-rh, --request-headers` option.

#### Steps to Retrieve API Headers

1. Open [Apple Music](https://music.apple.com/new) in a web browser.
2. Open Developer Tools and navigate to the **Network** tab.
3. Perform a search or an action that triggers an Apple Music API request.
4. Right-click on the request and select **Copy as cURL**.
5. Use a tool like [cURL Converter](https://curlconverter.com/) to extract the request headers as JSON.

### Spotify OAuth Client

For Spotify integration, you need to register an application as a Spotify Developer and obtain OAuth credentials. These values are set as environment variables.

Follow the instructions at [Spotipy Authorization Code Flow](https://spotipy.readthedocs.io/en/2.11.1/#authorization-code-flow).

## Modes of Operation

Apple Music Importer supports multiple modes to import and synchronize music tracks efficiently.

### Local Mode

This mode scans local music files and attempts to match them with tracks available on Apple Music. If a match isn't found, you can optionally edit the metadata interactively.

#### Options

- `FOLDER_PATH`: Path to the folder containing music files
- `--artist-name-position`: Index of the artist name in the file path (default: -2)
- `--album-name-position`: Index of the album name in the file path (default: -1)
- `--allow-edit`: Enables interactive editing of MP3 metadata for unmatched tracks (default: False)

### Spotify Mode

This mode imports tracks from a specified Spotify playlist, searching for corresponding tracks on Apple Music.

#### Options

- `PLAYLIST_ID`: Spotify playlist ID to import

### Sync Mode

This mode synchronizes tracks from both local files and Spotify with Apple Music. You can add synced tracks to your Apple Music Library and/or create playlists.

#### Options

- `--request-headers` (required): Path to the JSON file containing request headers for the Apple Music API
- `--track-list`: Path to a file containing track information (useful for resuming imports)
- `--country-code`: Country code for Apple Music search (default: US)
- `--limit`: Number of search results to retrieve (default: 3)
- `--require-confirm`: Requires confirmation for artist name mismatches (skips automatically if not set)

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
