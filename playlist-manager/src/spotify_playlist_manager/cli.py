"""Command-line interface for the playlist manager."""

from __future__ import annotations

from pathlib import Path

import click

from spotify_playlist_helper.playlist_tool import OutputFormat
from spotify_playlist_helper.spotify_client import build_spotify_client

from .manager import calculate_managed_union_checks, format_managed_union_checks_text
from .state import DEFAULT_STATE_PATH, load_state


@click.group()
def cli() -> None:
    """Manage recorded union playlists and report whether they are out of date."""


@cli.command("check")
@click.option(
    "--state-path",
    type=click.Path(path_type=Path),
    default=DEFAULT_STATE_PATH,
    show_default=True,
    help="Path to the JSON file that stores recorded union playlists.",
)
@click.option(
    "--output-format",
    type=click.Choice(["human", "machine"], case_sensitive=False),
    default="human",
    show_default=True,
    help="Choose human-readable or machine-readable diff output.",
)
def check_command(state_path: Path, output_format: OutputFormat) -> None:
    """Print diffs for every recorded union playlist."""

    sp_client = build_spotify_client()
    state = load_state(state_path)
    managed_union_checks = calculate_managed_union_checks(sp_client, state)
    click.echo(format_managed_union_checks_text(managed_union_checks, output_format))
