"""
Tidal integration for Simple Balance Music.
Uses tidalapi for OAuth2 login and library access.
"""

import streamlit as st

try:
    import tidalapi
    HAS_TIDAL = True
except ImportError:
    tidalapi = None
    HAS_TIDAL = False


def is_available():
    """Check if tidalapi is installed."""
    return HAS_TIDAL


def get_session():
    """Get or create a Tidal session from Streamlit session state."""
    if not HAS_TIDAL:
        return None
    if "tidal_session" in st.session_state and st.session_state["tidal_session"]:
        session = st.session_state["tidal_session"]
        if session.check_login():
            return session
    return None


def start_login():
    """Start Tidal OAuth2 login flow. Returns (login_url, future) for device auth."""
    if not HAS_TIDAL:
        return None, None
    session = tidalapi.Session()
    login, future = session.login_oauth()
    st.session_state["tidal_login_future"] = future
    st.session_state["tidal_login_session"] = session
    return login, future


def complete_login():
    """Check if OAuth login has been completed by the user."""
    future = st.session_state.get("tidal_login_future")
    session = st.session_state.get("tidal_login_session")
    if not future or not session:
        return False
    try:
        future.result(timeout=1)
        st.session_state["tidal_session"] = session
        return True
    except Exception:
        return False


def get_favorites(session, limit=50):
    """Get user's favorite tracks."""
    if not session:
        return []
    try:
        favorites = session.user.favorites
        tracks = favorites.tracks(limit=limit)
        return [_track_to_dict(t) for t in tracks]
    except Exception as e:
        return [{"error": str(e)}]


def get_playlists(session):
    """Get user's playlists."""
    if not session:
        return []
    try:
        playlists = session.user.playlists()
        return [{"id": p.id, "name": p.name, "num_tracks": p.num_tracks, "description": getattr(p, "description", "")} for p in playlists]
    except Exception as e:
        return [{"error": str(e)}]


def get_playlist_tracks(session, playlist_id, limit=100):
    """Get tracks from a specific playlist."""
    if not session:
        return []
    try:
        playlist = session.playlist(playlist_id)
        tracks = playlist.tracks(limit=limit)
        return [_track_to_dict(t) for t in tracks]
    except Exception as e:
        return [{"error": str(e)}]


def search_tracks(session, query, limit=20):
    """Search Tidal for tracks."""
    if not session:
        return []
    try:
        results = session.search(query, models=[tidalapi.media.Track], limit=limit)
        return [_track_to_dict(t) for t in results.get("tracks", [])]
    except Exception as e:
        return [{"error": str(e)}]


def _track_to_dict(track):
    """Convert a tidalapi Track to a clean dictionary."""
    try:
        return {
            "id": track.id,
            "name": track.name,
            "artist": track.artist.name if track.artist else "Unknown",
            "album": track.album.name if track.album else "Unknown",
            "duration_sec": track.duration,
            "bpm": getattr(track, "bpm", None),
            "url": track.get_url() if hasattr(track, "get_url") else None,
        }
    except Exception:
        return {"name": str(track), "artist": "Unknown"}
