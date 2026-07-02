"""Reusable command logic and output formatting for the playlist tool."""

from __future__ import annotations

from typing import Literal

from .core import (
    DiffTracksOutput,
    TrackInfo,
    diff_tracks,
    track_display_name,
    track_sort_key,
    unique_tracks,
)
from .spotify_client import (
    create_playlist_from_tracks,
    find_playlist_by_name_fragment,
    playlist_name,
    playlist_tracks,
)

OutputFormat = Literal["human", "machine"]


def resolve_union_tracks(
    sp_client, source_playlist_ids: tuple[str, ...]
) -> list[TrackInfo]:
    """Collect all source playlist tracks and return the deduplicated union."""
    collected: list[TrackInfo] = []
    for playlist_id in source_playlist_ids:
        collected.extend(playlist_tracks(sp_client, playlist_id))
    return sorted(unique_tracks(collected), key=track_sort_key)


def build_default_union_description(
    sp_client, source_playlist_ids: tuple[str, ...]
) -> str:
    """Build the default description for a union playlist from source names."""
    source_playlist_names = [
        playlist_name(sp_client, playlist_id) for playlist_id in source_playlist_ids
    ]
    return "This playlist is a union of the playlists: " + ", ".join(
        source_playlist_names
    )


def find_playlist_matches(sp_client, query: str):
    """Return playlists whose names contain the query string."""
    return find_playlist_by_name_fragment(sp_client, query)


def create_union_playlist(
    sp_client,
    source_playlist_ids: tuple[str, ...],
    name: str | None,
    description: str | None,
) -> dict:
    """Create a union playlist and return the created playlist."""
    union_tracks = resolve_union_tracks(sp_client, source_playlist_ids)
    created_playlist_name = (
        name or f"Union of {len(source_playlist_ids)} Spotify playlists"
    )
    playlist_description = description or build_default_union_description(
        sp_client, source_playlist_ids
    )
    playlist = create_playlist_from_tracks(
        sp_client,
        created_playlist_name,
        union_tracks,
        description=playlist_description,
    )
    return playlist


def calculate_diff_output(
    sp_client,
    target_playlist_id: str,
    source_playlist_ids: tuple[str, ...],
) -> DiffTracksOutput:
    """Calculate the tracks needed to transform the target into the union."""
    source_tracks = resolve_union_tracks(sp_client, source_playlist_ids)
    target_tracks = playlist_tracks(sp_client, target_playlist_id)
    return diff_tracks(source_tracks=source_tracks, target_tracks=target_tracks)


def format_diff_output_text(
    diff_output: DiffTracksOutput,
    output_format: OutputFormat,
) -> str:
    """Return the diff as a newline-delimited string for the requested format."""
    to_add = sorted(diff_output.to_add, key=track_sort_key)
    to_remove = sorted(diff_output.to_remove, key=track_sort_key)

    if output_format == "machine":
        return "\n".join(
            [
                *[f"+{track.uri} - {track.name}" for track in to_add],
                *[f"-{track.uri} - {track.name}" for track in to_remove],
            ]
        )

    elif output_format == "human":

        if to_add or to_remove:
            lines: list[str] = []

            if to_add:
                lines.append(f"Tracks to add: {len(to_add)}")
                lines.extend(
                    f"+ {track_display_name(track)} ({track.uri})" for track in to_add
                )

            if to_remove:
                lines.append(f"Tracks to remove: {len(to_remove)}")
                lines.extend(
                    f"- {track_display_name(track)} ({track.uri})"
                    for track in to_remove
                )

            return "\n".join(lines)

        else:
            return "Target playlist already matches the union."
