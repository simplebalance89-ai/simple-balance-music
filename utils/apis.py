"""External API integrations for Simple Balance Music."""

import requests
import streamlit as st
from datetime import datetime, timedelta


# --- EDMTrain API ---
def get_edmtrain_events(city: str = "Los Angeles", days_ahead: int = 30) -> list:
    """Fetch upcoming EDM events from EDMTrain."""
    api_key = st.secrets.get("EDMTRAIN_API_KEY", "")
    if not api_key:
        return _mock_edmtrain_events(city)

    url = "https://edmtrain.com/api/events"
    params = {
        "client": api_key,
        "state": "California" if city in ["Los Angeles", "LA"] else None,
        "city": city,
    }
    try:
        resp = requests.get(url, params={k: v for k, v in params.items() if v}, timeout=10)
        if resp.status_code == 200:
            return resp.json().get("data", [])
    except Exception:
        pass
    return _mock_edmtrain_events(city)


def _mock_edmtrain_events(city: str) -> list:
    """Demo events when no API key configured."""
    today = datetime.now()
    return [
        {
            "name": "Afterlife presents Tale of Us",
            "venue": {"name": "BMO Stadium", "location": city},
            "date": (today + timedelta(days=14)).strftime("%Y-%m-%d"),
            "ages": "21+",
            "artists": [{"name": "Tale of Us"}, {"name": "Colyn"}, {"name": "Anyma"}],
            "link": "https://edmtrain.com",
        },
        {
            "name": "This Never Happened: Lane 8",
            "venue": {"name": "The Shrine Auditorium", "location": city},
            "date": (today + timedelta(days=21)).strftime("%Y-%m-%d"),
            "ages": "18+",
            "artists": [{"name": "Lane 8"}, {"name": "Township Rebellion"}],
            "link": "https://edmtrain.com",
        },
        {
            "name": "Drumcode: Adam Beyer",
            "venue": {"name": "Exchange LA", "location": city},
            "date": (today + timedelta(days=7)).strftime("%Y-%m-%d"),
            "ages": "21+",
            "artists": [{"name": "Adam Beyer"}, {"name": "Amelie Lens"}],
            "link": "https://edmtrain.com",
        },
        {
            "name": "Day Zero: Melodic Edition",
            "venue": {"name": "Academy LA", "location": city},
            "date": (today + timedelta(days=10)).strftime("%Y-%m-%d"),
            "ages": "21+",
            "artists": [{"name": "Glowal"}, {"name": "Upercent"}],
            "link": "https://edmtrain.com",
        },
        {
            "name": "Desert Hearts Festival Pre-Party",
            "venue": {"name": "Sound Nightclub", "location": city},
            "date": (today + timedelta(days=5)).strftime("%Y-%m-%d"),
            "ages": "21+",
            "artists": [{"name": "Lee Burridge"}, {"name": "Mikey Lion"}],
            "link": "https://edmtrain.com",
        },
    ]


# --- Bandsintown API ---
def get_bandsintown_events(artist: str) -> list:
    """Fetch upcoming events for an artist from Bandsintown."""
    app_id = st.secrets.get("BANDSINTOWN_APP_ID", "")
    if not app_id:
        return []

    url = f"https://rest.bandsintown.com/artists/{artist}/events"
    params = {"app_id": app_id}
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return []


# --- Last.fm API ---
def get_lastfm_trending(tag: str = "electronic", limit: int = 20) -> list:
    """Get trending tracks for a tag from Last.fm."""
    api_key = st.secrets.get("LASTFM_API_KEY", "")
    if not api_key:
        return _mock_lastfm_trending(tag)

    url = "http://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "tag.gettoptracks",
        "tag": tag,
        "api_key": api_key,
        "format": "json",
        "limit": limit,
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("tracks", {}).get("track", [])
    except Exception:
        pass
    return _mock_lastfm_trending(tag)


