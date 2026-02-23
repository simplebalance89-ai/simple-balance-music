"""Tab 10: Simple Balance Dashboard — Activity, stats, calendar, recommendations."""

import streamlit as st
from datetime import datetime, timedelta


def render():
    st.markdown("### Simple Balance Dashboard")
    st.caption("Peter + Jimmy. Activity feed. Stats. The command center overview.")

    # Top metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Jimmy's Mixes", "18", "+2 this month")
    with m2:
        st.metric("Tracked Artists", "12", "+3 new")
    with m3:
        st.metric("Upcoming Shows", "3", "Next: 5 days")
    with m4:
        st.metric("Sets Built", "0", "Start building!")

    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("#### Activity Feed")

        activities = [
            {"time": "Today", "icon": "🎧", "text": "Platform launched — Simple Balance Music AI Command Center is live."},
            {"time": "Today", "icon": "🎵", "text": "18 J.A.W. mixes archived and tagged. Full catalog searchable."},
            {"time": "Today", "icon": "📡", "text": "Event radar active — tracking 12 artists across LA, Miami, Vegas."},
            {"time": "Upcoming", "icon": "🎸", "text": "MGK Lost Americana Tour — West Palm Beach, May 27, 2026. Peter + Jimmy confirmed."},
        ]

        for a in activities:
            st.markdown(f"""
{a['icon']} **{a['time']}** — {a['text']}
""")

        st.markdown("---")
        st.markdown("#### Upcoming Shows Calendar")

        shows = [
            {"date": "May 27, 2026", "event": "MGK Lost Americana Tour", "location": "West Palm Beach", "who": "Peter + Jimmy"},
        ]

        for show in shows:
            st.markdown(f"""
**{show['date']}** — {show['event']}
{show['location']} | {show['who']}
""")

        st.markdown("---")
        st.markdown("#### Sinton.ia Music Recommendations")
        st.markdown("""
Based on Peter's recent activity and mood patterns:

**This Week's Picks:**
- **Township Rebellion — New Release** — Melodic, emotional. Jimmy turned Peter onto them.
- **Glowal — Latest Mix** — The Sinton.ia origin artist. Always worth a listen.
- **Brunello — Deep Cut** — Lost In The Mellow Circus vibes. Late night material.
""")

    with col2:
        st.markdown("#### Quick Stats")

        st.markdown("**Peter's Top Genres:**")
        genres = {"Melodic House & Techno": 45, "Progressive House": 25, "Deep House": 15, "Tech House": 10, "Ambient": 5}
        for genre, pct in genres.items():
            st.progress(pct / 100, text=f"{genre} ({pct}%)")

        st.markdown("---")
        st.markdown("**Jimmy's Mix Moods:**")
        moods = {"Emotional": 4, "Driving": 3, "Dark": 2, "Deep": 3, "Chill": 2, "Euphoric": 2}
        for mood, count in moods.items():
            bar = "█" * count + "░" * (6 - count)
            st.markdown(f"`{bar}` {mood} ({count})")

        st.markdown("---")
        st.markdown("#### Platform Status")

        apis = {
            "Azure OpenAI": True,
            "Beatport": st.secrets.get("BEATPORT_API_KEY", "") != "",
            "EDMTrain": st.secrets.get("EDMTRAIN_API_KEY", "") != "",
            "Last.fm": st.secrets.get("LASTFM_API_KEY", "") != "",
            "Bandsintown": st.secrets.get("BANDSINTOWN_APP_ID", "") != "",
            "Mubert": st.secrets.get("MUBERT_API_KEY", "") != "",
            "Dolby.io": st.secrets.get("DOLBY_API_KEY", "") != "",
        }

        for api, connected in apis.items():
            status = "Connected" if connected else "Demo Mode"
            icon = "🟢" if connected else "🟡"
            st.markdown(f"{icon} **{api}:** {status}")

        st.markdown("---")
        st.markdown("#### The Brothers")
        st.markdown("""
**Peter** — Curator. Finds, pushes, speaks.
**Jimmy** — Amplifier. Takes it and makes it 5x.

*"1 person is 2."*

Simple Balance isn't just Peter + Jimmy. It's the third mind.
""")
