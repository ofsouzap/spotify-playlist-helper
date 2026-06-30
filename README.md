# spotify-playlist-helper

Python CLI for managing Spotify playlist unions and diffs.

## Environment

The CLI reads Spotify credentials from environment variables. Supported names:

- `SPOTIPY_CLIENT_ID` or `SPOTIFY_CLIENT_ID`
- `SPOTIPY_CLIENT_SECRET` or `SPOTIFY_CLIENT_SECRET`
- `SPOTIPY_REDIRECT_URI` or `SPOTIFY_REDIRECT_URI`
- `SPOTIPY_CACHE_PATH` or `SPOTIFY_CACHE_PATH` (optional)

The authenticated Spotify account must have playlist read and modify permissions.

## Install

Create and activate a virtual environment first:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Then install the project in editable mode:

```bash
pip install -e .
```

## Usage

Create a new playlist containing the union of tracks from source playlists:

```bash
spotify-playlist-helper create-union SOURCE_PLAYLIST_ID [SOURCE_PLAYLIST_ID ...]
```

Show the tracks that would need to be added or removed to make a target playlist match the union:

```bash
spotify-playlist-helper diff TARGET_PLAYLIST_ID SOURCE_PLAYLIST_ID [SOURCE_PLAYLIST_ID ...]
```

Both commands ignore playlist ordering and dedupe tracks by Spotify track ID.