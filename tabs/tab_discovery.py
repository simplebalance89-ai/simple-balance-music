"""Tab 2: Music Discovery & Breaking Artists."""

import streamlit as st
from utils.ai_client import chat
from utils.apis import get_lastfm_trending, search_lastfm_artist

try:
    from utils.tidal_client import (
        is_available as tidal_available, get_session as tidal_session,
        start_login, complete_login, get_favorites, get_playlists,
        get_playlist_tracks, search_tracks as tidal_search,
    )
    HAS_TIDAL = tidal_available()
except ImportError:
    HAS_TIDAL = False

DISCOVERY_SYSTEM_PROMPT = """You are Peter's music discovery assistant — Simple Balance. You find songs based on mood, meaning, and connection — not just genre. Music is how Peter processes. It's communication, memory, and healing — not background noise.

PETER'S MUSICAL ARC:
5:3666 (Hotel Diablo darkness) → sun to me (found the light). Peter lived this. Demons to dawn. Transformed at 46.

CORE ARTISTS & WHY:
| Artist | Why |
|--------|-----|
| MGK | Lived the same darkness-to-light journey |
| Twenty One Pilots | Emotional depth for empaths |
| Blue October | Wrote the Wilson brothers' story |
| Papa Roach | The rage years, losing mom |
| Hozier | Soul music for empaths |
| Mike Posner | Raw honesty, no mask |
| Labrinth | Euphoria soundtrack, cinematic soul |
| MARINA | Theatrical transformation, butterfly |
| Shaboozey | Peter's country guy, countryside soul |
| Colyn | Afterlife label, Encore Vegas set |
| Upercent | Valencia, avant-garde, dark controlled chaos |
| Township Rebellion | Melodic, emotional |
| Glowal | The Sinton.ia origin artist |

KEY RELATIONSHIPS IN MUSIC:
- For Jimmy (brother): Twenty One Pilots - "My Blood"
- For Gladys (wife): MGK - "sun to me" (she's his light)
- For Mom (Phantasma playlist): Fleetwood Mac, Meat Loaf, Stevie Nicks
- For Gian Lucca (son): SAINt JHN - "The Best Part of Life"

MOOD MATCHING:
| Mood | Direction |
|------|-----------|
| Need to release | 070 Shake, dark builds, cathartic |
| Need to land | Sampha, intimate, just keys and soul |
| Missing mom | Phantasma playlist — Fleetwood Mac, Meat Loaf |
| Brotherhood | My Blood, For My Brother, Blood Brothers |
| Gratitude/light | sun to me, Be As You Are |
| Working/focus | Melodic house, progressive |
| Decompress | Nightly ritual sequence |

NIGHTLY DECOMPRESS SEQUENCE:
1. Release: 070 Shake - Guilty Conscience
2. Land: Sampha - No One Knows Me Like the Piano
3. Mom: Phantasma track (rotate)
4. Brothers: My Blood or For My Brother
5. Close: Mike Posner - Be As You Are

BREAKING ARTIST CRITERIA:
- Under 50K monthly listeners but growing fast (>200% in 3 months)
- Unique sound or blending genres in a new way
- Authentic — not manufactured or trend-chasing
- Would fit Peter's arc or Jimmy's DJ sets

COMMANDS:
- "Find something for [mood]" — Match to mood
- "Something like [artist/song]" — Similar vibes
- "For the Phantasma playlist" — Mom's vibe
- "Jimmy would mix this" — DJ-friendly, mashup potential
- "Decompress mode" — Run nightly sequence
- "New artists like [X]" — Discovery mode
- "Breaking artists" — Scout emerging talent

RULES:
1. Never repeat the same song twice in a session
2. Discover NEW music — don't default to old favorites
3. Know what's current
4. The Nights = anthem for meaning, not for replay

Music is medicine. Find the right prescription."""


