from spotify_playlist_helper.core import DiffTracksOutput, TrackInfo
from spotify_playlist_helper.playlist_tool import format_diff_output_text


def test_format_diff_output_text_uses_track_uri_in_machine_output():
    diff_output = DiffTracksOutput(
        to_add=[
            TrackInfo(
                uri="spotify:track:abc123",
                album="Album A",
                name="Track A",
                artists=["Artist A"],
            )
        ],
        to_remove=[],
    )

    assert format_diff_output_text(diff_output, "machine") == "+spotify:track:abc123 - Track A"


def test_format_diff_output_text_preserves_non_track_uri():
    diff_output = DiffTracksOutput(
        to_add=[
            TrackInfo(
                uri="spotify:episode:xyz",
                album="Album A",
                name="Track A",
                artists=["Artist A"],
            )
        ],
        to_remove=[],
    )

    assert format_diff_output_text(diff_output, "human") == (
        "Tracks to add: 1\n"
        "+ Artist A - Track A (spotify:episode:xyz)"
    )