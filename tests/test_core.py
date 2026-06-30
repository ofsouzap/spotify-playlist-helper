from spotify_playlist_helper.core import (
    DiffTracksOutput,
    TrackInfo,
    diff_tracks,
    unique_tracks,
)


def test_unique_tracks_keeps_first_occurrence_only():
    tracks = [
        TrackInfo(uri="spotify:track:1", album="Album A", name="A", artists=["Artist"]),
        TrackInfo(
            uri="spotify:track:1",
            album="Album A",
            name="A duplicate",
            artists=["Artist"],
        ),
        TrackInfo(uri="spotify:track:2", album="Album B", name="B", artists=["Artist"]),
    ]

    assert unique_tracks(tracks) == [tracks[0], tracks[2]]


def test_diff_tracks_ignores_order_and_returns_set_difference():
    source_tracks = [
        TrackInfo(uri="spotify:track:1", album="Album A", name="A", artists=["Artist"]),
        TrackInfo(uri="spotify:track:2", album="Album B", name="B", artists=["Artist"]),
    ]
    target_tracks = [
        TrackInfo(uri="spotify:track:2", album="Album B", name="B", artists=["Artist"]),
        TrackInfo(uri="spotify:track:3", album="Album C", name="C", artists=["Artist"]),
    ]

    diff_output = diff_tracks(source_tracks, target_tracks)

    assert diff_output == DiffTracksOutput(
        to_add=[source_tracks[0]], to_remove=[target_tracks[1]]
    )