def render():
    st.markdown("### Music Discovery & Breaking Artists")
    st.caption("Find tracks by mood, meaning, and connection. Scout emerging talent.")

    col1, col2 = st.columns([2, 1])

    with col2:
        st.markdown("#### Trending Now")
        tag = st.selectbox("Genre Tag", ["electronic", "melodic techno", "deep house",
                                          "progressive house", "indie", "hip-hop",
                                          "alternative", "soul"], key="disc_tag")
        if st.button("Load Trending", key="disc_trend"):
            tracks = get_lastfm_trending(tag)
            for t in tracks[:10]:
                name = t.get("name", "Unknown")
                artist = t.get("artist", {})
                artist_name = artist.get("name", "Unknown") if isinstance(artist, dict) else str(artist)
                plays = int(t.get("playcount", 0))
                st.markdown(f"**{name}** — {artist_name} ({plays:,} plays)")

        st.markdown("---")
        st.markdown("#### Artist Lookup")
        artist_query = st.text_input("Artist name", key="disc_artist_q", placeholder="Search artist...")
        if st.button("Lookup", key="disc_artist_go") and artist_query:
            info = search_lastfm_artist(artist_query)
            if info:
                st.markdown(f"**{info.get('name', artist_query)}**")
                stats = info.get("stats", {})
                st.metric("Listeners", f"{int(stats.get('listeners', 0)):,}")
                st.metric("Plays", f"{int(stats.get('playcount', 0)):,}")
                tags = info.get("tags", {}).get("tag", [])
                if tags:
                    st.markdown("**Tags:** " + ", ".join(t["name"] for t in tags[:5]))
                bio = info.get("bio", {}).get("summary", "")
                if bio:
                    st.markdown(bio[:300] + "...")
            else:
                st.info("No data found. Try with Last.fm API key configured.")

        st.markdown("---")
        st.markdown("#### Quick Moods")
        moods = {
            "Need to release": "Find something dark, cathartic, building",
            "Need to land": "Find something intimate, grounding, just piano and soul",
            "Missing mom": "Find something for the Phantasma playlist",
            "Brotherhood": "Find brotherhood anthems, bonds that don't break",
            "Working/focus": "Find melodic house, progressive, focus music",
            "Decompress": "Run the nightly decompress sequence",
        }
        for mood, prompt_text in moods.items():
            if st.button(mood, key=f"mood_{mood}"):
                st.session_state["disc_auto_prompt"] = prompt_text

        # --- TIDAL CONNECT ---
        st.markdown("---")
        st.markdown("#### 🎵 Tidal Connect")
        if not HAS_TIDAL:
            st.caption("Tidal integration not available (install tidalapi)")
        else:
            session = tidal_session()
            if session:
                st.success("Connected to Tidal")
                if st.button("My Favorites", key="tidal_favs"):
                    favs = get_favorites(session, limit=20)
                    for t in favs:
                        if "error" not in t:
                            st.markdown(f"**{t['name']}** — {t['artist']}")
                        else:
                            st.error(t["error"])

                if st.button("My Playlists", key="tidal_playlists"):
                    pls = get_playlists(session)
                    for p in pls:
                        if "error" not in p:
                            if st.button(f"📋 {p['name']} ({p['num_tracks']} tracks)", key=f"tpl_{p['id']}"):
                                tracks = get_playlist_tracks(session, p["id"], limit=30)
                                for t in tracks:
                                    if "error" not in t:
                                        st.markdown(f"**{t['name']}** — {t['artist']}")

                tidal_q = st.text_input("Search Tidal", key="tidal_search_q", placeholder="Search tracks...")
                if st.button("Search", key="tidal_search_go") and tidal_q:
                    results = tidal_search(session, tidal_q, limit=15)
                    for t in results:
                        if "error" not in t:
                            dur = f"{t.get('duration_sec', 0) // 60}:{t.get('duration_sec', 0) % 60:02d}" if t.get("duration_sec") else ""
                            st.markdown(f"**{t['name']}** — {t['artist']} ({dur})")

                if st.button("Disconnect Tidal", key="tidal_disconnect"):
                    st.session_state.pop("tidal_session", None)
                    st.rerun()
            else:
                st.caption("Connect your Tidal account to pull your library.")
                if st.button("Connect Tidal", key="tidal_connect"):
                    login, future = start_login()
                    if login:
                        st.session_state["tidal_auth_url"] = login.verification_uri_complete
                        st.rerun()

                if "tidal_auth_url" in st.session_state:
                    st.markdown(f"**1.** Open this link and log in:")
                    st.code(st.session_state["tidal_auth_url"])
                    st.markdown("**2.** After logging in, click below:")
                    if st.button("I've logged in", key="tidal_verify"):
                        if complete_login():
                            st.session_state.pop("tidal_auth_url", None)
                            st.success("Connected!")
                            st.rerun()
                        else:
                            st.warning("Not yet. Finish logging in at the link above, then try again.")

    with col1:
        chat_key = "discovery_messages"
        if chat_key not in st.session_state:
            st.session_state[chat_key] = []

        for msg in st.session_state[chat_key]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if not st.session_state[chat_key]:
            with st.chat_message("assistant"):
                st.markdown("**Music Discovery** ready. Tell me your mood, and I'll find something that hits. Say **decompress mode** for the nightly ritual.")

        auto_prompt = st.session_state.pop("disc_auto_prompt", None)
        user_input = st.chat_input("What mood are you in?", key="disc_input")
        prompt = auto_prompt or user_input

        if prompt:
            st.session_state[chat_key].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Discovering..."):
                    reply = chat(DISCOVERY_SYSTEM_PROMPT, st.session_state[chat_key])
                    st.markdown(reply)
                    st.session_state[chat_key].append({"role": "assistant", "content": reply})
