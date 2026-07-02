from __future__ import annotations

import click

from .playlist_tool import (
    OutputFormat,
    calculate_diff_output,
    create_union_playlist,
    find_playlist_matches,
    format_diff_output_text,
)
from .spotify_client import build_spotify_client


@click.group()
def cli() -> None:
    """Manage Spotify playlists by union and diff."""


@cli.command("find-playlist-id")
@click.argument("query")
def find_playlist_id_command(query: str) -> None:
    sp_client = build_spotify_client()
    playlist_matches = find_playlist_matches(sp_client, query)
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
    playlist = create_union_playlist(
        sp_client,
        source_playlist_ids,
        name=name,
        description=description,
    )
    click.echo(f"Created playlist: {playlist['external_urls']['spotify']}")


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
    diff_output = calculate_diff_output(
        sp_client,
        target_playlist_id=target_playlist_id,
        source_playlist_ids=source_playlist_ids,
    )
    output_text = format_diff_output_text(diff_output, output_format)
    if output_text:
        click.echo(output_text)
