"""Reusable manager logic for checking recorded union playlists."""

from __future__ import annotations

from dataclasses import dataclass

from spotify_playlist_helper.core import DiffTracksOutput
from spotify_playlist_helper.playlist_tool import (
    OutputFormat,
    calculate_diff_output,
    format_diff_output_text,
)
from spotify_playlist_helper.spotify_client import playlist_name

from .state import ManagedUnionPlaylist, ManagerState


@dataclass(frozen=True, slots=True)
class ManagedUnionCheck:
    """The current status of one recorded union playlist."""

    playlist_id: str
    playlist_name: str
    diff_output: DiffTracksOutput


@dataclass(frozen=True, slots=True)
class NamedSourcePlaylist:
    """A source playlist ID paired with its current Spotify name."""

    playlist_id: str
    playlist_name: str


@dataclass(frozen=True, slots=True)
class NamedManagedPlaylist:
    """A managed target playlist and all of its named sources."""

    playlist_id: str
    playlist_name: str
    source_playlists: list[NamedSourcePlaylist]


def add_managed_playlist_state(
    state: ManagerState,
    target_playlist_id: str,
    source_playlist_ids: tuple[str, ...],
) -> ManagerState:
    """Return updated state that includes a new managed playlist."""

    if not source_playlist_ids:
        raise RuntimeError("Provide at least one source playlist ID.")

    if any(
        managed_playlist.playlist_id == target_playlist_id
        for managed_playlist in state.managed_playlists
    ):
        raise RuntimeError(
            f"A managed playlist with target ID '{target_playlist_id}' already exists."
        )

    return ManagerState(
        managed_playlists=[
            *state.managed_playlists,
            ManagedUnionPlaylist(
                playlist_id=target_playlist_id,
                source_playlist_ids=list(source_playlist_ids),
            ),
        ]
    )


def remove_managed_playlist_state(
    state: ManagerState,
    target_playlist_id: str,
) -> ManagerState:
    """Return updated state that removes one managed playlist."""

    if not any(
        managed_playlist.playlist_id == target_playlist_id
        for managed_playlist in state.managed_playlists
    ):
        raise RuntimeError(
            f"No managed playlist with target ID '{target_playlist_id}' was found."
        )

    return ManagerState(
        managed_playlists=[
            managed_playlist
            for managed_playlist in state.managed_playlists
            if managed_playlist.playlist_id != target_playlist_id
        ]
    )


def list_named_managed_playlists(
    sp_client,
    state: ManagerState,
) -> list[NamedManagedPlaylist]:
    """Resolve Spotify names for all managed playlists and their sources."""

    named_playlists: list[NamedManagedPlaylist] = []
    for managed_playlist in state.managed_playlists:
        source_playlists = [
            NamedSourcePlaylist(
                playlist_id=source_playlist_id,
                playlist_name=playlist_name(sp_client, source_playlist_id),
            )
            for source_playlist_id in managed_playlist.source_playlist_ids
        ]
        named_playlists.append(
            NamedManagedPlaylist(
                playlist_id=managed_playlist.playlist_id,
                playlist_name=playlist_name(sp_client, managed_playlist.playlist_id),
                source_playlists=source_playlists,
            )
        )
    return named_playlists


def calculate_managed_union_checks(
    sp_client,
    state: ManagerState,
) -> list[ManagedUnionCheck]:
    """Calculate the diff for every recorded union playlist."""

    checks: list[ManagedUnionCheck] = []
    for managed_playlist in state.managed_playlists:
        checks.append(
            ManagedUnionCheck(
                playlist_id=managed_playlist.playlist_id,
                playlist_name=playlist_name(sp_client, managed_playlist.playlist_id),
                diff_output=calculate_diff_output(
                    sp_client,
                    target_playlist_id=managed_playlist.playlist_id,
                    source_playlist_ids=tuple(managed_playlist.source_playlist_ids),
                ),
            )
        )
    return checks


def format_managed_union_check_text(
    managed_union_check: ManagedUnionCheck,
    output_format: OutputFormat,
) -> str:
    """Format one managed playlist check as a heading and diff block."""

    diff_text = format_diff_output_text(
        managed_union_check.diff_output,
        output_format,
    )
    heading = f"{managed_union_check.playlist_name} ({managed_union_check.playlist_id})"
    return heading if not diff_text else f"{heading}\n{diff_text}"


def format_managed_union_checks_text(
    managed_union_checks: list[ManagedUnionCheck],
    output_format: OutputFormat,
) -> str:
    """Format all managed playlist checks into a single block of text."""

    if not managed_union_checks:
        return "No managed union playlists recorded."

    return "\n\n".join(
        format_managed_union_check_text(check, output_format)
        for check in managed_union_checks
    )
