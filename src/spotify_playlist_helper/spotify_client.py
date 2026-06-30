from __future__ import annotations

import os
from collections.abc import Iterable
from dataclasses import dataclass
from collections.abc import Mapping

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from .core import TrackInfo, unique_tracks

DEFAULT_SCOPES = "playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public"


@dataclass(frozen=True, slots=True)
class _PlaylistItem:
    is_local: bool
    uri: str
    album: str
    name: str
    artists: list[str]

    @classmethod
    def from_spotify_dict(cls, value: object) -> "_PlaylistItem":
        if not isinstance(value, Mapping):
            raise RuntimeError("Spotify playlist item track was not a mapping")

        is_local = value.get("is_local")
        if not isinstance(is_local, bool):
            raise RuntimeError(
                "Spotify playlist item track did not include a valid is_local flag"
            )

        uri = value.get("uri")
        if not isinstance(uri, str) or not uri:
            raise RuntimeError(
                "Spotify playlist item track did not include a valid uri"
            )

        name = value.get("name")
        if not isinstance(name, str) or not name:
            raise RuntimeError(
                "Spotify playlist item track did not include a valid name"
            )

        raw_album = value.get("album")
        if not isinstance(raw_album, Mapping):
            raise RuntimeError("Spotify playlist item track did not include an album")

        album_name = raw_album.get("name")
        if not isinstance(album_name, str) or not album_name:
            raise RuntimeError(
                "Spotify playlist item track did not include a valid album name"
            )

        raw_artists = value.get("artists")
        if not isinstance(raw_artists, list):
            raise RuntimeError("Spotify playlist item track did not include artists")

        artists: list[str] = []
        for artist in raw_artists:
            if not isinstance(artist, Mapping):
                raise RuntimeError(
                    "Spotify playlist item track included a malformed artist"
                )

            artist_name = artist.get("name")
            if not isinstance(artist_name, str) or not artist_name:
                raise RuntimeError(
                    "Spotify playlist item track included an artist without a valid name"
                )

            artists.append(artist_name)

        return cls(
            is_local=is_local,
            uri=uri,
            album=album_name,
            name=name,
            artists=artists,
        )


@dataclass(frozen=True, slots=True)
class _PlaylistSearchResult:
    playlist_id: str
    playlist_name: str


def _read_env(*names: str, required: bool = False) -> str | None:
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    if required:
        joined = ", ".join(names)
        raise RuntimeError(
            f"Missing required environment variable. Set one of: {joined}"
        )
    return None


def build_spotify_client() -> spotipy.Spotify:
    client_id = _read_env("SPOTIPY_CLIENT_ID", "SPOTIFY_CLIENT_ID", required=True)
    client_secret = _read_env(
        "SPOTIPY_CLIENT_SECRET", "SPOTIFY_CLIENT_SECRET", required=True
    )
    redirect_uri = _read_env(
        "SPOTIPY_REDIRECT_URI", "SPOTIFY_REDIRECT_URI", required=True
    )
    cache_path = _read_env("SPOTIPY_CACHE_PATH", "SPOTIFY_CACHE_PATH")
    scopes = os.getenv("SPOTIFY_SCOPES", DEFAULT_SCOPES)

    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scopes,
        cache_path=cache_path,
        open_browser=True,
    )
    return spotipy.Spotify(auth_manager=auth_manager)


def _playlist_name_contains_query_case_insensitive(name: str, query: str) -> bool:
    return query.casefold() in name.casefold()


def _playlist_items(
    sp_client: spotipy.Spotify, playlist_id: str
) -> Iterable[_PlaylistItem]:
    response = sp_client.playlist_items(
        playlist_id,
        additional_types=("track",),
        limit=100,
        offset=0,
        fields="items(item(id,uri,name,album(name),artists(name),is_local)),next",
    )
    while True:
        if response is None:
            raise RuntimeError(
                f"Spotify did not return playlist items for playlist {playlist_id}"
            )

        items = response.get("items")
        if items is None:
            raise RuntimeError(
                f"Spotify playlist items response missing items for playlist {playlist_id}"
            )

        for item in items:
            track = item.get("item")
            if track:
                yield _PlaylistItem.from_spotify_dict(track)
        next_page = response.get("next")
        if not next_page:
            break
        response = sp_client.next(response)


def playlist_tracks(sp_client: spotipy.Spotify, playlist_id: str) -> list[TrackInfo]:
    tracks: list[TrackInfo] = []
    for track in _playlist_items(sp_client, playlist_id):
        if track.is_local:
            continue
        tracks.append(
            TrackInfo(
                uri=track.uri,
                album=track.album,
                name=track.name,
                artists=track.artists,
            )
        )
    return unique_tracks(tracks)


def find_playlist_by_name_fragment(
    sp_client: spotipy.Spotify, query: str
) -> list[_PlaylistSearchResult]:
    if not query:
        raise RuntimeError("Playlist search query cannot be empty")

    matches: list[_PlaylistSearchResult] = []
    response = sp_client.current_user_playlists(limit=50, offset=0)
    while True:
        if response is None:
            raise RuntimeError("Spotify did not return playlists for the current user")

        items = response.get("items")
        if items is None:
            raise RuntimeError("Spotify playlist response missing items")

        for playlist in items:
            if not isinstance(playlist, Mapping):
                continue

            playlist_name = playlist.get("name")
            playlist_id = playlist.get("id")
            if (
                isinstance(playlist_name, str)
                and isinstance(playlist_id, str)
                and _playlist_name_contains_query_case_insensitive(playlist_name, query)
            ):
                matches.append(
                    _PlaylistSearchResult(
                        playlist_id=playlist_id,
                        playlist_name=playlist_name,
                    )
                )

        next_page = response.get("next")
        if not next_page:
            break
        response = sp_client.next(response)

    return matches


def create_playlist_from_tracks(
    sp_client: spotipy.Spotify,
    name: str,
    tracks: list[TrackInfo],
    description: str = "",
) -> dict:
    playlist = sp_client.current_user_playlist_create(
        name=name,
        public=False,
        collaborative=False,
        description=description,
    )

    if playlist is None:
        raise RuntimeError("Spotify did not return the created playlist")

    playlist_id = playlist.get("id")
    if not playlist_id:
        raise RuntimeError("Spotify created playlist response did not include an id")

    uris = [track.uri for track in tracks]
    for start in range(0, len(uris), 100):
        sp_client.playlist_add_items(playlist_id, uris[start : start + 100])

    return playlist
