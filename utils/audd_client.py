"""
AudD Music Recognition Client — Simple Balance Music
Handles mix tracklist extraction via AudD Enterprise endpoint.
"""

import os
import time
import json
import requests
import streamlit as st


AUDD_API_URL = "https://enterprise.audd.io/"
AUDD_RECOGNIZE_URL = "https://api.audd.io/"
SPOTIFY_SEARCH_URL = "https://api.spotify.com/v1/search"


def get_api_token():
    """Get AudD API token from secrets or env."""
    try:
        return st.secrets.get("AUDD_API_TOKEN", os.environ.get("AUDD_API_TOKEN", ""))
    except Exception:
        return os.environ.get("AUDD_API_TOKEN", "")


def recognize_segment(audio_data, api_token=None):
    """Recognize a single audio segment using AudD main endpoint."""
    token = api_token or get_api_token()
    if not token:
        return {"error": "No AudD API token configured"}

    data = {
        "api_token": token,
        "return": "spotify,apple_music,deezer",
    }

    try:
        if isinstance(audio_data, str) and (audio_data.startswith("http") or audio_data.startswith("//")):
            data["url"] = audio_data
            response = requests.post(AUDD_RECOGNIZE_URL, data=data, timeout=30)
        else:
            files = {"file": ("segment.mp3", audio_data, "audio/mpeg")}
            response = requests.post(AUDD_RECOGNIZE_URL, data=data, files=files, timeout=30)

        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def extract_tracklist_enterprise(file_path=None, file_data=None, url=None, api_token=None):
    """
    Extract full tracklist from a DJ mix using AudD Enterprise endpoint.
    Accepts file path, file bytes, or URL. Returns list of identified tracks with timestamps.
    """
    token = api_token or get_api_token()
    if not token:
        return {"error": "No AudD API token configured", "tracks": []}

    data = {
        "api_token": token,
        "accurate_offsets": "true",
        "return": "spotify,apple_music,deezer",
        "skip": "2",
        "every": "5",
    }

    try:
        if url:
            data["url"] = url
            response = requests.post(AUDD_API_URL, data=data, timeout=300)
        elif file_path:
            with open(file_path, "rb") as f:
                files = {"file": ("mix.mp3", f, "audio/mpeg")}
                response = requests.post(AUDD_API_URL, data=data, files=files, timeout=300)
        elif file_data:
            files = {"file": ("mix.mp3", file_data, "audio/mpeg")}
            response = requests.post(AUDD_API_URL, data=data, files=files, timeout=300)
        else:
            return {"error": "No audio source provided", "tracks": []}

        response.raise_for_status()
        result = response.json()

        if "result" not in result:
            return {"error": result.get("error", {}).get("error_message", "Unknown error"), "tracks": []}

        return parse_enterprise_result(result["result"])

    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Mix may be too large for single upload.", "tracks": []}
    except Exception as e:
        return {"error": str(e), "tracks": []}


def parse_enterprise_result(results):
    """Parse AudD Enterprise response into clean tracklist."""
    if not results:
        return {"tracks": [], "raw_matches": 0}

    seen_tracks = {}
    raw_count = len(results)

    for match in results:
        if not match or "songs" not in match or not match["songs"]:
            continue

        song = match["songs"][0]
        offset = match.get("offset", 0)
        artist = song.get("artist", "Unknown")
        title = song.get("title", "Unknown")
        track_key = f"{artist}|{title}".lower()

        spotify_data = song.get("spotify", {})
        spotify_url = None
        spotify_id = None
        album_art = None
        is_unreleased = True

        if spotify_data:
            if isinstance(spotify_data, dict):
                spotify_url = spotify_data.get("external_urls", {}).get("spotify")
                spotify_id = spotify_data.get("id")
                album = spotify_data.get("album", {})
                images = album.get("images", [])
                if images:
                    album_art = images[0].get("url")
                is_unreleased = False
            elif isinstance(spotify_data, str):
                spotify_url = spotify_data
                is_unreleased = False

        apple_data = song.get("apple_music", {})
        apple_url = None
        if apple_data and isinstance(apple_data, dict):
            apple_url = apple_data.get("url")
            if apple_url:
                is_unreleased = False

        if track_key not in seen_tracks:
            seen_tracks[track_key] = {
                "artist": artist,
                "title": title,
                "first_offset": offset,
                "offsets": [offset],
                "spotify_url": spotify_url,
                "spotify_id": spotify_id,
                "apple_music_url": apple_url,
                "album_art": album_art,
                "unreleased": is_unreleased,
                "label": song.get("label", ""),
                "album": song.get("album", ""),
                "release_date": song.get("release_date", ""),
            }
        else:
            seen_tracks[track_key]["offsets"].append(offset)

    tracks = sorted(seen_tracks.values(), key=lambda t: t["first_offset"])

    for i, track in enumerate(tracks):
        track["position"] = i + 1
        track["timestamp"] = format_timestamp(track["first_offset"])

    return {
        "tracks": tracks,
        "raw_matches": raw_count,
        "unique_tracks": len(tracks),
    }


def format_timestamp(seconds):
    """Convert seconds to MM:SS or HH:MM:SS."""
    if isinstance(seconds, str) and ':' in seconds:
        return seconds
    seconds = int(float(seconds))
    if seconds >= 3600:
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h}:{m:02d}:{s:02d}"
    else:
        m = seconds // 60
        s = seconds % 60
        return f"{m:02d}:{s:02d}"


def format_tracklist_text(result):
    """Format tracklist as clean text output."""
    if not result.get("tracks"):
        return "No tracks identified."

    lines = []
    lines.append(f"TRACKLIST ({result['unique_tracks']} tracks identified)")
    lines.append("=" * 50)

    for track in result["tracks"]:
        unreleased_tag = " [UNRELEASED]" if track["unreleased"] else ""
        line = f"{track['timestamp']}  {track['artist']} - {track['title']}{unreleased_tag}"
        lines.append(line)

    lines.append("=" * 50)
    lines.append(f"Raw fingerprint matches: {result['raw_matches']}")

    return "\n".join(lines)


def format_tracklist_markdown(result):
    """Format tracklist as markdown for Streamlit display."""
    if not result.get("tracks"):
        return "No tracks identified."

    lines = []
    for track in result["tracks"]:
        unreleased = " `UNRELEASED`" if track["unreleased"] else ""
        spotify_link = f" [Spotify]({track['spotify_url']})" if track.get("spotify_url") else ""
        apple_link = f" [Apple]({track['apple_music_url']})" if track.get("apple_music_url") else ""
        links = f" {spotify_link}{apple_link}" if (spotify_link or apple_link) else ""

        lines.append(f"**{track['timestamp']}** — {track['artist']} — *{track['title']}*{unreleased}{links}")

    return "\n\n".join(lines)
