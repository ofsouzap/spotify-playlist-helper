# playlist-tool

Python CLI for managing Spotify playlist unions and diffs.

This README covers the `playlist-tool` component in the repository.

## Environment

The CLI reads Spotify credentials from environment variables. Supported names:

- `SPOTIPY_CLIENT_ID` or `SPOTIFY_CLIENT_ID`
- `SPOTIPY_CLIENT_SECRET` or `SPOTIFY_CLIENT_SECRET`
- `SPOTIPY_REDIRECT_URI` or `SPOTIFY_REDIRECT_URI`
- `SPOTIPY_CACHE_PATH` or `SPOTIFY_CACHE_PATH` (optional)

The authenticated Spotify account must have playlist read and modify permissions.

## Install

Create and activate a virtual environment first from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Then install the project in editable mode from the repository root:

```bash
pip install -e .
```

## Usage

Create a new playlist containing the union of tracks from source playlists:

```bash
spotify-playlist-helper create-union SOURCE_PLAYLIST_ID [SOURCE_PLAYLIST_ID ...]
```

If you omit `--description`, the tool generates one from the source playlist names.

Find playlists whose names contain a query string:

```bash
spotify-playlist-helper find-playlist-id QUERY
```

Show the tracks that would need to be added or removed to make a target playlist match the union:

```bash
spotify-playlist-helper diff TARGET_PLAYLIST_ID SOURCE_PLAYLIST_ID [SOURCE_PLAYLIST_ID ...]
```

For machine-readable output, use:

```bash
spotify-playlist-helper diff --output-format machine TARGET_PLAYLIST_ID SOURCE_PLAYLIST_ID [SOURCE_PLAYLIST_ID ...]
```

Human-readable diff output is the default.

Both commands ignore playlist ordering and dedupe tracks by Spotify track ID.