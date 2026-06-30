from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TrackInfo:
    uri: str
    name: str
    artists: list[str]


@dataclass(frozen=True, slots=True)
class DiffTracksOutput:
    to_add: list[TrackInfo]
    to_remove: list[TrackInfo]


def unique_tracks(tracks: list[TrackInfo]) -> list[TrackInfo]:
    seen: set[str] = set()
    unique: list[TrackInfo] = []
    for track in tracks:
        if track.uri in seen:
            continue
        seen.add(track.uri)
        unique.append(track)
    return unique


def track_uri_set(tracks: list[TrackInfo]) -> set[str]:
    return {track.uri for track in tracks}


def track_sort_key(track: TrackInfo) -> tuple[str, str, str]:
    return (track.name.casefold(), ", ".join(track.artists).casefold(), track.uri)


def diff_tracks(
    source_tracks: list[TrackInfo],
    target_tracks: list[TrackInfo],
) -> DiffTracksOutput:
    source_uris = track_uri_set(source_tracks)
    target_uris = track_uri_set(target_tracks)

    to_add = [track for track in source_tracks if track.uri not in target_uris]
    to_remove = [track for track in target_tracks if track.uri not in source_uris]
    return DiffTracksOutput(to_add=to_add, to_remove=to_remove)


def track_display_name(track: TrackInfo) -> str:
    artist_text = ", ".join(track.artists)
    return f"{track.name} - {artist_text}" if artist_text else track.name
