from pathlib import Path

from click.testing import CliRunner

from spotify_playlist_manager.cli import cli
from spotify_playlist_manager.state import (
    ManagedUnionPlaylist,
    ManagerState,
    load_state,
    save_state,
)


def test_add_adds_managed_playlist(tmp_path: Path):
    state_path = tmp_path / "state.json"

    result = CliRunner().invoke(
        cli,
        [
            "add",
            "--state-path",
            str(state_path),
            "target-1",
            "source-1",
            "source-2",
        ],
    )

    assert result.exit_code == 0
    assert load_state(state_path) == ManagerState(
        managed_playlists=[
            ManagedUnionPlaylist(
                playlist_id="target-1",
                source_playlist_ids=["source-1", "source-2"],
            )
        ]
    )


def test_add_rejects_duplicate_target(tmp_path: Path):
    state_path = tmp_path / "state.json"
    save_state(
        ManagerState(
            managed_playlists=[
                ManagedUnionPlaylist(
                    playlist_id="target-1",
                    source_playlist_ids=["source-1"],
                )
            ]
        ),
        state_path,
    )

    result = CliRunner().invoke(
        cli,
        [
            "add",
            "--state-path",
            str(state_path),
            "target-1",
            "source-2",
        ],
    )

    assert result.exit_code != 0
    assert "already exists" in result.output


def test_remove_removes_managed_playlist_after_confirmation(
    tmp_path: Path,
    monkeypatch,
):
    state_path = tmp_path / "state.json"
    save_state(
        ManagerState(
            managed_playlists=[
                ManagedUnionPlaylist(
                    playlist_id="target-1",
                    source_playlist_ids=["source-1", "source-2"],
                ),
                ManagedUnionPlaylist(
                    playlist_id="target-2",
                    source_playlist_ids=["source-3"],
                ),
            ]
        ),
        state_path,
    )

    monkeypatch.setattr(
        "spotify_playlist_manager.cli.build_spotify_client",
        lambda: object(),
    )
    monkeypatch.setattr(
        "spotify_playlist_manager.cli.playlist_name",
        lambda _sp_client, _playlist_id: "Playlist One",
    )

    result = CliRunner().invoke(
        cli,
        ["remove", "--state-path", str(state_path), "target-1"],
        input="y\n",
    )

    assert result.exit_code == 0
    assert 'Remove managed playlist "Playlist One" (target-1)? [y/N]:' in result.output
    assert load_state(state_path) == ManagerState(
        managed_playlists=[
            ManagedUnionPlaylist(
                playlist_id="target-2",
                source_playlist_ids=["source-3"],
            )
        ]
    )


def test_list_human_shows_target_and_source_names(tmp_path: Path, monkeypatch):
    state_path = tmp_path / "state.json"
    save_state(
        ManagerState(
            managed_playlists=[
                ManagedUnionPlaylist(
                    playlist_id="target-1",
                    source_playlist_ids=["source-1", "source-2"],
                )
            ]
        ),
        state_path,
    )

    monkeypatch.setattr(
        "spotify_playlist_manager.cli.build_spotify_client",
        lambda: object(),
    )
    playlist_names = {
        "target-1": "Target Playlist",
        "source-1": "Source One",
        "source-2": "Source Two",
    }
    monkeypatch.setattr(
        "spotify_playlist_manager.manager.playlist_name",
        lambda _sp_client, playlist_id: playlist_names[playlist_id],
    )

    result = CliRunner().invoke(
        cli,
        ["list", "--state-path", str(state_path), "--output-format", "human"],
    )

    assert result.exit_code == 0
    assert "Target: Target Playlist (target-1)" in result.output
    assert "Sources (2):" in result.output
    assert "- Source One (source-1)" in result.output
    assert "- Source Two (source-2)" in result.output


def test_list_machine_shows_ids_and_names(tmp_path: Path, monkeypatch):
    state_path = tmp_path / "state.json"
    save_state(
        ManagerState(
            managed_playlists=[
                ManagedUnionPlaylist(
                    playlist_id="target-1",
                    source_playlist_ids=["source-1", "source-2"],
                )
            ]
        ),
        state_path,
    )

    monkeypatch.setattr(
        "spotify_playlist_manager.cli.build_spotify_client",
        lambda: object(),
    )
    playlist_names = {
        "target-1": "Target Playlist",
        "source-1": "Source One",
        "source-2": "Source Two",
    }
    monkeypatch.setattr(
        "spotify_playlist_manager.manager.playlist_name",
        lambda _sp_client, playlist_id: playlist_names[playlist_id],
    )

    result = CliRunner().invoke(
        cli,
        ["list", "--state-path", str(state_path), "--output-format", "machine"],
    )

    assert result.exit_code == 0
    assert "target-1\tTarget Playlist\tsource-1|source-2" in result.output
