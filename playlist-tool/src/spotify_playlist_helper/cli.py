from __future__ import annotations

import click
from typing import Literal

from .core import (
    DiffTracksOutput,
    diff_tracks,
    track_display_name,
    track_sort_key,
    unique_tracks,
)
from .spotify_client import (
    build_spotify_client,
    create_playlist_from_tracks,
    find_playlist_by_name_fragment,
    playlist_name,
    playlist_tracks,
)

OutputFormat = Literal["human", "machine"]


def _resolve_union_tracks(sp_client, source_playlist_ids: tuple[str, ...]):
    collected = []
    for playlist_id in source_playlist_ids:
        collected.extend(playlist_tracks(sp_client, playlist_id))
    result = sorted(unique_tracks(collected), key=track_sort_key)
    return result


def _echo_diff_output_human(diff_output: DiffTracksOutput) -> None:
    to_add = sorted(diff_output.to_add, key=track_sort_key)
    to_remove = sorted(diff_output.to_remove, key=track_sort_key)

    if to_add or to_remove:
        if to_add:
            click.echo(f"Tracks to add: {len(to_add)}")
            for track in to_add:
                click.echo(f"+ {track_display_name(track)}")

        if to_remove:
            click.echo(f"Tracks to remove: {len(to_remove)}")
            for track in to_remove:
                click.echo(f"- {track_display_name(track)}")
    else:
        click.echo("Target playlist already matches the union.")


def _echo_diff_output_machine(diff_output: DiffTracksOutput) -> None:
    to_add = sorted(diff_output.to_add, key=track_sort_key)
    to_remove = sorted(diff_output.to_remove, key=track_sort_key)

    for track in to_add:
        click.echo(f"+{track.uri} - {track.name}")

    for track in to_remove:
        click.echo(f"-{track.uri} - {track.name}")


@click.group()
def cli() -> None:
    """Manage Spotify playlists by union and diff."""


@cli.command("find-playlist-id")
@click.argument("query")
def find_playlist_id_command(query: str) -> None:
    sp_client = build_spotify_client()
    playlist_matches = find_playlist_by_name_fragment(sp_client, query)
    if not playlist_matches:
        raise click.ClickException(f'No playlist found containing "{query}"')

    for playlist_match in playlist_matches:
        click.echo(f"{playlist_match.playlist_id} - {playlist_match.playlist_name}")


@cli.command("create-union")
@click.argument("source_playlist_ids", nargs=-1, required=True)
@click.option("--name", help="Name for the new playlist.")
@click.option(
    "--description",
    help=(
        "Optional description for the new playlist. If omitted, the description "
        "will be generated from the source playlist names."
    ),
)
def create_union_command(
    source_playlist_ids: tuple[str, ...], name: str | None, description: str | None
) -> None:
    sp_client = build_spotify_client()
    union_tracks = _resolve_union_tracks(sp_client, source_playlist_ids)
    created_playlist_name = (
        name or f"Union of {len(source_playlist_ids)} Spotify playlists"
    )
    source_playlist_names = [
        playlist_name(sp_client, playlist_id) for playlist_id in source_playlist_ids
    ]
    playlist_description = description or (
        "This playlist is a union of the playlists: " + ", ".join(source_playlist_names)
    )
    playlist = create_playlist_from_tracks(
        sp_client, created_playlist_name, union_tracks, description=playlist_description
    )

    click.echo(f"Created playlist: {playlist['external_urls']['spotify']}")
    click.echo(f"Track count: {len(union_tracks)}")


@cli.command("diff")
@click.argument("target_playlist_id")
@click.argument("source_playlist_ids", nargs=-1, required=True)
@click.option(
    "--output-format",
    type=click.Choice(["human", "machine"], case_sensitive=False),
    default="human",
    show_default=True,
    help="Choose human-readable or machine-readable diff output.",
)
def diff_command(
    target_playlist_id: str,
    source_playlist_ids: tuple[str, ...],
    output_format: OutputFormat,
) -> None:
    sp_client = build_spotify_client()
    source_tracks = _resolve_union_tracks(sp_client, source_playlist_ids)
    target_tracks = playlist_tracks(sp_client, target_playlist_id)
    diff_output = diff_tracks(
        source_tracks=source_tracks,
        target_tracks=target_tracks,
    )

    if output_format == "machine":
        print("Machine-readable diff output:")
        _echo_diff_output_machine(diff_output)
    else:
        print("Human-readable diff output:")
        _echo_diff_output_human(diff_output)
