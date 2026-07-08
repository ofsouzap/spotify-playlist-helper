from spotify_playlist_helper.core import DiffTracksOutput, TrackInfo

from spotify_playlist_manager.manager import (
    ManagedUnionCheck,
    format_managed_union_check_text,
    format_managed_union_checks_text,
)


def test_format_managed_union_checks_text_reports_empty_state():
    assert format_managed_union_checks_text([], "human") == (
        "No managed union playlists recorded."
    )


def test_format_managed_union_check_text_sorts_machine_output():
    diff_output = DiffTracksOutput(
        to_add=[
            TrackInfo(
                uri="spotify:track:2",
                album="Album B",
                name="Beta",
                artists=["Artist B"],
            ),
            TrackInfo(
                uri="spotify:track:1",
                album="Album A",
                name="Alpha",
                artists=["Artist A"],
            ),
        ],
        to_remove=[
            TrackInfo(
                uri="spotify:track:4",
                album="Album D",
                name="Delta",
                artists=["Artist D"],
            ),
            TrackInfo(
                uri="spotify:track:3",
                album="Album C",
                name="Gamma",
                artists=["Artist C"],
            ),
        ],
    )

    check = ManagedUnionCheck(
        playlist_id="playlist-1",
        playlist_name="My playlist",
        diff_output=diff_output,
    )

    assert format_managed_union_check_text(check, "machine") == (
        "playlist-1 - My playlist\n"
        "+spotify:track:1 - Alpha\n"
        "+spotify:track:2 - Beta\n"
        "-spotify:track:3 - Gamma\n"
        "-spotify:track:4 - Delta"
    )