"""Command-line interface for the playlist manager."""

from __future__ import annotations

from typing import Iterable
from pathlib import Path

import click

from spotify_playlist_helper.playlist_tool import OutputFormat
from spotify_playlist_helper.spotify_client import build_spotify_client, playlist_name

from .manager import (
    calculate_managed_union_checks,
    add_managed_playlist_state,
    remove_managed_playlist_state,
    format_managed_union_checks_text,
    list_named_managed_playlists,
    NamedManagedPlaylist,
)
from .state import DEFAULT_STATE_PATH, load_state, save_state


def _format_list_output_human(
    named_managed_playlists: Iterable[NamedManagedPlaylist],
) -> str:
    if not named_managed_playlists:
        return "No managed union playlists recorded."

    blocks: list[str] = []
    for managed_playlist in named_managed_playlists:
        source_lines = [
            f"- {source_playlist.playlist_name} ({source_playlist.playlist_id})"
            for source_playlist in managed_playlist.source_playlists
        ]
        block_lines = [
            f"Target: {managed_playlist.playlist_name} ({managed_playlist.playlist_id})",
            f"Sources ({len(source_lines)}):",
            *source_lines,
        ]
        blocks.append("\n".join(block_lines))
    return "\n\n".join(blocks)


def _format_list_output_machine(
    named_managed_playlists: Iterable[NamedManagedPlaylist],
) -> str:
    lines: list[str] = []

    for managed_playlist in named_managed_playlists:
        source_entries = [
            source_playlist.playlist_id
            for source_playlist in managed_playlist.source_playlists
        ]
        lines.append(
            f"{managed_playlist.playlist_id}\t{managed_playlist.playlist_name}\t"
            f"{'|'.join(source_entries)}"
        )

    return "\n".join(lines)


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


@cli.command("list")
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
    help="Choose human-readable or machine-readable list output.",
)
def list_command(state_path: Path, output_format: OutputFormat) -> None:
    """List recorded managed playlists and their source playlists."""

    state = load_state(state_path)
    sp_client = build_spotify_client()
    named_managed_playlists = list_named_managed_playlists(sp_client, state)
    if output_format == "machine":
        output_text = _format_list_output_machine(named_managed_playlists)
    else:
        output_text = _format_list_output_human(named_managed_playlists)
    click.echo(output_text)


@cli.command("add")
@click.option(
    "--state-path",
    type=click.Path(path_type=Path),
    default=DEFAULT_STATE_PATH,
    show_default=True,
    help="Path to the JSON file that stores recorded union playlists.",
)
@click.argument("target_playlist_id")
@click.argument("source_playlist_ids", nargs=-1)
def add_command(
    state_path: Path,
    target_playlist_id: str,
    source_playlist_ids: tuple[str, ...],
) -> None:
    """Record a managed union playlist in state."""

    state = load_state(state_path)
    try:
        updated_state = add_managed_playlist_state(
            state,
            target_playlist_id,
            source_playlist_ids,
        )
    except RuntimeError as exc:
        raise click.ClickException(str(exc)) from exc
    save_state(updated_state, state_path)
    click.echo(
        f"Recorded managed playlist '{target_playlist_id}' with "
        f"{len(source_playlist_ids)} source playlist(s)."
    )


@cli.command("remove")
@click.option(
    "--state-path",
    type=click.Path(path_type=Path),
    default=DEFAULT_STATE_PATH,
    show_default=True,
    help="Path to the JSON file that stores recorded union playlists.",
)
@click.argument("target_playlist_id")
def remove_command(state_path: Path, target_playlist_id: str) -> None:
    """Remove a recorded managed union playlist from state."""

    state = load_state(state_path)
    try:
        updated_state = remove_managed_playlist_state(state, target_playlist_id)
    except RuntimeError as exc:
        raise click.ClickException(str(exc)) from exc

    sp_client = build_spotify_client()
    target_playlist_name = playlist_name(sp_client, target_playlist_id)
    if click.confirm(
        (
            f'Remove managed playlist "{target_playlist_name}" '
            f"({target_playlist_id})?"
        )
    ):
        save_state(updated_state, state_path)
        click.echo(
            f"Removed managed playlist '{target_playlist_name}' ({target_playlist_id})."
        )
