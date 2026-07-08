from pathlib import Path

from spotify_playlist_manager.state import (
    ManagedUnionPlaylist,
    ManagerState,
    load_state,
    save_state,
)


def test_state_round_trip(tmp_path: Path):
    state_path = tmp_path / "state.json"
    state = ManagerState(
        managed_playlists=[
            ManagedUnionPlaylist(
                playlist_id="playlist-1",
                source_playlist_ids=["source-1", "source-2"],
            )
        ]
    )

    save_state(state, state_path)

    assert load_state(state_path) == state