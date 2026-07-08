"""JSON state handling for the playlist manager."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

DEFAULT_STATE_PATH = Path(__file__).resolve().parents[2] / "state.json"


@dataclass(frozen=True, slots=True)
class ManagedUnionPlaylist:
    """A stored union playlist and the playlists used to build it."""

    playlist_id: str
    source_playlist_ids: list[str]


@dataclass(frozen=True, slots=True)
class ManagerState:
    """All union playlists tracked by the manager."""

    managed_playlists: list[ManagedUnionPlaylist]


def _validate_string_list(values: object, field_name: str) -> list[str]:
    if not isinstance(values, list):
        raise RuntimeError(f"Manager state field '{field_name}' must be a list")

    validated_values: list[str] = []
    for value in values:
        if not isinstance(value, str) or not value:
            raise RuntimeError(
                f"Manager state field '{field_name}' must contain non-empty strings"
            )
        validated_values.append(value)
    return validated_values


def load_state(state_path: Path = DEFAULT_STATE_PATH) -> ManagerState:
    """Load the manager state from JSON, or return an empty state if missing."""

    if not state_path.exists():
        return ManagerState(managed_playlists=[])

    payload = json.loads(state_path.read_text())
    raw_managed_playlists = payload.get("managed_playlists", [])
    if not isinstance(raw_managed_playlists, list):
        raise RuntimeError("Manager state field 'managed_playlists' must be a list")

    managed_playlists: list[ManagedUnionPlaylist] = []
    for item in raw_managed_playlists:
        if not isinstance(item, dict):
            raise RuntimeError("Each managed playlist entry must be a JSON object")

        playlist_id = item.get("playlist_id")
        if not isinstance(playlist_id, str) or not playlist_id:
            raise RuntimeError("Managed playlist entries must include a playlist_id")

        source_playlist_ids = _validate_string_list(
            item.get("source_playlist_ids"), "source_playlist_ids"
        )
        managed_playlists.append(
            ManagedUnionPlaylist(
                playlist_id=playlist_id,
                source_playlist_ids=source_playlist_ids,
            )
        )

    return ManagerState(managed_playlists=managed_playlists)


def save_state(state: ManagerState, state_path: Path = DEFAULT_STATE_PATH) -> None:
    """Persist the manager state to JSON."""

    payload = {
        "managed_playlists": [
            {
                "playlist_id": managed_playlist.playlist_id,
                "source_playlist_ids": managed_playlist.source_playlist_ids,
            }
            for managed_playlist in state.managed_playlists
        ]
    }
    state_path.write_text(json.dumps(payload, indent=2) + "\n")
