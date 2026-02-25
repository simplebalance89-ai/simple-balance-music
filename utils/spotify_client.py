"""
Spotify integration for Simple Balance Music.
Uses spotipy for OAuth2 login and library access.
"""

import streamlit as st

try:
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth
    HAS_SPOTIFY = True
except ImportError:
    spotipy = None
    HAS_SPOTIFY = False

SPOTIFY_CLIENT_ID = "a3fcdeaa8be54f2392bc3b88f849b6af"
SPOTIFY_CLIENT_SECRET = "33c2801c30314da38e4349404c22bb03"
SPOTIFY_REDIRECT_URI = "https://simple-balance-music.streamlit.app"
SPOTIFY_SCOPE = "user-library-read user-top-read playlist-read-private playlist-read-collaborative user-read-recently-played"


def is_available():
    return HAS_SPOTIFY


def get_auth_manager():
    """Get SpotifyOAuth manager for the login flow."""
    if not HAS_SPOTIFY:
        return None
    return SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=SPOTIFY_SCOPE,
        cache_handler=spotipy.cache_handler.MemoryCacheHandler(
            token_info=st.session_state.get("spotify_token_info")
        ),
        show_dialog=True,
    )


def get_client():
    """Get authenticated Spotify client from session state."""
    if not HAS_SPOTIFY:
        return None
    token_info = st.session_state.get("spotify_token_info")
    if not token_info:
        return None
    auth_manager = get_auth_manager()
    if auth_manager.is_token_expired(token_info):
        try:
            token_info = auth_manager.refresh_access_token(token_info["refresh_token"])
            st.session_state["spotify_token_info"] = token_info
        except Exception:
            st.session_state.pop("spotify_token_info", None)
            return None
    return spotipy.Spotify(auth=token_info["access_token"])


def handle_auth_callback():
    """Handle the OAuth callback — extract code from URL query params."""
    params = st.query_params
    code = params.get("code")
    if code:
        auth_manager = get_auth_manager()
        try:
            token_info = auth_manager.get_access_token(code, as_dict=True)
            st.session_state["spotify_token_info"] = token_info
            st.query_params.clear()
            return True
        except Exception:
            return False
    return False


def get_auth_url():
    """Get the Spotify authorization URL."""
    auth_manager = get_auth_manager()
    if auth_manager:
        return auth_manager.get_authorize_url()
    return None


def get_user_profile(client):
    """Get current user's profile."""
    try:
        return client.current_user()
    except Exception as e:
        return {"error": str(e)}


def get_top_tracks(client, time_range="medium_term", limit=20):
    """Get user's top tracks. time_range: short_term, medium_term, long_term."""
    try:
        results = client.current_user_top_tracks(limit=limit, time_range=time_range)
        return [_track_to_dict(t) for t in results.get("items", [])]
    except Exception as e:
        return [{"error": str(e)}]


def get_saved_tracks(client, limit=20):
    """Get user's saved/liked tracks."""
    try:
        results = client.current_user_saved_tracks(limit=limit)
        return [_track_to_dict(item["track"]) for item in results.get("items", [])]
    except Exception as e:
        return [{"error": str(e)}]


def get_playlists(client, limit=20):
    """Get user's playlists."""
    try:
        results = client.current_user_playlists(limit=limit)
        return [
            {
                "id": p["id"],
                "name": p["name"],
                "num_tracks": p["tracks"]["total"],
                "image": p["images"][0]["url"] if p.get("images") else None,
                "owner": p["owner"]["display_name"],
            }
            for p in results.get("items", [])
        ]
    except Exception as e:
        return [{"error": str(e)}]


def get_playlist_tracks(client, playlist_id, limit=50):
    """Get tracks from a specific playlist."""
    try:
        results = client.playlist_tracks(playlist_id, limit=limit)
        return [_track_to_dict(item["track"]) for item in results.get("items", []) if item.get("track")]
    except Exception as e:
        return [{"error": str(e)}]


def get_recently_played(client, limit=20):
    """Get recently played tracks."""
    try:
        results = client.current_user_recently_played(limit=limit)
        return [_track_to_dict(item["track"]) for item in results.get("items", [])]
    except Exception as e:
        return [{"error": str(e)}]


def get_audio_features(client, track_ids):
    """Get audio features (BPM, key, energy, danceability) for tracks."""
    try:
        features = client.audio_features(track_ids)
        return [
            {
                "id": f["id"],
                "bpm": round(f["tempo"], 1),
                "key": _key_number_to_name(f["key"], f["mode"]),
                "energy": f["energy"],
                "danceability": f["danceability"],
                "valence": f["valence"],
                "loudness": round(f["loudness"], 1),
                "duration_sec": f["duration_ms"] // 1000,
            }
            for f in features if f
        ]
    except Exception as e:
        return [{"error": str(e)}]


def search_tracks(client, query, limit=20):
    """Search Spotify for tracks."""
    try:
        results = client.search(q=query, type="track", limit=limit)
        return [_track_to_dict(t) for t in results["tracks"]["items"]]
    except Exception as e:
        return [{"error": str(e)}]


def _track_to_dict(track):
    """Convert a Spotify track dict to a clean dictionary."""
    try:
        artists = ", ".join(a["name"] for a in track.get("artists", []))
        return {
            "id": track["id"],
            "name": track["name"],
            "artist": artists,
            "album": track.get("album", {}).get("name", "Unknown"),
            "duration_sec": track.get("duration_ms", 0) // 1000,
            "preview_url": track.get("preview_url"),
            "image": track.get("album", {}).get("images", [{}])[0].get("url") if track.get("album", {}).get("images") else None,
        }
    except Exception:
        return {"name": str(track), "artist": "Unknown"}


def _key_number_to_name(key_num, mode):
    """Convert Spotify's key number (0-11) and mode (0=minor, 1=major) to key name."""
    if key_num < 0:
        return "?"
    keys = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    key_name = keys[key_num]
    if mode == 0:
        key_name += "m"
    return key_name
