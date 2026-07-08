# playlist-manager

Stateful companion CLI for tracking recorded Spotify union playlists.

## State file

By default, the manager stores its JSON state in `playlist-manager/state.json`.
That file is ignored by git and can be edited manually for now.

The JSON shape is:

```json
{
  "managed_playlists": [
    {
      "playlist_id": "spotify playlist id",
      "source_playlist_ids": ["source1", "source2"]
    }
  ]
}
```

## Install

From the repository root:

```bash
pip install -e .
```

## Usage

Check all recorded union playlists:

```bash
spotify-playlist-manager check
```

Use `--output-format machine` to get one diff line per change.