def _mock_lastfm_trending(tag: str) -> list:
    """Demo trending tracks."""
    return [
        {"name": "Oxygen Levels Low", "artist": {"name": "Colyn"}, "playcount": "2450000"},
        {"name": "Trigger Your Sense", "artist": {"name": "Glowal"}, "playcount": "1800000"},
        {"name": "Reality", "artist": {"name": "Tim Engelhardt"}, "playcount": "1200000"},
        {"name": "Crazy", "artist": {"name": "Philip Bader"}, "playcount": "980000"},
        {"name": "Ghost Dance", "artist": {"name": "Brunello"}, "playcount": "850000"},
        {"name": "Afterglow", "artist": {"name": "Township Rebellion"}, "playcount": "750000"},
        {"name": "Parallels", "artist": {"name": "Upercent"}, "playcount": "620000"},
        {"name": "Dawn Patrol", "artist": {"name": "Lane 8"}, "playcount": "540000"},
    ]


def search_lastfm_artist(artist: str) -> dict:
    """Search for artist info on Last.fm."""
    api_key = st.secrets.get("LASTFM_API_KEY", "")
    if not api_key:
        return {}

    url = "http://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "artist.getinfo",
        "artist": artist,
        "api_key": api_key,
        "format": "json",
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            return resp.json().get("artist", {})
    except Exception:
        pass
    return {}


# --- MusicBrainz API ---
def search_musicbrainz(query: str, entity: str = "recording", limit: int = 10) -> list:
    """Search MusicBrainz for tracks/artists/releases."""
    headers = {"User-Agent": st.secrets.get("MUSICBRAINZ_USER_AGENT", "SimpleBalanceMusic/1.0")}
    url = f"https://musicbrainz.org/ws/2/{entity}/"
    params = {"query": query, "fmt": "json", "limit": limit}
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return data.get(f"{entity}s", data.get(entity, []))
    except Exception:
        pass
    return []


# --- Beatport API v4 ---
def search_beatport(query: str, genre: str = None, bpm_min: int = None, bpm_max: int = None) -> list:
    """Search Beatport catalog. Returns mock data if no API key."""
    api_key = st.secrets.get("BEATPORT_API_KEY", "")
    if not api_key:
        return _mock_beatport_search(query)

    # Beatport API v4 integration
    headers = {"Authorization": f"Bearer {api_key}"}
    url = "https://api.beatport.com/v4/catalog/search/"
    params = {"q": query, "type": "tracks"}
    if genre:
        params["genre"] = genre
    if bpm_min:
        params["bpm_min"] = bpm_min
    if bpm_max:
        params["bpm_max"] = bpm_max

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        if resp.status_code == 200:
            return resp.json().get("results", [])
    except Exception:
        pass
    return _mock_beatport_search(query)


def _mock_beatport_search(query: str) -> list:
    """Demo Beatport results."""
    return [
        {"title": "Oxygen Levels Low", "artist": "Colyn", "bpm": 126, "key": "Am", "genre": "Melodic House & Techno", "energy": 5, "label": "Afterlife"},
        {"title": "Trigger Your Sense", "artist": "Glowal", "bpm": 122, "key": "Cm", "genre": "Melodic House & Techno", "energy": 4, "label": "All Day I Dream"},
        {"title": "Ghost Dance", "artist": "Brunello", "bpm": 124, "key": "Dm", "genre": "Melodic House & Techno", "energy": 4, "label": "Steyoyoke"},
        {"title": "Reality", "artist": "Tim Engelhardt", "bpm": 121, "key": "Fm", "genre": "Deep House", "energy": 3, "label": "Poker Flat"},
        {"title": "Crazy", "artist": "Philip Bader", "bpm": 128, "key": "Gm", "genre": "Tech House", "energy": 5, "label": "Moon Harbour"},
        {"title": "Parallels", "artist": "Upercent", "bpm": 132, "key": "Bbm", "genre": "Melodic Techno", "energy": 5, "label": "Stil Vor Talent"},
    ]
