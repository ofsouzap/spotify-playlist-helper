from __future__ import annotations

import click

from .core import diff_tracks, track_display_name, track_sort_key, unique_tracks
from .spotify_client import (
    build_spotify_client,
    create_playlist_from_tracks,
    find_playlist_by_name_fragment,
    playlist_tracks,
)


def _resolve_union_tracks(sp_client, source_playlist_ids: tuple[str, ...]):
    collected = []
    for playlist_id in source_playlist_ids:
        collected.extend(playlist_tracks(sp_client, playlist_id))
    result = sorted(unique_tracks(collected), key=track_sort_key)
    return result


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
    "--description", default="Created by spotify-playlist-helper", show_default=True
)
def create_union_command(
    source_playlist_ids: tuple[str, ...], name: str | None, description: str
) -> None:
    sp_client = build_spotify_client()
    union_tracks = _resolve_union_tracks(sp_client, source_playlist_ids)
    playlist_name = name or f"Union of {len(source_playlist_ids)} Spotify playlists"
    playlist = create_playlist_from_tracks(
        sp_client, playlist_name, union_tracks, description=description
    )

    click.echo(f"Created playlist: {playlist['external_urls']['spotify']}")
    click.echo(f"Track count: {len(union_tracks)}")


@cli.command("diff")
@click.argument("target_playlist_id")
@click.argument("source_playlist_ids", nargs=-1, required=True)
def diff_command(target_playlist_id: str, source_playlist_ids: tuple[str, ...]) -> None:
    sp_client = build_spotify_client()
    source_tracks = _resolve_union_tracks(sp_client, source_playlist_ids)
    target_tracks = playlist_tracks(sp_client, target_playlist_id)
    diff_output = diff_tracks(source_tracks, target_tracks)
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
