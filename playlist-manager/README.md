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

List all managed playlists and their source playlists:

```bash
spotify-playlist-manager list --output-format human
spotify-playlist-manager list --output-format machine
```

List output includes both playlist names and IDs for targets and sources.

Add a managed union playlist to state:

```bash
spotify-playlist-manager create TARGET_PLAYLIST_ID SOURCE_PLAYLIST_ID [SOURCE_PLAYLIST_ID ...]
```

The command rejects duplicate target playlist IDs.

Delete a managed union playlist from state:

```bash
spotify-playlist-manager delete TARGET_PLAYLIST_ID
```

Delete requires confirmation and shows the playlist name in the prompt.
